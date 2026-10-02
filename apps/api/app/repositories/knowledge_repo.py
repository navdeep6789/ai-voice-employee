from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import KnowledgeDocument, KnowledgeChunk


class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_document_by_doc_id(self, doc_id: str) -> Optional[KnowledgeDocument]:
        result = await self.db.execute(
            select(KnowledgeDocument)
            .options(selectinload(KnowledgeDocument.chunks))
            .where(KnowledgeDocument.doc_id == doc_id)
        )
        return result.scalar_one_or_none()

    async def save_document(
        self, doc_id: str, title: str, category: str, file_path: str, chunks_data: List[dict]
    ) -> KnowledgeDocument:
        # Delete existing document with same doc_id if exists (idempotent ingestion)
        existing = await self.get_document_by_doc_id(doc_id)
        if existing:
            await self.db.delete(existing)
            await self.db.flush()

        doc = KnowledgeDocument(doc_id=doc_id, title=title, category=category, file_path=file_path)
        self.db.add(doc)
        await self.db.flush()

        for chunk in chunks_data:
            k_chunk = KnowledgeChunk(
                document_id=doc.id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                metadata_json=chunk.get("metadata", {}),
                embedding_json=chunk.get("embedding", []),
            )
            self.db.add(k_chunk)

        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_all_chunks(self, category: Optional[str] = None) -> List[KnowledgeChunk]:
        query = select(KnowledgeChunk).join(KnowledgeDocument)
        if category:
            query = query.where(KnowledgeDocument.category == category)
        query = query.options(selectinload(KnowledgeChunk.document))
        result = await self.db.execute(query)
        return list(result.scalars().all())

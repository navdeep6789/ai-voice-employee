import asyncio
import os
import re
from pathlib import Path
from app.db.session import AsyncSessionLocal, sync_engine
from app.db.base import Base
from app.models import KnowledgeDocument, KnowledgeChunk
from app.repositories.knowledge_repo import KnowledgeRepository
from app.rag.chunker import MarkdownChunker
from app.rag.embedding import local_embedding_engine
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def ingest_all_documents(knowledge_dir_path: str = None):
    # Ensure tables exist
    Base.metadata.create_all(bind=sync_engine)

    if not knowledge_dir_path:
        knowledge_dir_path = settings.KNOWLEDGE_DIR

    k_dir = Path(knowledge_dir_path)
    if not k_dir.exists():
        logger.error(f"Knowledge directory does not exist: {k_dir}")
        return

    md_files = list(k_dir.glob("*.md"))
    if not md_files:
        logger.warning(f"No markdown documents found in {k_dir}")
        return

    logger.info(f"Beginning knowledge ingestion for {len(md_files)} documents from {k_dir}")

    # First read all files to build global corpus for embedding vectorizer
    all_chunks_raw = []
    file_docs = []

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8")
        doc_id = file_path.stem
        # Derive human title from H1 or filename
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = h1_match.group(1).strip() if h1_match else doc_id.replace("-", " ").title()
        category = "Services" if "service" in doc_id or "voice" in doc_id else "Company"

        metadata = {"doc_id": doc_id, "title": title, "category": category, "file_path": str(file_path)}
        chunks = MarkdownChunker.chunk_markdown(content, metadata)
        file_docs.append({
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "file_path": str(file_path),
            "chunks": chunks
        })
        for c in chunks:
            all_chunks_raw.append(c["content"])

    # Fit local embedding engine on all chunks
    local_embedding_engine.fit_corpus(all_chunks_raw)

    async with AsyncSessionLocal() as session:
        repo = KnowledgeRepository(session)
        for doc_info in file_docs:
            chunks_with_embeddings = []
            for c in doc_info["chunks"]:
                emb = local_embedding_engine.embed_query(c["content"])
                chunks_with_embeddings.append({
                    "chunk_index": c["chunk_index"],
                    "content": c["content"],
                    "metadata": c["metadata"],
                    "embedding": emb,
                })

            await repo.save_document(
                doc_id=doc_info["doc_id"],
                title=doc_info["title"],
                category=doc_info["category"],
                file_path=doc_info["file_path"],
                chunks_data=chunks_with_embeddings,
            )
            logger.info(f"Ingested doc '{doc_info['doc_id']}' with {len(chunks_with_embeddings)} chunks.")

    logger.info("Knowledge ingestion completed successfully.")


def main():
    asyncio.run(ingest_all_documents())


if __name__ == "__main__":
    main()

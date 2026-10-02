from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.knowledge_repo import KnowledgeRepository
from app.rag.chunker import MarkdownChunker
from app.rag.embedding import local_embedding_engine, EmbeddingProvider
from app.schemas.knowledge import KnowledgeChunkResult, KnowledgeSearchResponse
from app.core.logging import logger


class RAGService:
    def __init__(self, db: AsyncSession, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.embedder = embedding_provider or local_embedding_engine

    async def search(
        self, query: str, top_k: int = 3, category: Optional[str] = None, min_score: float = 0.1
    ) -> KnowledgeSearchResponse:
        chunks = await self.repo.get_all_chunks(category=category)
        if not chunks:
            return KnowledgeSearchResponse(success=True, results=[], total_found=0)

        # Prepare corpus texts and embeddings if not already in memory
        corpus_texts = [c.content for c in chunks]
        if not self.embedder.is_fitted:
            self.embedder.fit_corpus(corpus_texts)

        query_vec = self.embedder.embed_query(query)
        doc_vecs = [c.embedding_json if c.embedding_json else self.embedder.embed_query(c.content) for c in chunks]

        sim_scores = self.embedder.compute_similarity(query_vec, doc_vecs)

        scored_chunks: List[tuple] = []
        for i, score in enumerate(sim_scores):
            if score >= min_score:
                chunk = chunks[i]
                doc_title = chunk.document.title if chunk.document else "Knowledge Document"
                doc_cat = chunk.document.category if chunk.document else "General"
                scored_chunks.append((
                    score,
                    KnowledgeChunkResult(
                        document_id=chunk.document.doc_id if chunk.document else chunk.document_id,
                        document_title=doc_title,
                        category=doc_cat,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        similarity_score=round(float(score), 4),
                        metadata=chunk.metadata_json or {},
                    )
                ))

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_results = [item[1] for item in scored_chunks[:top_k]]

        logger.info(
            f"RAG search executed for query='{query[:40]}...'. Found {len(top_results)} relevant chunks.",
            extra={"tool": "search_knowledge", "top_k": top_k}
        )

        return KnowledgeSearchResponse(
            success=True,
            results=top_results,
            total_found=len(scored_chunks)
        )

    def build_context(self, search_results: List[KnowledgeChunkResult]) -> str:
        """Constructs grounded context string for the LLM prompt with clear citations."""
        if not search_results:
            return "No relevant internal documents found in approved knowledge base."

        context_parts = []
        for i, res in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}: {res.document_title} | Category: {res.category}]\n{res.content.strip()}"
            )
        return "\n\n---\n\n".join(context_parts)

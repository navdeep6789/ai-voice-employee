import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.rag.service import RAGService
from app.rag.chunker import MarkdownChunker
from app.rag.embedding import LocalHybridEmbeddingProvider
from app.repositories.knowledge_repo import KnowledgeRepository


@pytest.fixture
async def test_rag_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_rag_chunking_and_retrieval(test_rag_db):
    repo = KnowledgeRepository(test_rag_db)
    embedder = LocalHybridEmbeddingProvider()

    # Seed test documents
    doc1_content = """# AI Voice Agents
## Realtime Audio
Our AI voice receptionist answers customer calls with sub-second latency and books demo appointments.
Pricing starts at $4,500 setup plus $350 per month.
## Security Architecture
Voice streams are encrypted with zero permanent audio storage.
"""
    chunks = MarkdownChunker.chunk_markdown(doc1_content, {"doc_id": "test-voice", "title": "AI Voice Agents"})
    corpus = [c["content"] for c in chunks]
    embedder.fit_corpus(corpus)

    chunks_with_emb = []
    for c in chunks:
        chunks_with_emb.append({
            "chunk_index": c["chunk_index"],
            "content": c["content"],
            "metadata": c["metadata"],
            "embedding": embedder.embed_query(c["content"])
        })

    await repo.save_document(
        doc_id="test-voice",
        title="AI Voice Agents",
        category="Services",
        file_path="mock/path.md",
        chunks_data=chunks_with_emb
    )

    rag = RAGService(test_rag_db, embedding_provider=embedder)

    # 1. Search for appointment booking
    res = await rag.search(query="How does appointment booking work with voice agents?", top_k=2)
    assert res.success is True
    assert len(res.results) > 0
    top = res.results[0]
    assert top.document_title == "AI Voice Agents"
    assert any("appointments" in r.content for r in res.results)

    # 2. Verify citations context construction
    context = rag.build_context(res.results)
    assert "[Source 1: AI Voice Agents" in context

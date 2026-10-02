from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.rag.service import RAGService
from app.schemas.knowledge import KnowledgeSearchResponse

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    query: str = Query(..., min_length=2, description="Search query string"),
    top_k: int = Query(3, ge=1, le=10),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    rag = RAGService(db)
    return await rag.search(query=query, top_k=top_k, category=category)

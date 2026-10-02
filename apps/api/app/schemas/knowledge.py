from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class KnowledgeChunkResult(BaseModel):
    document_id: str
    document_title: str
    category: str
    chunk_index: int
    content: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    category: Optional[str] = None


class KnowledgeSearchResponse(BaseModel):
    success: bool
    results: List[KnowledgeChunkResult]
    total_found: int

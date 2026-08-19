from typing import Literal

from pydantic import BaseModel


# Models
class Citation(BaseModel):
    doc_title: str
    source: str
    content: str
    chunk_index: int
    similarity: float


class QueryFilter(BaseModel):
    """Schema for filters during RAG query and answer"""

    query: str
    k: int | None = 3


class QueryResponse(BaseModel):
    answer: str
    citations: list[str]
    status: Literal["answered", "needs_more_data"]

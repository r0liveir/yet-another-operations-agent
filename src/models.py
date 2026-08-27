from dataclasses import dataclass
from logging import Logger
from typing import Literal

from asyncpg import Pool
from pydantic import BaseModel


@dataclass
class Dependencies:
    logger: Logger
    pool: Pool
    citations: dict[str, dict]


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


class QueryAPIResponse(BaseModel):
    answer: str
    citations: dict[str, dict]
    status: Literal["answered", "needs_more_data"]

from pydantic_ai import RunContext

from knowledge_base.rag import retrieve
from models import RetrievedCitation

from .agent import Dependencies


async def search_docs(
    ctx: RunContext[Dependencies], query: str
) -> list[RetrievedCitation]:
    """Search the codebase architecture, runbooks, and incidents

    Call this tool exactly once. It returns up to three relevant chunks, each with
    a `citation_id` (for example `C0`). Use only those IDs in the final
    response's `citations` field"""
    chunks = await retrieve(
        query=query, conn=ctx.deps.pool, logger=ctx.deps.logger, limit=3
    )
    ctx.deps.docs_retrieved = True
    return [
        RetrievedCitation(citation_id=f"C{i}", **chunk.model_dump())
        for i, chunk in enumerate(chunks)
    ]

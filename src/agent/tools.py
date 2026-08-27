from pydantic_ai import RunContext
from pydantic_evals import set_eval_attribute

from knowledge_base.rag import retrieve
from models import Dependencies


async def search_docs(ctx: RunContext[Dependencies], query: str) -> dict[str, dict]:
    """Search the codebase architecture, runbooks, and incidents

    Call this tool exactly once. It returns a dict containing 3 keys and chunks,
    in the mapping 'citation_id'->chunk. Use 'citation_id' as the citation ID in
    the `citations` list."""
    chunks = await retrieve(
        query=query, conn=ctx.deps.pool, logger=ctx.deps.logger, limit=3
    )
    citations = {f"C{i}": chunk.model_dump() for i, chunk in enumerate(chunks)}

    # evaluate whether the citations have queried the correct docs
    # outside of evaluation tasks, this does nothing
    set_eval_attribute(
        "retrieved_citation_ids",
        {
            citation_id: citation["doc_id"]
            for citation_id, citation in citations.items()
        },
    )
    ctx.deps.citations = citations
    return citations

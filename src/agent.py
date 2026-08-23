import asyncio
import logging
import os
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

import asyncpg
from dotenv import load_dotenv
from pydantic_ai import Agent, Capability, RunContext, UsageLimits
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.tools import ToolDefinition

import ingestion
from models import Citation, QueryResponse

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass
class Dependencies:
    logger: Logger
    pool: asyncpg.Pool
    # this let us remove the retrieval tool once its result is in the message history
    docs_retrieved: bool = False


class RetrievedCitation(Citation):
    """A retrieved chunk with the stable ID the agent must return to callers."""

    citation_id: str


document_context = Capability[Dependencies](
    id="document-context",
    description="Documentation context for architecture, runbooks, past incidents, tickets, etc",
)

# this defines some limits for our agent.
limits = UsageLimits(request_limit=4, tool_calls_limit=4, total_tokens_limit=10000)


def prepare_search_docs(
    ctx: RunContext[Dependencies], tool_def: ToolDefinition
) -> ToolDefinition | None:
    """Offer retrieval only until the first successful result is returned."""
    return None if ctx.deps.docs_retrieved else tool_def


## tool: search docs(query: str, service?, doc_type?)
@document_context.tool(prepare=prepare_search_docs)
async def search_docs(
    ctx: RunContext[Dependencies], query: str
) -> list[RetrievedCitation]:
    """Search the codebase architecture, runbooks, and incidents

    Call this tool exactly once. It returns up to three relevant chunks, each with
    a `citation_id` (for example `C0`). Use only those IDs in the final
    response's `citations` field. After this call, the tool is unavailable and
    you must answer from the returned chunks."""
    chunks = await ingestion.retrieve(
        query=query, conn=ctx.deps.pool, logger=ctx.deps.logger, limit=3
    )
    ctx.deps.docs_retrieved = True
    return [
        RetrievedCitation(citation_id=f"C{i}", **chunk.model_dump())
        for i, chunk in enumerate(chunks)
    ]


model = GroqModel(model_name="llama-3.3-70b-versatile")

agent = Agent(
    model=model,
    deps_type=Dependencies,
    output_type=QueryResponse,
    instructions=(
        "You are an operations/SRE agent for a codebase. "
        "Use `search_docs` once to retrieve relevant documentation before answering. "
        "After the tool result, synthesize only the returned chunks; the tool is "
        "no longer available. For an answered response, `citations` must contain "
        "only the returned `citation_id` values (such as `C0`). If the retrieved "
        "chunks cannot answer the question, return status `needs_more_data` with "
        "an empty citations list."
    ),
    capabilities=[document_context],
)


async def main():
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
    logger = logging.getLogger(__name__)
    pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"), min_size=5, max_size=20
    )

    deps = Dependencies(logger=logger, pool=pool)
    result = await agent.run(
        "What is the architecture of the project?", deps=deps, usage_limits=limits
    )
    print(result.output)


if __name__ == "__main__":
    print("Now running main")
    asyncio.run(main())

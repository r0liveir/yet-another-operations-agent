import asyncio
import logging
from dataclasses import dataclass
from logging import Logger

import asyncpg
from pydantic_ai import Agent, Capability, UsageLimits
from pydantic_ai.models.groq import GroqModel

from config import settings
from models import QueryResponse


@dataclass
class Dependencies:
    logger: Logger
    pool: asyncpg.Pool
    docs_retrieved: bool = False


document_context = Capability[Dependencies](
    id="document-context",
    description="Documentation context for architecture, runbooks, past incidents, tickets, etc",
)

# this defines some limits for our agent.
limits = UsageLimits(request_limit=4, tool_calls_limit=4, total_tokens_limit=10000)


## tool: search docs(query: str, service?, doc_type?)
# @document_context.tool()

model = GroqModel(model_name=settings.groq_model)

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
    pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=5, max_size=20)

    deps = Dependencies(logger=logger, pool=pool)
    result = await agent.run(
        "What is the architecture of the project?", deps=deps, usage_limits=limits
    )
    print(result.output)


if __name__ == "__main__":
    print("Now running main")
    asyncio.run(main())

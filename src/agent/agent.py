import asyncio
import logging

import asyncpg
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.groq import GroqModel

from agent.tools import search_docs
from config import settings
from models import Dependencies, QueryResponse


class OperationsAgent:
    """Wrapper to agent"""

    def __init__(self):
        self.limits = UsageLimits(
            request_limit=4, tool_calls_limit=4, total_tokens_limit=10000
        )
        self.agent = Agent(
            model=GroqModel(model_name=settings.groq_model),
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
        )
        self.agent.tool(search_docs)

    async def run(self, query: str, deps: Dependencies) -> QueryResponse:
        result = await self.agent.run(query, deps=deps, usage_limits=self.limits)
        return result.output


async def main():
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
    logger = logging.getLogger(__name__)
    pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=5, max_size=20)

    # deps = Dependencies(logger=logger, pool=pool)
    # result = await agent.run(
    #    "What is the architecture of the project?", deps=deps, usage_limits=limits
    # )
    # print(result.output)


if __name__ == "__main__":
    print("Now running main")
    asyncio.run(main())

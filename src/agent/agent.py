from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.groq import GroqModel

from config import settings
from models import Dependencies, QueryResponse

from .tools import search_docs


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
                "an empty citations list. "
                "Keep your answer short to, at most, 2 paragraphs."
            ),
        )
        self.agent.tool(search_docs)

    async def run(self, query: str, deps: Dependencies) -> QueryResponse:
        result = await self.agent.run(query, deps=deps, usage_limits=self.limits)
        return result.output

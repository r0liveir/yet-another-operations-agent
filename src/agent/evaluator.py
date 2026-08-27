import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

import asyncpg
import logfire
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    Evaluator,
    EvaluatorContext,
    MaxToolCalls,
    ToolCorrectness,
)

from config import settings
from knowledge_base.markdown import parse_markdown_file
from models import Dependencies, QueryResponse

from .agent import OperationsAgent


@dataclass
class ScenarioExpectation:
    expected_document_ids: set[str]
    expected_status: str


@dataclass
class EvidenceEvaluator(Evaluator):
    """Check if agent gathered some evidence for a query.
    Compares with ScenarioExpectation"""

    """Check that final citations refer to expected retrieved documents."""

    def evaluate(self, ctx: EvaluatorContext[str, QueryResponse, ScenarioExpectation]):
        expected = ctx.metadata
        retrieved: dict[str, str] = ctx.attributes["retrieved_citation_ids"]

        if expected is None or not set(ctx.output.citations) <= set(retrieved):
            return False

        document_ids_retrieved = {
            retrieved[citation_id] for citation_id in ctx.output.citations
        }

        # evaluates if status match and expected is subset of retrieved
        return (
            ctx.output.status == expected.expected_status
            and expected.expected_document_ids <= document_ids_retrieved
        )


async def main():
    logfire.configure(send_to_logfire=False)
    logfire.instrument_pydantic_ai()

    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
    logger = logging.getLogger(__name__)
    pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=5, max_size=20)

    files: list[dict] = []
    operations_agent = OperationsAgent()

    scenario_dir = Path(__file__).resolve().parents[2] / "data" / "scenarios"

    for file_path in scenario_dir.glob("*.md"):
        metadata, _ = parse_markdown_file(str(file_path))
        files.append(metadata)

    cases: list[Case] = []

    for scenario in files:
        cases.append(
            Case(
                name=scenario["id"],
                inputs=scenario["question"],
                metadata=ScenarioExpectation(
                    expected_status=scenario["expected_status"],
                    expected_document_ids=set(scenario["expected_document_ids"]),
                ),
            )
        )

    dataset = Dataset(
        name="Evaluate Simple Scenarios",
        cases=cases,
        evaluators=[
            EvidenceEvaluator(),
            ToolCorrectness(expected_tools=["search_docs"]),
            MaxToolCalls(1),
        ],
    )

    # Function to evaluate, without deps.
    async def run_agent(question: str) -> QueryResponse:
        deps = Dependencies(logger=logger, pool=pool)
        return await operations_agent.run(question, deps)

    report = await dataset.evaluate(run_agent, max_concurrency=1)
    report.print(
        include_input=True,
        include_output=True,
        include_expected_output=True,
        include_total_duration=True,
    )

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())

import glob
from dataclasses import dataclass

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    Evaluator,
    EvaluatorContext,
    MaxToolCalls,
    ToolCorrectness,
)

from knowledge_base.markdown import parse_markdown_file
from models import QueryResponse


@dataclass
class ScenarioExpectation:
    expected_document_ids: set[str]
    expected_status: str


@dataclass
class EvidenceEvaluator(Evaluator):
    """Check if agent gathered some evidence for a query.
    Compares with ScenarioExpectation"""

    # EvaluatorContext[x,y,z]: x -> ctx.input, y -> ctx.output, z -> ctx.metadata
    def evaluate(self, ctx: EvaluatorContext[str, QueryResponse, ScenarioExpectation]):
        expected = ctx.metadata
        retrieved: dict[str, str] = ctx.attributes["retrieved_citation_ids"]

        document_ids_retrieved = {
            retrieved[citation_id]
            for citation_id in ctx.output.citations
            if citation_id in retrieved
        }

        # evaluates if status match and expected is subset of retrieved
        return (
            ctx.output.status == expected.expected_status
            and expected.expected_document_ids <= document_ids_retrieved
        )


def main():
    files: list[dict] = []

    for file_path in glob.glob("../../data/scenarios/*.md"):
        metadata, _ = parse_markdown_file(file_path)
        files.append(metadata)

    cases: list[Case] = []

    for scenario in files:
        cases.append(
            Case(
                name=scenario["id"],
                inputs=scenario["question"],
                metadata=ScenarioExpectation(
                    expected_status=scenario["status"],
                    expected_document_ids=scenario["expected_document_ids"],
                ),
            )
        )

    dataset = Dataset(
        name="Evaluate Simple Scenarios",
        cases=cases,
        evaluators=[
            EvidenceEvaluator(),
            ToolCorrectness(expected_tools=["search_docs"]),
            MaxToolCalls(2),
        ],
    )


if __name__ == "__main__":
    main()

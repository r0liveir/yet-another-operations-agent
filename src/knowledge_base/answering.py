"""Generate a structured answer from chunks retrieved by the RAG workflow."""

from ollama import AsyncClient

from config import settings
from models import Citation, QueryResponse

PROMPT_TEMPLATE = """
You are an assistant for question-answering tasks.
Use the supplied documents to answer the question.
For the output, citations is a list of citation IDs in strings.
Keep answers at most five sentences.
You must cite every `answered` response.
Never return `answered` with empty citations.
Use `needs_more_data` only when supplied context cannot answer question; citations must then be empty.
"""


async def query_llm(query: str, citations: dict[str, Citation]):
    """Answer a question using only its retrieved citations."""
    messages = [
        {
            "role": "system",
            "content": f"{PROMPT_TEMPLATE}\nYou may use these citations:\n{citations}",
        },
        {"role": "user", "content": query},
    ]
    return await AsyncClient().chat(
        model=settings.language_model,
        messages=messages,
        format=QueryResponse.model_json_schema(),
        think=False,
        options={"temperature": 0, "seed": 67},
    )

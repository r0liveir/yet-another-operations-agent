"""The RAG workflow: index operational documents and retrieve relevant chunks."""

import glob
import logging
from logging import Logger

import asyncpg
from ollama import AsyncClient

from config import settings
from models import Citation

from .markdown import chunk_markdown, parse_markdown_file


async def retrieve(
    query: str, conn: asyncpg.Pool, logger: Logger, limit: int = 3
) -> list[Citation]:
    """Embed a question and return its most similar indexed document chunks."""
    query_embedding = await AsyncClient().embed(model=settings.embed_model, input=query)
    embeddings = query_embedding.get("embeddings")[0]

    logger.debug("[Query done] %s", query)
    sql_query = """
    SELECT doc_id, doc_title, chunk_index, source, content,
        1 - (embedding <=> $1) AS similarity
    FROM document_chunks
    ORDER BY embedding <=> $1
    LIMIT $2
    """
    rows = await conn.fetch(sql_query, str(embeddings), limit)

    if logger.isEnabledFor(logging.DEBUG):
        for row in rows:
            logger.debug(
                "Retrieved %s (similarity: %s)", row["doc_title"], row["similarity"]
            )

    return [Citation.model_validate(dict(row)) for row in rows]


async def ingest_docs(docs_dir: str, conn: asyncpg.Pool, logger: Logger) -> None:
    """Parse, chunk, embed, and replace all Markdown documents in a directory."""
    sql_insertion_query = """
    INSERT INTO document_chunks
        (doc_id, doc_title, doc_type, service, source, content, chunk_index, embedding)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """

    for file_path in glob.glob(f"{docs_dir}/**/*.md", recursive=True):
        metadata, body = parse_markdown_file(file_path, logger)
        chunks = chunk_markdown(metadata, body)
        if not chunks:
            continue

        embeddings = await AsyncClient().embed(model=settings.embed_model, input=chunks)
        async with conn.acquire() as connection, connection.transaction():
            await connection.execute(
                "DELETE FROM document_chunks WHERE doc_id = $1", metadata.get("id")
            )
            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings.embeddings, strict=True)
            ):
                await connection.execute(
                    sql_insertion_query,
                    metadata.get("id", ""),
                    metadata.get("title", ""),
                    metadata.get("type", ""),
                    metadata.get("service", ""),
                    metadata.get("source", ""),
                    chunk,
                    index,
                    str(embedding),
                )

        logger.info("Indexed %s - %d chunks", metadata.get("title", ""), len(chunks))

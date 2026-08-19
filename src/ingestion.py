import glob
from logging import Logger

import asyncpg
import yaml
from ollama import AsyncClient

EMBED_MODEL = "nomic-embed-text"


def parse_markdown_file(file_path: str, logger: Logger) -> tuple[dict, str]:
    """Extract YAML frontmatter metadata and body content"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    metadata = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    logger.debug(f"[Markdown file parsed]: {metadata}\n{body[:100]}")

    return metadata, body


def chunk_markdown(metadata: dict, body: str, max_chars: int = 800) -> list[str]:
    """Splits markdown on paragraphs, preserving header sections
    This also uses a context prefix in the chunks, which solves the
    context loss problem in search and RAG systems"""
    paragraphs = body.split("\n\n")
    chunks, current = [], ""

    context_prefix = f"[{metadata.get('type', 'doc').upper()}: {metadata.get('title', '')} | Service: {metadata.get('service', 'general')}]\n"

    for p in paragraphs:
        # limit how much the current chunk has
        # this will split per paragraph
        if len(current) + len(p) < max_chars:
            current += "\n\n" + p if current else p
        else:
            # if passed max_chars, append the current chunk
            if current:
                chunks.append(f"{context_prefix}{current.strip()}")
            current = p

    # append the last chunk
    if current:
        chunks.append(f"{context_prefix}{current.strip()}")
    return chunks


async def retrieve(query: str, conn: asyncpg.Pool, logger: Logger, limit: int = 3):
    """Retrieval function for our document_chunks db
    This is RAG!
    """

    # create the embedding for the query, same embedding used when ingesting and inserting docs
    query_embedding = await AsyncClient().embed(model=EMBED_MODEL, input=query)
    embeddings = query_embedding.get("embeddings")[0]

    logger.debug(f"[Query done] {query}")
    logger.debug(f"[Embedding of query] {embeddings}")

    sql_query = """
    select doc_title, source, content,
        1 - (embedding <=> $1) as similarity
    from document_chunks
    order by embedding <=> $1
    limit $2
    """

    rows = await conn.fetch(sql_query, str(embeddings), limit)

    print(f"Top {limit} matches for the query:")
    for r in rows:
        print("---")
        print(f"title: {r['doc_title']}, similarity: {r['similarity']}")
        print(r["content"])
        print("---\n")


async def ingest_docs(docs_dir: str, conn: asyncpg.Connection, logger: Logger):
    """Function for ingesting docs at once
    This may be improved by using LangChain, see more at:
    https://www.datacamp.com/tutorial/pgvector-tutorial"""

    sql_insertion_query = """
    insert into document_chunks
        (doc_id, doc_title, doc_type, service, source, content, chunk_index, embedding)
    VALUES
        ($1, $2, $3, $4, $5, $6, $7, $8)
    """

    files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)

    for file_path in files:
        logger.debug(f"Now working with {file_path}")

        metadata, body = parse_markdown_file(file_path, logger)

        chunks = chunk_markdown(metadata, body)
        if not chunks:
            continue

        # generate embeddings locally, using batch
        embeddings = await AsyncClient().embed(model=EMBED_MODEL, input=chunks)

        logger.debug(f"[Chunks and embeddings parsed]: {chunks}\n{embeddings}")

        res = await conn.execute(
            "DELETE FROM document_chunks WHERE doc_id = $1", metadata.get("id")
        )

        logger.debug(f"[Chunks deleted]: {res}")

        for i in range(len(chunks)):
            await conn.execute(
                sql_insertion_query,
                metadata.get("id", ""),
                metadata.get("title", ""),
                metadata.get("type", ""),
                metadata.get("service", ""),
                metadata.get("source", ""),
                chunks[i],
                i,
                str(embeddings.embeddings[i]),
            )

        print(f"Indexed {metadata.get('title', '')} - {len(chunks)} chunks")

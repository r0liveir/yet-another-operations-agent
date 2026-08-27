import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request

from config import settings
from knowledge_base.answering import query_llm
from knowledge_base.rag import ingest_docs, retrieve
from models import QueryFilter, QueryResponse


# defines a lifespan for the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
    app.state.logger = logging.getLogger(__name__)

    app.state.docs_dir = settings.docs_dir
    app.state.pool = await asyncpg.create_pool(
        dsn=settings.database_url, min_size=5, max_size=20
    )
    yield

    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


# dependency injections
async def get_db_connection(
    request: Request,
) -> asyncpg.Pool:
    return request.app.state.pool


async def get_logger(
    request: Request,
) -> logging.Logger:
    return request.app.state.logger


async def get_docs_dir(
    request: Request,
) -> str:
    return request.app.state.docs_dir


@app.get("/")
async def root():
    return {"message": "Hello there"}


@app.post("/ingest")
async def ingest_documents(
    background_tasks: BackgroundTasks,
    db: asyncpg.Pool = Depends(get_db_connection),
    docs_dir: str = Depends(get_docs_dir),
    logger: logging.Logger = Depends(get_logger),
):
    background_tasks.add_task(ingest_docs, docs_dir, db, logger)
    return {"message": "Ingestion scheduled in the background"}


@app.post("/query")
async def query_existing_documents(
    query_payload: QueryFilter,
    db: asyncpg.Pool = Depends(get_db_connection),
    logger: logging.Logger = Depends(get_logger),
):
    chunks = await retrieve(
        query=query_payload.query, conn=db, logger=logger, limit=query_payload.k
    )

    chunks_dict = {}
    for i, c in enumerate(chunks):
        chunks_dict[f"C{i}"] = c

    response = await query_llm(query=query_payload.query, citations=chunks_dict)

    # validate model response here
    if response.message.content is None:
        raise ValueError("Ollama returned empty response")
    result = QueryResponse.model_validate_json(response.message.content)
    if result.status == "answered" and not result.citations:
        raise HTTPException(502, "Model answered without citations")

    return QueryResponse.model_validate_json(response.message.content)

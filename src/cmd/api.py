import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request

from agent.agent import OperationsAgent
from config import settings
from knowledge_base.rag import ingest_docs
from models import Dependencies, QueryAPIResponse, QueryFilter

operations_agent = OperationsAgent()


# defines a lifespan for the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    level = logging.DEBUG if settings.log_debug_mode == "DEBUG" else logging.INFO
    logging.basicConfig(level=level, filename="app.log", filemode="w")
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
async def query_agent(
    query_payload: QueryFilter,
    db: asyncpg.Pool = Depends(get_db_connection),
    logger: logging.Logger = Depends(get_logger),
) -> QueryAPIResponse:
    """Endpoint for querying Ops Agent"""

    deps = Dependencies(logger=logger, pool=db, citations={})
    result = await operations_agent.run(query=query_payload.query, deps=deps)

    response = QueryAPIResponse(
        answer=result.answer, status=result.status, citations={}
    )
    for cit in result.citations:
        if cit not in deps.citations:
            raise HTTPException(status_code=500, detail="Citation not in original dict")

        # May convert into clickable/viewable citation
        response.citations[cit] = deps.citations[cit]

    return response

import logging
import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, Request

import ingestion

load_dotenv("../.env")


# defines a lifespan for the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
    app.state.logger = logging.getLogger(__name__)

    database_url = os.getenv("DATABASE_URL")
    app.state.docs_dir = os.getenv("DOCS_DIR")
    app.state.pool = await asyncpg.create_pool(
        dsn=database_url, min_size=5, max_size=20
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
    background_tasks.add_task(ingestion.ingest_docs, docs_dir, db, logger)
    return {"message": "Ingestion started in the background"}

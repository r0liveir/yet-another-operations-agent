import argparse
import asyncio
import logging
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

import ingestion

# Initial config
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
database_url = os.getenv("DATABASE_URL")
docs_dir = os.getenv("DOCS_DIR")

pool: asyncpg.Pool = None  # type:ignore
logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")
logger = logging.getLogger(__name__)


async def init_db():
    global pool
    global database_url
    pool = await asyncpg.create_pool(dsn=database_url, min_size=5, max_size=20)


async def main():
    global logger
    await init_db()
    parser = argparse.ArgumentParser(
        prog="CLI for RAG ingestor",
        description="CLI that uses ingestion module and a query, and returns results of documents, etc",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest command
    parser_ingest = subparsers.add_parser("ingest", help="ingest the docs dir")
    parser_ingest.add_argument(
        "-d", "--dir", type=str, required=True, help="path for the dir"
    )

    # retrieve command
    parser_retrieve = subparsers.add_parser(
        "retrieve", help="retrieve from the database"
    )
    parser_retrieve.add_argument(
        "-q", "--query", type=str, required=True, help="query for the database"
    )

    parser.add_argument("--debug", action="store_true", help="enable debug log")

    args = parser.parse_args()
    if args.debug:
        logger.level = logging.DEBUG

    if args.command == "ingest":
        await ingestion.ingest_docs(docs_dir=args.dir, conn=pool, logger=logger)
    elif args.command == "retrieve":
        await ingestion.retrieve(query=args.query, conn=pool, logger=logger)


if __name__ == "__main__":
    asyncio.run(main())

import argparse
import asyncio
import logging

import ingestion


async def main():
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
        ingestion.logger.level = logging.DEBUG

    if args.command == "ingest":
        await ingestion.ingest_docs(args.dir)
    elif args.command == "retrieve":
        await ingestion.retrieve(args.query)


if __name__ == "__main__":
    asyncio.run(main())

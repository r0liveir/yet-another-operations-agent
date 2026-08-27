"""Parsing and chunking Markdown knowledge sources."""

from logging import Logger

import yaml


def parse_markdown_file(file_path: str, logger: Logger) -> tuple[dict, str]:
    """Extract YAML frontmatter metadata and body content."""
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    logger.debug("[Markdown file parsed]: %s\n%s", metadata, body[:100])
    return metadata, body


def chunk_markdown(metadata: dict, body: str, max_chars: int = 800) -> list[str]:
    """Split Markdown on paragraphs while preserving document context."""
    context_prefix = (
        f"[{metadata.get('type', 'doc').upper()}: {metadata.get('title', '')} "
        f"| Service: {metadata.get('service', 'general')}]\n"
    )
    chunks: list[str] = []
    current = ""

    for paragraph in body.split("\n\n"):
        if len(current) + len(paragraph) < max_chars:
            current += "\n\n" + paragraph if current else paragraph
        else:
            if current:
                chunks.append(f"{context_prefix}{current.strip()}")
            current = paragraph

    if current:
        chunks.append(f"{context_prefix}{current.strip()}")
    return chunks

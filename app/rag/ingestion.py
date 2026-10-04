"""Document ingestion, frontmatter parsing, cleaning, and chunking pipeline."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown file if present.

    Returns:
        tuple of (metadata_dict, body_text)
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, raw_text, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        body = match.group(2)
        try:
            metadata = yaml.safe_load(yaml_content) or {}
        except Exception:
            metadata = {}
        return metadata, body
    return {}, raw_text


def clean_text(text: str) -> str:
    """Normalize whitespace, convert CRLF to LF, and strip excessive blank lines."""
    text = text.replace("\r\n", "\n")
    # Replace 3 or more newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_document(file_path: str | Path) -> dict[str, Any]:
    """Load a single markdown document, extracting metadata and content."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found at: {file_path}")

    raw_text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(raw_text)
    cleaned_body = clean_text(body)

    # Derive document title from first Markdown header #
    title_match = re.search(r"^#\s+(.+)$", cleaned_body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    doc_id = str(metadata.get("document_id") or path.stem).strip()
    tags = metadata.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    return {
        "document_id": doc_id,
        "title": title,
        "document_type": str(metadata.get("document_type", "General")),
        "module": str(metadata.get("module", "General")),
        "priority": str(metadata.get("priority", "Medium")),
        "status": str(metadata.get("status", "Active")),
        "tags": tags,
        "tags_str": ", ".join(tags),
        "content": cleaned_body,
        "file_path": str(path.as_posix()),
        "raw_metadata": metadata,
    }


def chunk_document(doc: dict[str, Any], max_chunk_words: int = 250) -> list[dict[str, Any]]:
    """Split a document into logical, section-aware chunks.

    Splits by Markdown '## ' section headers first to preserve semantic cohesion.
    If a section exceeds max_chunk_words, it further splits by paragraphs.
    """
    content = doc["content"]
    document_id = doc["document_id"]

    # Split by section headers (## ) while keeping the header text
    sections = re.split(r"(?=\n##\s+)", "\n" + content)
    chunks: list[dict[str, Any]] = []
    chunk_index = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        words = section.split()
        if len(words) <= max_chunk_words:
            # Fits neatly in one chunk
            header_match = re.search(r"^##\s+(.+)$", section, re.MULTILINE)
            section_title = header_match.group(1).strip() if header_match else doc["title"]

            chunk_id = f"{document_id}_c{chunk_index}"
            chunks.append({
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "document_id": document_id,
                "title": f"{doc['title']} - {section_title}" if section_title != doc["title"] else doc["title"],
                "document_type": doc["document_type"],
                "module": doc["module"],
                "priority": doc["priority"],
                "status": doc["status"],
                "tags": doc["tags"],
                "tags_str": doc["tags_str"],
                "file_path": doc["file_path"],
                "text": section,
            })
            chunk_index += 1
        else:
            # Split section further by double newlines (paragraphs)
            paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
            current_batch: list[str] = []
            current_count = 0

            for para in paragraphs:
                para_words = len(para.split())
                if current_count + para_words > max_chunk_words and current_batch:
                    chunk_text = "\n\n".join(current_batch)
                    chunk_id = f"{document_id}_c{chunk_index}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_index,
                        "document_id": document_id,
                        "title": doc["title"],
                        "document_type": doc["document_type"],
                        "module": doc["module"],
                        "priority": doc["priority"],
                        "status": doc["status"],
                        "tags": doc["tags"],
                        "tags_str": doc["tags_str"],
                        "file_path": doc["file_path"],
                        "text": chunk_text,
                    })
                    chunk_index += 1
                    current_batch = [para]
                    current_count = para_words
                else:
                    current_batch.append(para)
                    current_count += para_words

            if current_batch:
                chunk_text = "\n\n".join(current_batch)
                chunk_id = f"{document_id}_c{chunk_index}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                    "document_id": document_id,
                    "title": doc["title"],
                    "document_type": doc["document_type"],
                    "module": doc["module"],
                    "priority": doc["priority"],
                    "status": doc["status"],
                    "tags": doc["tags"],
                    "tags_str": doc["tags_str"],
                    "file_path": doc["file_path"],
                    "text": chunk_text,
                })
                chunk_index += 1

    # Fallback if no sections were parsed
    if not chunks:
        chunks.append({
            "chunk_id": f"{document_id}_c0",
            "chunk_index": 0,
            "document_id": document_id,
            "title": doc["title"],
            "document_type": doc["document_type"],
            "module": doc["module"],
            "priority": doc["priority"],
            "status": doc["status"],
            "tags": doc["tags"],
            "tags_str": doc["tags_str"],
            "file_path": doc["file_path"],
            "text": content,
        })

    return chunks


def load_all_documents(data_dir: str | Path = "data") -> list[dict[str, Any]]:
    """Scan and load all markdown documents from data directories."""
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    documents: list[dict[str, Any]] = []
    # Sort for deterministic loading order
    for md_file in sorted(data_path.rglob("*.md")):
        doc = load_document(md_file)
        documents.append(doc)

    return documents

# Source‑reference utilities for Phase 6 – Grounded LLM response
"""Utility functions that extract and validate source identifiers from the
retrieved chunks passed to the LLM client.

Each chunk is expected to be a dictionary with a ``metadata`` field that (at a
minimum) contains a ``doc_id`` string.  The helper returns a *deduplicated* list
preserving the order in which the chunks appear.

If a chunk lacks a valid ``doc_id`` it is ignored – this prevents the LLM from
being given fabricated references.
"""

from __future__ import annotations

from typing import List, Dict, Any


def extract_source_ids(chunks: List[Dict[str, Any]]) -> List[str]:
    """Return an ordered list of unique document IDs from ``chunks``.

    The function walks the chunks in their original order, reads ``metadata['doc_id']``
    (if present and non‑empty), and adds it to the result list only once.
    Duplicate IDs are skipped, and any malformed or missing ``doc_id`` entries are
    silently ignored.
    """
    seen: set[str] = set()
    sources: List[str] = []
    for chunk in chunks:
        # Support both flat {"doc_id": ...} chunks and nested {"metadata": {"doc_id": ...}} chunks.
        metadata = chunk.get("metadata", {}) or {}
        doc_id = metadata.get("doc_id") or chunk.get("doc_id")
        if not isinstance(doc_id, str) or not doc_id:
            continue
        if doc_id not in seen:
            seen.add(doc_id)
            sources.append(doc_id)
    return sources

__all__ = ["extract_source_ids"]


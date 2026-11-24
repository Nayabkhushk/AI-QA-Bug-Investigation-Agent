# Prompt construction utilities for Phase 6 – Grounded LLM response
"""Utilities that turn a bug report and a list of retrieved chunks into the
user‑visible part of the Gemini request.

The system instruction (role definition, grounding rules, fallback text) lives
in :pymod:`app.agent.prompts`.  This module only builds the *contents* that are
passed as ``contents`` to ``generate_content``.

The format mirrors the historic helper ``_build_prompt`` but is clearer and
easier to test.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _format_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Return a numbered, readable representation of ``chunks``.

    Each chunk is expected to contain:
    - ``content`` – the text of the knowledge‑base fragment.
    - ``metadata`` – a mapping that includes at least ``doc_id`` and optionally
      ``source``.

    The function produces something like::

        Chunk 1 (REQ‑001): <content>
        Chunk 2 (API‑DOC‑A): <content>

    Duplicated ``doc_id`` values are **not** collapsed here – the caller decides
    which chunks to keep.  Empty or malformed chunks are skipped safely.
    """
    lines: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        content = chunk.get("content", "").strip()
        if not content:
            continue  # skip empty chunks silently
        metadata = chunk.get("metadata", {}) or {}
        doc_id = metadata.get("doc_id", "UNKNOWN")
        source = metadata.get("source")
        label = f"{doc_id}" if source is None else f"{doc_id} ({source})"
        lines.append(f"Chunk {idx} [{label}]:\n{content}\n")
    return "\n".join(lines)


def build_investigation_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    """Assemble the full prompt sent to Gemini for a bug investigation.

    Parameters
    ----------
    query:
        The raw bug report supplied by the user.
    chunks:
        A list of retrieved, *reranked* knowledge‑base fragments.  The function
        will format them via :func:`_format_chunks`.

    Returns
    -------
    str
        The concatenated prompt.  If ``chunks`` is empty the function returns an
        empty string – the caller (`GeminiLLMClient.generate_investigation`) will
        fall back to the ``INSUFFICIENT_EVIDENCE_FALLBACK`` response.
    """
    query_part = f"REPORTED BUG QUERY:\n{query.strip()}\n\n"
    if not chunks:
        # No context – the client handles this case.
        return query_part
    context_part = (
        "RETRIEVED AND VALIDATED KNOWLEDGE‑BASE CONTEXT:\n"
        + _format_chunks(chunks)
    )
    return query_part + context_part + "\n"

# The module exports only the public helpers; ``_format_chunks`` is kept private
# but is useful for unit‑testing the formatting logic.

__all__ = ["build_investigation_prompt", "_format_chunks"]


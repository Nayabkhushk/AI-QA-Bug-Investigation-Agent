"""FAISS Vector Store — local, persistent, no internet required.

Index + metadata are saved to `faiss_index/` by `ingest.py`.
This module loads them at startup so there is no re-embedding cost.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------------
# Embedding model (downloaded once by HuggingFace Hub, then cached locally)
# ---------------------------------------------------------------------------
_MODEL_NAME = "all-MiniLM-L6-v2"  # 22 MB, CPU-fast, 100 % free


class FAISSVectorStore:
    """Load and query a pre-built FAISS index from disk.

    The index is built once by ``ingest.py``.  This class is read-only
    at query time — no writes, no network calls.
    """

    def __init__(self, index_dir: str = "./faiss_index"):
        self.index_dir = Path(index_dir)
        self.model = SentenceTransformer(_MODEL_NAME)

        index_path = self.index_dir / "index.faiss"
        meta_path = self.index_dir / "metadata.json"

        if not index_path.exists() or not meta_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at '{index_dir}'.\n"
                "Run  python ingest.py  first to build the index."
            )

        self.index: faiss.Index = faiss.read_index(str(index_path))
        with open(meta_path, encoding="utf-8") as f:
            self.metadata: list[dict[str, Any]] = json.load(f)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def similarity_search(
        self,
        query: str,
        top_k: int = 10,
        module: str | None = None,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Dense cosine similarity search with optional metadata pre-filters.

        Returns:
            Ranked list of matching chunk dicts, each including a ``score``
            (0–1, higher is better).
        """
        # Pre-filter metadata indices so FAISS only scores relevant chunks
        candidate_indices = self._filter_indices(module, document_type)

        if not candidate_indices:
            return []

        # Build a temporary sub-index from the filtered subset if we're
        # filtering, otherwise search the full index directly.
        if len(candidate_indices) < self.index.ntotal:
            vectors = np.array(
                [self.index.reconstruct(int(i)) for i in candidate_indices],
                dtype="float32",
            )
            sub_index = faiss.IndexFlatIP(vectors.shape[1])
            sub_index.add(vectors)
            query_vec = self._embed(query)
            distances, local_ids = sub_index.search(query_vec, min(top_k, len(candidate_indices)))
            # Map local IDs back to original metadata positions
            global_ids = [candidate_indices[lid] for lid in local_ids[0] if lid >= 0]
            scores = distances[0]
        else:
            query_vec = self._embed(query)
            distances, ids = self.index.search(query_vec, top_k)
            global_ids = [i for i in ids[0] if i >= 0]
            scores = distances[0]

        results: list[dict[str, Any]] = []
        for rank, (gid, score) in enumerate(zip(global_ids, scores)):
            meta = self.metadata[gid]
            results.append({
                **meta,
                "score": round(float(score), 4),
            })

        return results

    def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Reassemble a full document by collecting and ordering all its chunks."""
        chunks = [m for m in self.metadata if m.get("document_id") == document_id]
        if not chunks:
            return None

        chunks.sort(key=lambda c: c.get("chunk_index", 0))
        full_content = "\n\n".join(c.get("text", "") for c in chunks)
        first = chunks[0]

        return {
            "document_id": document_id,
            "title": first.get("title", document_id),
            "document_type": first.get("document_type", "General"),
            "module": first.get("module", "General"),
            "priority": first.get("priority", "Medium"),
            "status": first.get("status", "Active"),
            "tags": first.get("tags", []),
            "tags_str": first.get("tags_str", ""),
            "file_path": first.get("file_path", ""),
            "total_chunks": len(chunks),
            "content": full_content,
        }

    def count(self) -> int:
        """Return total number of indexed chunks."""
        return len(self.metadata)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _embed(self, text: str) -> np.ndarray:
        vec = self.model.encode([text], normalize_embeddings=True)
        return vec.astype("float32")

    def _filter_indices(
        self,
        module: str | None,
        document_type: str | None,
    ) -> list[int]:
        """Return metadata indices that pass the optional filters."""
        indices = []
        for i, meta in enumerate(self.metadata):
            if module and module != "All" and meta.get("module") != module:
                continue
            if document_type and document_type != "All" and meta.get("document_type") != document_type:
                continue
            indices.append(i)
        return indices

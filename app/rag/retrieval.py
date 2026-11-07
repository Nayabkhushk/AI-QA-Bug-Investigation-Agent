"""Hybrid Retrieval module — Dense FAISS + Sparse BM25 + Metadata Filtering.

Combines semantic understanding (FAISS) with exact keyword/code matching (BM25)
using Reciprocal Rank Fusion (RRF) to retrieve the most relevant evidence chunks.
"""

from __future__ import annotations

import copy
import hashlib
import math
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from app.rag.vector_store import FAISSVectorStore


# ---------------------------------------------------------------------------
# Tokenizer tailored for Software QA & Bug Analysis
# ---------------------------------------------------------------------------
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*")


def tokenize_code_and_text(text: str) -> list[str]:
    """Tokenize technical text while preserving compound identifiers.

    Keeps terms like: 'BUG-102', 'AUTH-REQ-002', 'token_version', 'HTTP_401'.
    Converts to lowercase for case-insensitive matching.
    """
    if not text:
        return []
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]


# ---------------------------------------------------------------------------
# Okapi BM25 Implementation (Zero external dependency bloat)
# ---------------------------------------------------------------------------
class BM25Index:
    """In-memory Okapi BM25 index built over document chunks."""

    def __init__(
        self,
        corpus: list[dict[str, Any]],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_len: list[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: dict[str, int] = Counter()
        self.term_freqs: list[dict[str, int]] = []
        self.idf: dict[str, float] = {}

        self._build_index()

    def _build_index(self) -> None:
        """Tokenize all chunks and compute BM25 statistics."""
        total_len = 0
        n_docs = len(self.corpus)

        for doc in self.corpus:
            # Index chunk text plus title, module, and tags for high-precision retrieval
            combined_text = f"{doc.get('title', '')} {doc.get('tags_str', '')} {doc.get('text', '')}"
            tokens = tokenize_code_and_text(combined_text)
            length = len(tokens)
            self.doc_len.append(length)
            total_len += length

            tf = Counter(tokens)
            self.term_freqs.append(dict(tf))
            for term in tf.keys():
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_doc_len = total_len / n_docs if n_docs > 0 else 0.0

        # Compute Robertson-Spärck Jones IDF with floor of 0
        for term, freq in self.doc_freqs.items():
            idf_val = math.log(1.0 + (n_docs - freq + 0.5) / (freq + 0.5))
            self.idf[term] = max(0.0, idf_val)

    def search(
        self,
        query: str,
        top_k: int = 10,
        module: str | None = None,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Score and rank chunks using BM25 with optional metadata pre-filtering."""
        query_tokens = tokenize_code_and_text(query)
        if not query_tokens:
            return []

        scores: list[tuple[int, float]] = []

        for idx, doc in enumerate(self.corpus):
            # Apply metadata filters
            if module and module != "All" and doc.get("module") != module:
                continue
            if document_type and document_type != "All" and doc.get("document_type") != document_type:
                continue

            doc_tf = self.term_freqs[idx]
            doc_len = self.doc_len[idx]

            score = 0.0
            for term in query_tokens:
                if term not in doc_tf:
                    continue
                tf = doc_tf[term]
                idf = self.idf.get(term, 0.0)
                # BM25 tf saturation formula
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += idf * ((tf * (self.k1 + 1.0)) / denom)

            if score > 0.0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:top_k]

        results = []
        for rank, (idx, score) in enumerate(top_scores, start=1):
            meta = dict(self.corpus[idx])
            meta["bm25_score"] = round(float(score), 4)
            meta["bm25_rank"] = rank
            results.append(meta)

        return results


# ---------------------------------------------------------------------------
# Query/Result Cache with TTL and Index-Change Invalidation
# ---------------------------------------------------------------------------
class RetrievalCache:
    """Simple in-memory cache for retrieval results.

    Cached entries expire after ``ttl_seconds``.  The entire cache is
    automatically invalidated when the FAISS index file on disk is
    modified (detected via file modification time), ensuring stale
    results are never served after a knowledge-base rebuild.
    """

    def __init__(
        self,
        max_size: int = 100,
        ttl_seconds: float = 300.0,
        index_dir: str = "./faiss_index",
    ):
        self._store: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._index_path = Path(index_dir) / "index.faiss"
        self._index_mtime: float = self._get_index_mtime()

    # -- public API ----------------------------------------------------------

    def get(
        self,
        query: str,
        top_k: int,
        module: str | None,
        document_type: str | None,
        alpha: float,
    ) -> list[dict[str, Any]] | None:
        """Return cached results or ``None`` on miss / expiry / invalidation."""
        # Invalidate entire cache if the index file changed on disk
        current_mtime = self._get_index_mtime()
        if current_mtime != self._index_mtime:
            self.clear()
            self._index_mtime = current_mtime
            return None

        key = self._make_key(query, top_k, module, document_type, alpha)
        if key not in self._store:
            return None

        timestamp, results = self._store[key]
        if time.time() - timestamp > self._ttl:
            del self._store[key]
            return None

        # Return a deep copy so callers cannot mutate cached data
        return copy.deepcopy(results)

    def put(
        self,
        query: str,
        top_k: int,
        module: str | None,
        document_type: str | None,
        alpha: float,
        results: list[dict[str, Any]],
    ) -> None:
        """Store results in the cache (deep-copied to prevent mutation)."""
        if len(self._store) >= self._max_size:
            # Evict the oldest entry
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest_key]

        key = self._make_key(query, top_k, module, document_type, alpha)
        self._store[key] = (time.time(), copy.deepcopy(results))

    def clear(self) -> None:
        """Remove all cached entries."""
        self._store.clear()

    def size(self) -> int:
        """Return the number of cached entries."""
        return len(self._store)

    # -- private helpers -----------------------------------------------------

    def _get_index_mtime(self) -> float:
        """Return the FAISS index file's modification time, or 0 if missing."""
        if self._index_path.exists():
            return self._index_path.stat().st_mtime
        return 0.0

    def _make_key(
        self,
        query: str,
        top_k: int,
        module: str | None,
        document_type: str | None,
        alpha: float,
    ) -> str:
        """Deterministic hash key from all query parameters."""
        raw = f"{query}|{top_k}|{module}|{document_type}|{alpha}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Hybrid Retriever (Dense FAISS + Sparse BM25 + Reciprocal Rank Fusion)
# ---------------------------------------------------------------------------
class HybridRetriever:
    """Hybrid Retriever combining dense FAISS search and sparse BM25 search.

    Uses Reciprocal Rank Fusion (RRF) to merge rankings:
        RRF_score(d) = (alpha / (k + dense_rank)) + ((1 - alpha) / (k + sparse_rank))
    """

    def __init__(
        self,
        vector_store: FAISSVectorStore | None = None,
        index_dir: str = "./faiss_index",
        rrf_k: int = 60,
        cache_max_size: int = 100,
        cache_ttl_seconds: float = 300.0,
    ):
        self.vector_store = vector_store or FAISSVectorStore(index_dir=index_dir)
        self.bm25 = BM25Index(corpus=self.vector_store.metadata)
        self.rrf_k = rrf_k
        self._cache = RetrievalCache(
            max_size=cache_max_size,
            ttl_seconds=cache_ttl_seconds,
            index_dir=index_dir,
        )
        self.last_retrieval_metrics: dict[str, Any] = {}

    def dense_search(
        self,
        query: str,
        top_k: int = 10,
        module: str | None = None,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform dense semantic similarity search via FAISS."""
        results = self.vector_store.similarity_search(
            query=query,
            top_k=top_k,
            module=module,
            document_type=document_type,
        )
        for rank, res in enumerate(results, start=1):
            res["dense_rank"] = rank
        return results

    def sparse_search(
        self,
        query: str,
        top_k: int = 10,
        module: str | None = None,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform sparse keyword search via BM25."""
        return self.bm25.search(
            query=query,
            top_k=top_k,
            module=module,
            document_type=document_type,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        module: str | None = None,
        document_type: str | None = None,
        alpha: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Retrieve top_k chunks using hybrid dense + sparse search with RRF.

        Args:
            query: The search query (e.g. bug description or error code)
            top_k: Number of final results to return
            module: Optional filter (e.g. 'Authentication', 'Billing')
            document_type: Optional filter (e.g. 'BugReport', 'Requirement')
            alpha: Weight for dense vs. sparse (0.5 = equal balance)

        Returns:
            Ranked list of merged chunk dictionaries with 'hybrid_score',
            'dense_rank', and 'bm25_rank'.

        Side effect:
            Updates ``self.last_retrieval_metrics`` with latency measurements,
            cache hit status, and result count.
        """
        # Guard clause for empty query
        if not query or not query.strip():
            self.last_retrieval_metrics = {
                "dense_latency_ms": 0.0,
                "sparse_latency_ms": 0.0,
                "total_latency_ms": 0.0,
                "cache_hit": False,
                "result_count": 0,
            }
            return []

        # ---- Check cache first ------------------------------------------------
        cached = self._cache.get(query, top_k, module, document_type, alpha)
        if cached is not None:
            self.last_retrieval_metrics = {
                "dense_latency_ms": 0.0,
                "sparse_latency_ms": 0.0,
                "total_latency_ms": 0.0,
                "cache_hit": True,
                "result_count": len(cached),
            }
            return cached

        # ---- Timed retrieval --------------------------------------------------
        total_start = time.perf_counter()

        candidate_k = max(top_k * 2, 20)

        dense_start = time.perf_counter()
        dense_results = self.dense_search(
            query=query,
            top_k=candidate_k,
            module=module,
            document_type=document_type,
        )
        dense_ms = (time.perf_counter() - dense_start) * 1000

        sparse_start = time.perf_counter()
        sparse_results = self.sparse_search(
            query=query,
            top_k=candidate_k,
            module=module,
            document_type=document_type,
        )
        sparse_ms = (time.perf_counter() - sparse_start) * 1000

        # Merge candidate pools with Reciprocal Rank Fusion
        merged_scores: dict[str, float] = {}
        chunk_data: dict[str, dict[str, Any]] = {}

        for rank, item in enumerate(dense_results, start=1):
            cid = item["chunk_id"]
            rrf = alpha / (self.rrf_k + rank)
            merged_scores[cid] = merged_scores.get(cid, 0.0) + rrf
            chunk_data[cid] = item

        for rank, item in enumerate(sparse_results, start=1):
            cid = item["chunk_id"]
            rrf = (1.0 - alpha) / (self.rrf_k + rank)
            merged_scores[cid] = merged_scores.get(cid, 0.0) + rrf
            if cid in chunk_data:
                chunk_data[cid]["bm25_score"] = item.get("bm25_score")
                chunk_data[cid]["bm25_rank"] = rank
            else:
                chunk_data[cid] = item

        # Sort by merged RRF score
        ranked_chunk_ids = sorted(
            merged_scores.keys(),
            key=lambda cid: merged_scores[cid],
            reverse=True,
        )

        final_results: list[dict[str, Any]] = []
        for rank, cid in enumerate(ranked_chunk_ids[:top_k], start=1):
            chunk = chunk_data[cid]
            chunk["hybrid_score"] = round(merged_scores[cid], 6)
            chunk["hybrid_rank"] = rank
            final_results.append(chunk)

        total_ms = (time.perf_counter() - total_start) * 1000

        # ---- Store in cache ---------------------------------------------------
        self._cache.put(query, top_k, module, document_type, alpha, final_results)

        # ---- Record retrieval metrics -----------------------------------------
        self.last_retrieval_metrics = {
            "dense_latency_ms": round(dense_ms, 2),
            "sparse_latency_ms": round(sparse_ms, 2),
            "total_latency_ms": round(total_ms, 2),
            "cache_hit": False,
            "result_count": len(final_results),
        }

        return final_results

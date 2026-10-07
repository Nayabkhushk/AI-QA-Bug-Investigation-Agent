"""Hybrid Retrieval module — Dense FAISS + Sparse BM25 + Metadata Filtering.

Combines semantic understanding (FAISS) with exact keyword/code matching (BM25)
using Reciprocal Rank Fusion (RRF) to retrieve the most relevant evidence chunks.
"""

from __future__ import annotations

import math
import re
from collections import Counter
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
    ):
        self.vector_store = vector_store or FAISSVectorStore(index_dir=index_dir)
        self.bm25 = BM25Index(corpus=self.vector_store.metadata)
        self.rrf_k = rrf_k

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
        """
        # Guard clause for empty query
        if not query or not query.strip():
            return []
        # Fetch candidate pools from both retrievers        
        candidate_k = max(top_k * 2, 20)
        dense_results = self.dense_search(
            query=query,
            top_k=candidate_k,
            module=module,
            document_type=document_type,
        )
        sparse_results = self.sparse_search(
            query=query,
            top_k=candidate_k,
            module=module,
            document_type=document_type,
        )

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

        return final_results

"""Reranker module using Cross-Encoder for deep contextual relevance scoring.

Takes candidate chunks retrieved by HybridRetriever and rescores them
jointly with the user query using a cross-encoder model.
"""

from __future__ import annotations

import time
from typing import Any
from sentence_transformers import CrossEncoder

# Free, fast, high-accuracy model for cross-encoder reranking on CPU (~80 MB)
DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class DocumentReranker:
    """Reranks candidate document chunks using a Cross-Encoder model.

    Unlike bi-encoders (which encode query and document independently),
    a cross-encoder performs joint self-attention over the query and chunk
    simultaneously, yielding significantly more accurate relevance ranking.
    """

    def __init__(self, model_name: str = DEFAULT_RERANKER_MODEL):
        self.model_name = model_name
        self.model = CrossEncoder(model_name)
        self.last_rerank_metrics: dict[str, Any] = {}

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 5,
        min_score: float | None = None,
        max_chunks_per_doc: int | None = 2,
    ) -> list[dict[str, Any]]:
        """Rerank retrieved chunks according to contextual relevance to the query.

        Args:
            query: The user bug description or search question.
            documents: List of chunk dictionaries (output of HybridRetriever).
            top_k: Maximum number of reranked documents to return.
            min_score: Optional minimum cross-encoder score cutoff.
            max_chunks_per_doc: Maximum number of chunks allowed from the same
                document_id to prevent context monopolization. Default is 2.
                Set to None to allow unlimited chunks per document.

        Returns:
            List of reranked chunk dictionaries, sorted by 'rerank_score' descending,
            with 'rerank_rank' and source metadata intact.
        """
        # Guard clause for empty inputs
        if not query or not query.strip() or not documents:
            self.last_rerank_metrics = {
                "rerank_latency_ms": 0.0,
                "input_count": len(documents) if documents else 0,
                "output_count": 0,
            }
            return []

        start_time = time.perf_counter()

        # Build (query, document_text) pairs for the cross-encoder
        # Prepend title and module for additional semantic context
        pairs = []
        for doc in documents:
            doc_context = f"{doc.get('title', '')} | {doc.get('text', '')}"
            pairs.append([query, doc_context])

        # Predict cross-encoder relevance scores
        scores = self.model.predict(pairs)

        # Attach scores while preserving all original metadata and hybrid scores
        scored_docs: list[dict[str, Any]] = []
        for doc, score in zip(documents, scores):
            doc_copy = dict(doc)
            doc_copy["rerank_score"] = round(float(score), 6)
            scored_docs.append(doc_copy)

        # Sort descending by cross-encoder score
        scored_docs.sort(key=lambda d: d["rerank_score"], reverse=True)

        # Optional threshold filtering to reject completely irrelevant chunks
        if min_score is not None:
            scored_docs = [d for d in scored_docs if d["rerank_score"] >= min_score]

        # Apply diversity filter (max_chunks_per_doc) to avoid single-doc dominance
        if max_chunks_per_doc is not None and max_chunks_per_doc > 0:
            doc_counts: dict[str, int] = {}
            diverse_docs: list[dict[str, Any]] = []
            for doc in scored_docs:
                doc_id = doc.get("document_id", "")
                count = doc_counts.get(doc_id, 0)
                if count < max_chunks_per_doc:
                    diverse_docs.append(doc)
                    doc_counts[doc_id] = count + 1
            scored_docs = diverse_docs

        # Select top-k and assign new final rank
        final_results = scored_docs[:top_k]
        for rank, doc in enumerate(final_results, start=1):
            doc["rerank_rank"] = rank

        latency_ms = (time.perf_counter() - start_time) * 1000

        self.last_rerank_metrics = {
            "rerank_latency_ms": round(latency_ms, 2),
            "input_count": len(documents),
            "output_count": len(final_results),
            "top_score": final_results[0]["rerank_score"] if final_results else None,
        }

        return final_results


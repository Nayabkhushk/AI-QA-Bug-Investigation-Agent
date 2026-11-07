"""Demonstration script: Before vs After Cross-Encoder Reranking."""

import sys
from pathlib import Path

# Ensure project root is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.retrieval import HybridRetriever
from app.rag.reranker import DocumentReranker


def main():
    query = "Login fails after password reset for some users"
    print("=" * 80)
    print("  AI QA & Bug Investigation Agent — PHASE 5: RERANKING DEMO")
    print("=" * 80)
    print(f"\nQuery: '{query}'\n")

    # 1. Hybrid Retrieval (Initial Candidate Fetch)
    print("[1/2] Running Hybrid Retrieval (FAISS Dense + BM25 Sparse)...")
    retriever = HybridRetriever()
    hybrid_candidates = retriever.retrieve(query=query, top_k=10)

    print("-" * 80)
    print("--- [BEFORE RERANKING: HYBRID RETRIEVAL CANDIDATES] ---")
    print(f"{'Rank':<6} | {'Hybrid Score':<14} | {'Doc ID':<14} | {'Title'}")
    print("-" * 80)
    for i, doc in enumerate(hybrid_candidates[:5], start=1):
        score = f"{doc.get('hybrid_score', 0.0):.6f}"
        doc_id = doc.get("document_id", "N/A")
        title = doc.get("title", "")
        if len(title) > 38:
            title = title[:35] + "..."
        print(f"{i:<6} | {score:<14} | {doc_id:<14} | {title}")

    # 2. Cross-Encoder Reranking
    print("\n[2/2] Running Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)...")
    reranker = DocumentReranker()
    reranked_results = reranker.rerank(query=query, documents=hybrid_candidates, top_k=5)

    print("-" * 80)
    print("--- [AFTER RERANKING: CROSS-ENCODER RESCORED & REORDERED] ---")
    print(f"{'Rank':<6} | {'Rerank Score':<14} | {'Doc ID':<14} | {'Title'}")
    print("-" * 80)
    for i, doc in enumerate(reranked_results, start=1):
        score = f"{doc.get('rerank_score', 0.0):+.4f}"
        doc_id = doc.get("document_id", "N/A")
        title = doc.get("title", "")
        if len(title) > 38:
            title = title[:35] + "..."
        print(f"{i:<6} | {score:<14} | {doc_id:<14} | {title}")

    # 3. Observability & Latency Metrics
    print("-" * 80)
    retrieval_metrics = retriever.last_retrieval_metrics
    rerank_metrics = reranker.last_rerank_metrics
    total_pipeline_ms = (
        retrieval_metrics.get("total_latency_ms", 0.0)
        + rerank_metrics.get("rerank_latency_ms", 0.0)
    )

    print("\n[Observability & Performance Metrics]")
    print(f"  * Retrieval Latency (FAISS+BM25): {retrieval_metrics.get('total_latency_ms', 0):.2f} ms")
    print(f"  * Reranking Latency (Cross-Enc): {rerank_metrics.get('rerank_latency_ms', 0):.2f} ms")
    print(f"  * Total Search Pipeline Latency: {total_pipeline_ms:.2f} ms")
    print(f"  * Candidates Scored:             {rerank_metrics.get('input_count', 0)}")
    print(f"  * Top Result Cross-Encoder Score:{rerank_metrics.get('top_score', 0):+.4f}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()


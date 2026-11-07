"""Helper script to display hybrid retrieval results cleanly."""

import sys
from pathlib import Path

# Ensure project root is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.retrieval import HybridRetriever

def main():
    query = "Login fails after password reset for some users"
    print("=" * 70)
    print("  AI QA & Bug Investigation Agent")
    print("  PHASE 5 BASELINE: HYBRID RETRIEVAL (BEFORE RERANKING)")
    print("=" * 70)
    print(f"\nQuery: '{query}'\n")

    retriever = HybridRetriever()
    results = retriever.retrieve(query=query, top_k=5)

    print("-" * 70)
    print(f"{'Rank':<6} | {'Score':<10} | {'Doc ID':<14} | {'Title'}")
    print("-" * 70)

    for i, doc in enumerate(results, start=1):
        score = f"{doc.get('hybrid_score', 0.0):.6f}"
        doc_id = doc.get("document_id", "N/A")
        title = doc.get("title", "")
        # Shorten title if too long for clean terminal display
        if len(title) > 35:
            title = title[:32] + "..."
        print(f"{i:<6} | {score:<10} | {doc_id:<14} | {title}")

    print("-" * 70)
    metrics = retriever.last_retrieval_metrics
    print(f"\n[Retrieval Metrics]")
    print(f"  * Dense Latency:   {metrics.get('dense_latency_ms', 0):.2f} ms")
    print(f"  * Sparse Latency:  {metrics.get('sparse_latency_ms', 0):.2f} ms")
    print(f"  * Total Latency:   {metrics.get('total_latency_ms', 0):.2f} ms")
    print(f"  * Cache Hit:       {metrics.get('cache_hit', False)}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()


"""End-to-end investigation pipeline connecting Hybrid Retrieval, Reranking, and Grounded LLM."""

import sys
import logging
from typing import Optional, Dict, Any

from app.rag.retrieval import HybridRetriever
from app.rag.reranker import DocumentReranker
from app.agent import get_llm_client, InvestigationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class BugInvestigationService:
    """Orchestrates Hybrid Retrieval -> Cross-Encoder Reranking -> Grounded LLM Response."""

    def __init__(self, index_dir: str = "./faiss_index", max_rerank_docs: int = 5):
        self.retriever = HybridRetriever(index_dir=index_dir)
        self.reranker = DocumentReranker(max_chunks_per_doc=2, min_score_cutoff=-10.0)
        self.max_rerank_docs = max_rerank_docs
        self.llm_client = get_llm_client()

    def investigate(self, bug_report: str) -> Dict[str, Any]:
        """Run complete investigation for a bug report query."""
        logger.info(f"Starting investigation for bug report: '{bug_report}'")

        # Step 1: Hybrid Retrieval (FAISS + BM25)
        raw_results, retrieval_meta = self.retriever.retrieve(
            query=bug_report,
            top_k=15,
            alpha=0.5,
        )

        # Step 2: Cross-Encoder Reranking
        reranked_results, rerank_meta = self.reranker.rerank(
            query=bug_report,
            documents=raw_results,
            top_k=self.max_rerank_docs,
        )

        # Step 3: Grounded LLM Investigation Generation
        investigation: InvestigationResult = self.llm_client.generate_investigation(
            query=bug_report,
            retrieved_chunks=reranked_results,
        )

        total_latency_ms = (
            retrieval_meta.get("retrieval_latency_ms", {}).get("total_ms", 0.0)
            + rerank_meta.get("rerank_latency_ms", 0.0)
            + investigation.metrics.latency_ms
        )

        return {
            "query": bug_report,
            "response": investigation.response_text,
            "is_fallback": investigation.is_fallback,
            "sources": investigation.sources,
            "chunks_used": investigation.chunks_used,
            "metrics": {
                "retrieval_latency_ms": retrieval_meta.get("retrieval_latency_ms", {}),
                "rerank_latency_ms": rerank_meta.get("rerank_latency_ms", 0.0),
                "llm_latency_ms": investigation.metrics.latency_ms,
                "total_pipeline_latency_ms": round(total_latency_ms, 2),
                "tokens": {
                    "input_tokens": investigation.metrics.input_tokens,
                    "output_tokens": investigation.metrics.output_tokens,
                    "total_tokens": investigation.metrics.total_tokens,
                },
                "estimated_cost_usd": investigation.metrics.estimated_cost_usd,
            },
        }


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Login fails after password reset for some users."

    print("=" * 70)
    print("AI QA & BUG INVESTIGATION AGENT — PHASE 6")
    print("=" * 70)
    print(f"Query: {query}\n")

    try:
        service = BugInvestigationService()
        result = service.investigate(query)

        print("\n" + "=" * 70)
        print("INVESTIGATION RESPONSE:")
        print("=" * 70)
        print(result["response"])
        print("\n" + "-" * 70)
        print("PIPELINE OBSERVABILITY & METRICS:")
        print("-" * 70)
        m = result["metrics"]
        print(f"Retrieved Chunks Used: {result['chunks_used']}")
        print(f"Sources: {', '.join(result['sources']) if result['sources'] else 'None'}")
        print(f"LLM Latency: {m['llm_latency_ms']:.2f} ms")
        print(f"Total Pipeline Latency: {m['total_pipeline_latency_ms']:.2f} ms")
        print(f"Tokens: Input={m['tokens']['input_tokens']} | Output={m['tokens']['output_tokens']} | Total={m['tokens']['total_tokens']}")
        print(f"Estimated Cost: ${m['estimated_cost_usd']:.6f} USD")
        print("=" * 70)

    except Exception as e:
        print(f"Error during investigation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


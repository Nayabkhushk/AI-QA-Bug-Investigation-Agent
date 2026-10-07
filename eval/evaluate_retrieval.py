from typing import List, Dict

import json
import os
import sys
# Ensure the project root is on the Python path so the 'app' package can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.rag.retrieval import HybridRetriever

# Paths (relative to this script's location)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EVAL_SET_PATH = os.path.join(BASE_DIR, "eval_set.json")

# Load evaluation set
with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
    eval_set: List[Dict] = json.load(f)

# Initialize retriever (FAISS index directory is relative to project root)
retriever = HybridRetriever()

# Metrics accumulators
recall_at_5 = 0
recall_at_10 = 0
precision_at_5 = 0
hit_rate_at_5 = 0

for entry in eval_set:
    query = entry["query"]
    ground_truth: List[str] = entry["relevant_docs"]

    # Retrieve top‑10 (we will slice for @5 later)
    results = retriever.retrieve(query=query, top_k=10)
    retrieved_ids = [doc.get("file_path") for doc in results]

    # Helper: count how many ground‑truth docs appear in top‑k
    def count_hits(k: int) -> int:
        return sum(1 for gt in ground_truth if any(gt in (doc_path or "") for doc_path in retrieved_ids[:k]))

    hits5 = count_hits(5)
    hits10 = count_hits(10)

    # Recall@k: all ground‑truth must be present
    if ground_truth:
        recall_at_5 += int(hits5 == len(ground_truth))
        recall_at_10 += int(hits10 == len(ground_truth))
        # Precision@5: relevant retrieved / 5
        precision_at_5 += hits5 / 5
        # Hit Rate@5: any relevant retrieved
        hit_rate_at_5 += int(hits5 > 0)
    else:
        # For no‑answer queries we treat them as successful if the retriever returns no docs
        recall_at_5 += int(len(results) == 0)
        recall_at_10 += int(len(results) == 0)
        precision_at_5 += 0
        hit_rate_at_5 += 1  # trivially true (no relevant docs needed)

num_queries = len(eval_set)
if num_queries == 0:
    raise ValueError("Evaluation set is empty.")

print("--- Retrieval Baseline Evaluation ---")
print(f"Queries evaluated: {num_queries}")
print(f"Recall@5: {recall_at_5 / num_queries:.3f}")
print(f"Recall@10: {recall_at_10 / num_queries:.3f}")
print(f"Precision@5: {precision_at_5 / num_queries:.3f}")
print(f"Hit Rate@5: {hit_rate_at_5 / num_queries:.3f}")

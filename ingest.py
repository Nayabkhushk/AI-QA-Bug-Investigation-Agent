"""ingest.py — Build and save the FAISS index from the /data folder.

Run this ONCE (or whenever you add/update documents in /data):

    python ingest.py

Output:
    faiss_index/index.faiss   — the FAISS vector index
    faiss_index/metadata.json — chunk text + metadata, aligned by row index

After this runs, the agent loads the index instantly from disk with
no re-embedding or internet access needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.ingestion import load_all_documents, chunk_document

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = "data"
INDEX_DIR = Path("faiss_index")
MODEL_NAME = "all-MiniLM-L6-v2"  # 22 MB, free, no API key required
CHUNK_MAX_WORDS = 250


def build_index() -> None:
    """Load all documents, chunk them, embed with SentenceTransformer, save to FAISS."""

    print("=" * 60)
    print("  CallFlow CRM — FAISS Ingest Pipeline")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 1. Load & chunk all markdown files from /data
    # -----------------------------------------------------------------------
    print(f"\n[1/4] Loading documents from '{DATA_DIR}/'...")
    docs = load_all_documents(DATA_DIR)
    print(f"      Loaded {len(docs)} documents.")

    all_chunks: list[dict] = []
    for doc in docs:
        chunks = chunk_document(doc, max_chunk_words=CHUNK_MAX_WORDS)
        all_chunks.extend(chunks)

    print(f"      Created {len(all_chunks)} chunks total.")

    # -----------------------------------------------------------------------
    # 2. Embed all chunks with SentenceTransformer (local, CPU, no API key)
    # -----------------------------------------------------------------------
    print(f"\n[2/4] Loading embedding model '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["text"] for chunk in all_chunks]
    print(f"      Embedding {len(texts)} chunks (this may take ~30 s on first run)...")
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,   # cosine similarity via inner product
        show_progress_bar=True,
        batch_size=64,
    )
    embeddings = np.array(embeddings, dtype="float32")
    print(f"      Embeddings shape: {embeddings.shape}")

    # -----------------------------------------------------------------------
    # 3. Build FAISS IndexFlatIP (exact cosine search, no training needed)
    # -----------------------------------------------------------------------
    print("\n[3/4] Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner Product = cosine when normalized
    index.add(embeddings)
    print(f"      Index contains {index.ntotal} vectors.")

    # -----------------------------------------------------------------------
    # 4. Save index + metadata to faiss_index/
    # -----------------------------------------------------------------------
    print(f"\n[4/4] Saving to '{INDEX_DIR}/'...")
    INDEX_DIR.mkdir(exist_ok=True)

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    # Strip numpy arrays / non-serializable fields before saving metadata
    safe_meta = []
    for chunk in all_chunks:
        safe_meta.append({
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "document_id": chunk["document_id"],
            "title": chunk["title"],
            "document_type": chunk["document_type"],
            "module": chunk["module"],
            "priority": chunk["priority"],
            "status": chunk["status"],
            "tags": chunk.get("tags", []),
            "tags_str": chunk.get("tags_str", ""),
            "file_path": chunk["file_path"],
            "text": chunk["text"],
        })

    with open(INDEX_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(safe_meta, f, indent=2, ensure_ascii=False)

    print(f"      Saved: {INDEX_DIR / 'index.faiss'}")
    print(f"      Saved: {INDEX_DIR / 'metadata.json'}")

    print("\n[OK] Ingestion complete!")
    print(f"    {len(docs)} documents -> {len(all_chunks)} chunks -> {index.ntotal} vectors")
    print("    Run the agent or tests -- no re-embedding needed until data changes.\n")


if __name__ == "__main__":
    build_index()

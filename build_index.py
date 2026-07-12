"""
Step 5: Embed chunks and store them in ChromaDB.

Run this after adding documents to `data/`:
    python build_index.py

This will (re)create a persistent Chroma collection on disk at CHROMA_DB_DIR,
so you only need to re-run it when your source documents change.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
)
from ingest import build_chunks_from_data_dir


def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def build_index():
    chunks = build_chunks_from_data_dir()
    if not chunks:
        print("No chunks to index. Add documents to the data/ folder first.")
        return

    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    model = get_embedding_model()

    texts = [c.text for c in chunks]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    # Fresh start each time we rebuild, so stale chunks don't linger
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[{"source": c.source, "chunk_index": c.chunk_index} for c in chunks],
    )

    print(f"Indexed {collection.count()} chunks into Chroma collection "
          f"'{COLLECTION_NAME}' at '{CHROMA_DB_DIR}/'.")


if __name__ == "__main__":
    build_index()
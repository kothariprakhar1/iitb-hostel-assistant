"""
Step 6: Retrieval + LLM integration (Gemini).
Step 7: Grounded "I don't know" guardrail.

Requires the GEMINI_API_KEY environment variable to be set:
    export GEMINI_API_KEY="AI..."          (Mac/Linux)
    setx GEMINI_API_KEY "AI..."            (Windows, then restart terminal)

Get a free API key at: https://aistudio.google.com/apikey

Usage:
    python rag_chain.py
"""

import sys
import os

import chromadb
from google import genai

from config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    TOP_K,
    MAX_DISTANCE_THRESHOLD,
    GEMINI_MODEL,
)
from build_index import get_embedding_model

SYSTEM_PROMPT = """You are the IITB Hostel & Campus Life Assistant.
Answer the user's question using ONLY the provided context excerpts below.
Rules:
- You MAY reasonably connect related terms in the context to the question, even if the exact
  wording differs (for example, "visiting hours" or "gate closing time" in the context can
  answer a question about "curfew" if that is clearly what it refers to).
- Only respond with "I don't know." if the context truly has nothing related to the question.
- Do not invent rules, numbers, or policies that are not present in the context.
- Keep answers concise and factual, and mention which source/rule you're basing the answer on.
"""


def retrieve(query: str, top_k: int = TOP_K):
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        raise RuntimeError(
            "No index found. Run 'python build_index.py' first after adding "
            "documents to the data/ folder."
        )

    model = get_embedding_model()
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return list(zip(docs, metadatas, distances))


def build_prompt(query: str, retrieved):
    context_blocks = []
    for i, (doc, meta, _dist) in enumerate(retrieved):
        context_blocks.append(f"[Source: {meta['source']} | chunk {meta['chunk_index']}]\n{doc}")
    context_text = "\n\n---\n\n".join(context_blocks)

    user_prompt = f"""Context excerpts:
{context_text}

Question: {query}

Answer using only the context above."""
    return user_prompt


def answer_question(query: str):
    retrieved = retrieve(query)

    if not retrieved:
        return {
            "answer": "I don't know.",
            "grounded": False,
            "sources": [],
            "reason": "No chunks retrieved.",
        }

    best_distance = retrieved[0][2]

    # Step 7 guardrail: if even the closest match is too dissimilar,
    # don't bother calling the LLM at all.
    if best_distance > MAX_DISTANCE_THRESHOLD:
        return {
            "answer": "I don't know.",
            "grounded": False,
            "sources": [],
            "reason": f"Best match distance {best_distance:.3f} exceeded threshold "
                      f"{MAX_DISTANCE_THRESHOLD}.",
        }

    user_prompt = build_prompt(query, retrieved)

    client = genai.Client()  # reads GEMINI_API_KEY from environment

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "temperature": 0,
        },
    )

    answer_text = response.text.strip()
    grounded = "i don't know" not in answer_text.lower()

    sources = [
        {"source": meta["source"], "chunk_index": meta["chunk_index"], "distance": dist}
        for _doc, meta, dist in retrieved
    ]

    return {
        "answer": answer_text,
        "grounded": grounded,
        "sources": sources,
        "reason": None,
    }


if __name__ == "__main__":
    print("IITB Hostel Assistant — type 'exit' to quit")
    while True:
        query = input("\nAsk a question: ")
        if query.lower() == "exit":
            break
        result = answer_question(query)

        print("\nAnswer:", result["answer"])
        print("Grounded:", result["grounded"])
        if result["reason"]:
            print("Reason:", result["reason"])
        if result["sources"]:
            print("\nSources used:")
            for s in result["sources"]:
                print(f"  - {s['source']} (chunk {s['chunk_index']}, distance={s['distance']:.3f})")
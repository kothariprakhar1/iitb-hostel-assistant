"""
Step 4: Parse + chunk your documents.

Drop your source files into the `data/` folder. Supported formats:
  - .txt / .md   -> read directly
  - .pdf         -> text extracted with pdfplumber
  - .html/.htm   -> text extracted with BeautifulSoup

Run this file directly to sanity-check chunking before building the index:
    python ingest.py
"""

import os
import re
import glob
import json
from dataclasses import dataclass, asdict

from config import DATA_DIR, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS


@dataclass
class Chunk:
    chunk_id: str
    source: str          # filename the chunk came from
    text: str
    chunk_index: int     # position within the source document


def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(path: str) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _read_html(path: str) -> str:
    from bs4 import BeautifulSoup
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    # Remove script/style tags before extracting text
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        return _read_txt(path)
    elif ext == ".pdf":
        return _read_pdf(path)
    elif ext in (".html", ".htm"):
        return _read_html(path)
    else:
        raise ValueError(f"Unsupported file type: {ext} ({path})")


def clean_text(text: str) -> str:
    # Collapse excessive whitespace/newlines while keeping paragraph breaks readable
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Simple word-count based sliding-window chunker."""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = end - overlap  # step forward with overlap
    return chunks


def build_chunks_from_data_dir(data_dir: str = DATA_DIR):
    all_chunks = []
    file_paths = sorted(
        glob.glob(os.path.join(data_dir, "**", "*"), recursive=True)
    )
    file_paths = [p for p in file_paths if os.path.isfile(p)]

    if not file_paths:
        print(f"[warning] No files found in '{data_dir}'. Add your source "
              f"documents there before running build_index.py.")
        return all_chunks

    for path in file_paths:
        try:
            raw_text = load_document(path)
        except ValueError as e:
            print(f"[skip] {e}")
            continue

        cleaned = clean_text(raw_text)
        if not cleaned:
            print(f"[skip] No extractable text in {path}")
            continue

        pieces = chunk_text(cleaned, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        source_name = os.path.basename(path)

        for i, piece in enumerate(pieces):
            chunk_id = f"{source_name}__chunk{i}"
            all_chunks.append(
                Chunk(chunk_id=chunk_id, source=source_name, text=piece, chunk_index=i)
            )

        print(f"[ok] {source_name}: {len(pieces)} chunks")

    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks_from_data_dir()
    print(f"\nTotal chunks created: {len(chunks)}")
    if chunks:
        print("\nSample chunk:")
        print(json.dumps(asdict(chunks[0]), indent=2)[:800])

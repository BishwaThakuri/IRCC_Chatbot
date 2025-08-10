import os
import re
import json
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Config
SOURCE_DIR = "knowledge_base/english"
VECTOR_DIR = "vector_store"
EMBED_MODEL = "all-MiniLM-L6-v2"
os.makedirs(VECTOR_DIR, exist_ok=True)

# ---------- TEXT CLEANING ----------
def clean_text(text: str) -> str:
    """Remove junk lines and normalize spaces."""
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[\.\d\s]{1,}$', line):
            continue
        if re.search(r'\.{5,}', line):
            continue
        if re.match(r'^\d{4}-\d{2}-\d{2}$', line):
            continue
        cleaned_lines.append(line)
    cleaned_text = " ".join(cleaned_lines)
    return re.sub(r'\s+', ' ', cleaned_text).strip()

# ---------- KEYWORD EXTRACTION ----------
def extract_keywords(text: str) -> List[str]:
    """Basic keyword extraction."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = {"this", "that", "with", "from", "they", "them", "have", "which", "shall"}
    keywords = sorted(set([w for w in words if w not in stopwords]))
    return keywords[:15]

# ---------- SEMANTIC CHUNKING ----------
def semantic_chunk(text: str) -> List[str]:
    """Chunk by semantic sections, then split into smaller pieces."""
    # Step 1: Split by section headings or numbers
    section_splits = re.split(r'\n(?=\d+(\.\d+)*\s+[A-Z])', text)
    
    # Step 2: Recursive splitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = []
    for section in section_splits:
        section = section.strip()
        if len(section) < 50:
            continue
        sub_chunks = splitter.split_text(section)
        chunks.extend([sc.strip() for sc in sub_chunks if len(sc.strip()) > 50])
    return chunks

# ---------- DOCUMENT LOADING ----------
def load_documents() -> List[Dict]:
    """Load JSON docs with source and page info."""
    docs = []
    for file in os.listdir(SOURCE_DIR):
        if not file.endswith(".json"):
            continue
        path = os.path.join(SOURCE_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"[WARN] Could not load {file}")
                continue

            if isinstance(data, list):
                for entry in data:
                    text = clean_text(entry.get("text", ""))
                    page = entry.get("page", None)
                    if text:
                        docs.append({"source": file, "page": page, "text": text})
            else:
                text = clean_text(data.get("text", ""))
                page = data.get("page", None)
                if text:
                    docs.append({"source": file, "page": page, "text": text})
    return docs

# ---------- CHUNK DOCUMENTS ----------
def chunk_documents(docs: List[Dict]) -> List[Dict]:
    """Split into semantic chunks with metadata."""
    all_chunks = []
    for doc in docs:
        chunks = semantic_chunk(doc["text"])
        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "page_start": doc.get("page"),
                "page_end": doc.get("page"),  # Single page for now
                "text": chunk,
                "keywords": extract_keywords(chunk),
                "char_length": len(chunk)
            })
    # Deduplicate by text content
    unique_chunks = {c["text"]: c for c in all_chunks}
    return list(unique_chunks.values())

# ---------- EMBEDDINGS ----------
def embed_chunks(chunks: List[Dict]):
    model = SentenceTransformer(EMBED_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return np.array(embeddings), chunks

# ---------- FAISS INDEX ----------
def build_faiss_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

# ---------- SAVE ----------
def save_index(index, chunks):
    faiss.write_index(index, os.path.join(VECTOR_DIR, "index.faiss"))
    with open(os.path.join(VECTOR_DIR, "chunks_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

# ---------- MAIN ----------
def main():
    print("[INFO] Loading documents...")
    docs = load_documents()
    print(f"[INFO] Loaded {len(docs)} documents.")

    print("[INFO] Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"[INFO] Total unique chunks: {len(chunks)}")

    print("[INFO] Generating embeddings...")
    embeddings, chunks = embed_chunks(chunks)

    print("[INFO] Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("[INFO] Saving index & metadata...")
    save_index(index, chunks)

    print("[DONE] Vector store created:", os.path.join(VECTOR_DIR, "index.faiss"))

if __name__ == "__main__":
    main()

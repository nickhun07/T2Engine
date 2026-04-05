#!/usr/bin/env python3
"""
RAG Regulator Indexer — OTengine4 T1 Tri-Core
===============================================
วิธีใช้:
    python3 rag-regulator-indexer.py

หรือเฉพาะ folder:
    python3 rag-regulator-indexer.py --folder core6-regulator/thai-cyber

Index ทำงานที่:
    /root/.openclaw/workspace/t1-tricore/group2-indexers/rag-sync/chroma_db/
"""

import os, json, hashlib
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings

# ========== CONFIG ==========
WORKSPACE = Path("/root/.openclaw/workspace/t1-tricore")
CHROMA_PATH = WORKSPACE / "group2-indexers/rag-sync/chroma_db"
COLLECTION_NAME = "t1_knowledge"
REGULATOR_DIR = WORKSPACE / "core6-regulator"

# Supported file types
MARKDOWN_EXTS = {".md", ".txt", ".text"}
JSON_EXTS = {".json"}
# ========== CONFIG ==========

def load_chroma():
    """Connect to existing ChromaDB"""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    col = client.get_collection(COLLECTION_NAME)
    return client, col

def compute_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()[:12]

def index_file(file_path: Path, source_label: str) -> list:
    """Index a single file into ChromaDB"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠️  Cannot read {file_path}: {e}")
        return []

    # Skip if too short
    if len(content) < 100:
        print(f"  ⏭️  Skipping (too short): {file_path.name}")
        return []

    # Split into chunks (by section for regulations)
    chunks = split_into_chunks(content, file_path.name)

    docs, metadatas, ids = [], [], []
    for i, chunk in enumerate(chunks):
        chunk_hash = compute_hash(chunk)
        docs.append(chunk)
        metadatas.append({
            "source": str(file_path),
            "source_label": source_label,
            "type": "regulation",
            "indexed_at": datetime.now().isoformat(),
            "chunk_idx": i,
            "total_chunks": len(chunks),
            "file_hash": chunk_hash
        })
        ids.append(f"reg-{file_path.stem}-{i}-{chunk_hash}")

    return [{"docs": docs, "metadatas": metadatas, "ids": ids}]

def split_into_chunks(content: str, filename: str) -> list:
    """Split regulation text into semantic chunks"""
    chunks = []

    # Try to split by markdown headers (## = section)
    if "##" in content:
        sections = content.split("##")
        for sec in sections:
            sec = sec.strip()
            if len(sec) > 100:
                # Get section title (first line)
                lines = sec.split("\n", 1)
                title = lines[0].strip()
                body = lines[1] if len(lines) > 1 else ""
                chunks.append(f"## {title}\n{body[:2000]}")  # Max 2000 chars per section

    # If no headers, split by paragraphs
    if not chunks:
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and len(p) > 100]
        for para in paragraphs:
            if len(para) > 100:
                chunks.append(para[:2000])

    # Final fallback: whole file
    if not chunks:
        chunks = [content[:2000]]

    return chunks

def scan_and_index(folder_path: Path = None) -> dict:
    """
    Scan core6-regulator folder and index all regulation documents.
    Returns summary dict.
    """
    if folder_path is None:
        folder_path = REGULATOR_DIR

    # Get existing sources to avoid duplicates
    _, col = load_chroma()
    existing = col.get(include=["metadatas"])
    existing_sources = {m["source"] for m in existing["metadatas"]} if existing["metadatas"] else set()

    stats = {"files_found": 0, "files_indexed": 0, "files_skipped": 0, "chunks_added": 0}

    # Walk through all regulation subdirectories
    for subdir in sorted(REGULATOR_DIR.iterdir()):
        if not subdir.is_dir():
            continue

        source_label = f"core6-regulator/{subdir.name}"
        print(f"\n📁 {subdir.name}/")

        for file_path in sorted(subdir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in MARKDOWN_EXTS | JSON_EXTS:
                continue

            stats["files_found"] += 1

            if str(file_path) in existing_sources:
                print(f"  ⏭️  Already indexed: {file_path.name}")
                stats["files_skipped"] += 1
                continue

            print(f"  📄 Indexing: {file_path.name}")
            result = index_file(file_path, source_label)

            if result:
                docs = result[0]["docs"]
                metas = result[0]["metadatas"]
                ids = result[0]["ids"]
                col.add(documents=docs, metadatas=metas, ids=ids)
                print(f"    ✅ {len(docs)} chunks added")
                stats["files_indexed"] += 1
                stats["chunks_added"] += len(docs)
            else:
                stats["files_skipped"] += 1

    return stats

def reindex_all() -> dict:
    """Delete all existing regulation entries and re-index from scratch"""
    print("⚠️  Re-indexing all regulation documents...")
    client, col = load_chroma()

    # Get all existing regulation IDs
    all_data = col.get(include=["metadatas"])
    reg_ids = [
        d["id"] for d in all_data["metadatas"]
        if d.get("type") == "regulation"
    ]

    if reg_ids:
        print(f"🗑️  Deleting {len(reg_ids)} existing regulation chunks...")
        col.delete(ids=reg_ids)

    # Re-index
    return scan_and_index()

def status() -> dict:
    """Show RAG status"""
    _, col = load_chroma()
    all_data = col.get(include=["metadatas"])

    total = len(all_data["metadatas"])
    by_source = {}
    for m in all_data["metadatas"]:
        label = m.get("source_label", "unknown")
        by_source[label] = by_source.get(label, 0) + 1

    return {
        "total_vectors": total,
        "by_source_label": dict(sorted(by_source.items()))
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reindex":
        print("🔄 Re-indexing all regulations...")
        result = reindex_all()
    else:
        print("🔍 Scanning for new regulations...")
        result = scan_and_index()

    print("\n" + "=" * 40)
    print("✅ Indexing complete!")
    print(f"   Files found:    {result['files_found']}")
    print(f"   Files indexed:  {result['files_indexed']}")
    print(f"   Files skipped:  {result['files_skipped']}")
    print(f"   Chunks added:   {result['chunks_added']}")
    print()
    print("📊 Current RAG status:")
    st = status()
    print(f"   Total vectors: {st['total_vectors']}")
    for label, count in st["by_source_label"].items():
        print(f"   • {label}: {count}")

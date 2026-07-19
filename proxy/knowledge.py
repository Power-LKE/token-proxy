"""
Knowledge base (RAG) management.
Simple TF-IDF + cosine similarity search (no external vector DB required).
This keeps the project deployable on Render free tier (512MB RAM).
"""

import json
import os
import re
import math
from typing import Optional, List, Dict, Any
from datetime import datetime

from proxy.storage import create_store, DataStore


class KnowledgeBaseManager:
    """Manages knowledge bases with basic TF-IDF search."""

    def __init__(self):
        self._store: DataStore = create_store(row_id="linkpower_knowledge")
        self._data: Dict[str, dict] = {}  # kb_id -> {name, docs: [{id, filename, content, chunks}]}
        self._load()

    def _load(self):
        try:
            raw = self._store.load()
            if raw:
                self._data = json.loads(raw.decode("utf-8"))
        except Exception:
            self._data = {}

    def _save(self):
        data = json.dumps(self._data, ensure_ascii=False, indent=2).encode("utf-8")
        self._store.save(data)

    # ── CRUD ────────────────────────────────────────────────

    def list_kb(self, api_key: str) -> List[dict]:
        """List knowledge bases for a user."""
        result = []
        for kb_id, kb in self._data.items():
            if kb.get("owner") == api_key:
                result.append({
                    "id": kb_id,
                    "name": kb.get("name", ""),
                    "doc_count": len(kb.get("docs", [])),
                    "created_at": kb.get("created_at", ""),
                })
        return result

    def create_kb(self, api_key: str, name: str) -> dict:
        """Create a new knowledge base."""
        kb_id = "kb-" + str(int(datetime.now().timestamp() * 1000))
        kb = {
            "id": kb_id,
            "name": name,
            "owner": api_key,
            "docs": [],
            "created_at": datetime.now().isoformat(),
        }
        self._data[kb_id] = kb
        self._save()
        return kb

    def delete_kb(self, api_key: str, kb_id: str) -> bool:
        """Delete a knowledge base."""
        kb = self._data.get(kb_id)
        if kb and kb.get("owner") == api_key:
            del self._data[kb_id]
            self._save()
            return True
        return False

    def upload_doc(self, api_key: str, kb_id: str, filename: str, content: str) -> Optional[dict]:
        """Upload a document to a knowledge base."""
        kb = self._data.get(kb_id)
        if not kb or kb.get("owner") != api_key:
            return None

        # Chunk the document (simple fixed-size chunks with overlap)
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)

        doc = {
            "id": "doc-" + str(int(datetime.now().timestamp() * 1000)),
            "filename": filename,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "char_count": len(content),
            "uploaded_at": datetime.now().isoformat(),
        }
        kb.setdefault("docs", []).append(doc)
        self._save()
        return doc

    def delete_doc(self, api_key: str, kb_id: str, doc_id: str) -> bool:
        """Delete a document from a knowledge base."""
        kb = self._data.get(kb_id)
        if not kb or kb.get("owner") != api_key:
            return False
        docs = kb.get("docs", [])
        for i, d in enumerate(docs):
            if d.get("id") == doc_id:
                docs.pop(i)
                self._save()
                return True
        return False

    # ── Search (TF-IDF) ─────────────────────────────────────

    def search(self, api_key: str, kb_id: str, query: str, top_k: int = 5) -> List[dict]:
        """Search a knowledge base for relevant chunks."""
        kb = self._data.get(kb_id)
        if not kb or kb.get("owner") != api_key:
            return []

        all_chunks = []
        for doc in kb.get("docs", []):
            for i, chunk in enumerate(doc.get("chunks", [])):
                all_chunks.append({
                    "text": chunk,
                    "filename": doc.get("filename", ""),
                    "doc_id": doc.get("id", ""),
                    "chunk_index": i,
                })

        if not all_chunks:
            return []

        # Build TF-IDF vectors
        corpus = [self._tokenize(c["text"]) for c in all_chunks]
        query_tokens = self._tokenize(query)
        idf = self._compute_idf(corpus, query_tokens)
        tf = [self._compute_tf(doc_tokens, query_tokens) for doc_tokens in corpus]

        # Score and rank
        for i, chunk in enumerate(all_chunks):
            chunk["score"] = sum(tf[i].get(t, 0) * idf.get(t, 0) for t in query_tokens)

        all_chunks.sort(key=lambda c: c["score"], reverse=True)
        return all_chunks[:top_k]

    # ── Helpers ─────────────────────────────────────────────

    def _tokenize(self, text: str) -> List[str]:
        """Simple Chinese/English tokenizer."""
        # Split on non-word characters, keep Chinese chars as individual tokens
        text = text.lower()
        # Keep alphanumeric and Chinese characters
        tokens = re.findall(r'[一-鿿]|[a-zA-Z0-9]+', text)
        return [t for t in tokens if len(t) > 0]

    def _compute_tf(self, doc_tokens: List[str], query_tokens: List[str]) -> dict:
        """Compute TF for query terms in a document."""
        tf = {}
        doc_len = max(len(doc_tokens), 1)
        for token in query_tokens:
            tf[token] = doc_tokens.count(token) / doc_len
        return tf

    def _compute_idf(self, corpus: List[List[str]], query_tokens: List[str]) -> dict:
        """Compute IDF for query terms across corpus."""
        idf = {}
        N = max(len(corpus), 1)
        for token in query_tokens:
            df = sum(1 for doc in corpus if token in doc)
            idf[token] = math.log((N + 1) / (df + 1)) + 1
        return idf

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            # Try to break at a sentence boundary
            if end < len(text):
                for sep in ['。', '.', '！', '？', '\n\n', '\n', ' ']:
                    last = text.rfind(sep, start, end)
                    if last > start + chunk_size // 2:
                        end = last + 1
                        break
            chunks.append(text[start:end].strip())
            start = end - overlap if end < len(text) else len(text)
        return [c for c in chunks if c]


kb_manager = KnowledgeBaseManager()

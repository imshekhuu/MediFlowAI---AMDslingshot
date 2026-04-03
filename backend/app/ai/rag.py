"""
MediFlow AI - RAG (Retrieval Augmented Generation)
Uses FAISS + sentence-transformers to retrieve relevant patient history
"""

import os
import json
from typing import List, Optional
from functools import lru_cache

# ─── FAISS + Embeddings ───────────────────────────────────
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[RAG] FAISS/sentence-transformers not available. RAG disabled.")

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./mediflow_faiss.index")
FAISS_DOCS_PATH = os.getenv("FAISS_DOCS_PATH", "./mediflow_faiss_docs.json")


class MediFlowRAG:
    """
    RAG engine for MediFlow AI.
    Stores patient symptom history as embeddings and retrieves
    semantically similar past cases to augment AI analysis.
    """

    def __init__(self):
        self.embed_model = None
        self.index = None
        self.documents: List[dict] = []
        self._initialized = False

        if FAISS_AVAILABLE:
            self._init()

    def _init(self):
        """Initialize embeddings model and FAISS index."""
        try:
            self.embed_model = SentenceTransformer(EMBED_MODEL_NAME)
            dim = self.embed_model.get_sentence_embedding_dimension()

            # Load existing index if available
            if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_DOCS_PATH):
                self.index = faiss.read_index(FAISS_INDEX_PATH)
                with open(FAISS_DOCS_PATH, "r") as f:
                    self.documents = json.load(f)
                print(f"[RAG] Loaded existing FAISS index ({self.index.ntotal} entries)")
            else:
                self.index = faiss.IndexFlatL2(dim)
                self.documents = []
                print(f"[RAG] New FAISS index created (dim={dim})")

            self._initialized = True
        except Exception as e:
            print(f"[RAG] Init failed: {e}")
            self._initialized = False

    def _save(self):
        """Persist FAISS index and documents to disk."""
        if self.index:
            faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_DOCS_PATH, "w") as f:
            json.dump(self.documents, f)

    def add_entry(self, patient_id: int, symptoms: str, priority: str, explanation: str):
        """Add a new symptom entry to the vector store."""
        if not self._initialized:
            return
        try:
            text = f"Patient {patient_id}: {symptoms}"
            embedding = self.embed_model.encode([text]).astype("float32")
            self.index.add(embedding)
            self.documents.append({
                "patient_id": patient_id,
                "symptoms": symptoms,
                "priority": priority,
                "explanation": explanation,
                "text": text,
            })
            self._save()
        except Exception as e:
            print(f"[RAG] add_entry error: {e}")

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """Retrieve the top-k most semantically similar cases."""
        if not self._initialized or self.index.ntotal == 0:
            return []
        try:
            embedding = self.embed_model.encode([query]).astype("float32")
            distances, indices = self.index.search(embedding, min(top_k, self.index.ntotal))
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    results.append(self.documents[idx])
            return results
        except Exception as e:
            print(f"[RAG] retrieve error: {e}")
            return []

    def build_context(self, symptoms: str) -> str:
        """Build context string from retrieved cases for LLM augmentation."""
        cases = self.retrieve(symptoms)
        if not cases:
            return ""
        context_lines = ["Similar historical cases:"]
        for i, case in enumerate(cases, 1):
            context_lines.append(
                f"{i}. Symptoms: {case['symptoms']} → Priority: {case['priority']}"
            )
        return "\n".join(context_lines)


@lru_cache(maxsize=1)
def get_rag() -> MediFlowRAG:
    """Singleton RAG instance."""
    return MediFlowRAG()

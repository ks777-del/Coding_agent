# intelligence/rag/vector_store.py

import numpy as np
from typing import List, Dict, Any, Tuple
import pickle
import os


class VectorStore:
    """
    Lightweight FAISS-style vector store (can be swapped with FAISS later)
    """

    def __init__(self, dim: int = 64, path: str = "./memory/vectors.db"):
        self.dim = dim
        self.path = path

        self.vectors: List[np.ndarray] = []
        self.payloads: List[Dict[str, Any]] = []

        self._load()

    def add(self, vector: List[float], payload: Dict[str, Any]):
        self.vectors.append(np.array(vector, dtype=np.float32))
        self.payloads.append(payload)
        self._save()

    def cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[float, Dict]]:
        q = np.array(query_vector, dtype=np.float32)

        scored = []
        for vec, payload in zip(self.vectors, self.payloads):
            score = self.cosine(q, vec)
            scored.append((score, payload))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:top_k]

    def _save(self):
        with open(self.path, "wb") as f:
            pickle.dump((self.vectors, self.payloads), f)

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.vectors, self.payloads = pickle.load(f)
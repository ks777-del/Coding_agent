import faiss
import numpy as np
from typing import List, Dict, Tuple


class FAISSVectorStore:
    """
    Production-grade vector memory store
    """

    def __init__(self, dim: int):
        self.dim = dim

        self.index = faiss.IndexFlatIP(dim)  # cosine-like similarity
        self.metadata: List[Dict] = []

    def add(self, vector: List[float], metadata: Dict):
        vec = np.array([vector]).astype("float32")

        # normalize for cosine similarity
        faiss.normalize_L2(vec)

        self.index.add(vec)
        self.metadata.append(metadata)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[float, Dict]]:
        q = np.array([query_vector]).astype("float32")
        faiss.normalize_L2(q)

        scores, indices = self.index.search(q, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append((float(score), self.metadata[idx]))

        return results
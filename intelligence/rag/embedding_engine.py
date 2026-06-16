# intelligence/rag/embedding_engine.py

from typing import List, Protocol
import numpy as np


class EmbeddingModel(Protocol):
    def encode(self, text: str) -> List[float]:
        ...


class SimpleEmbeddingEngine:
    """
    Production-ready abstraction layer.
    Swap this with:
    - sentence-transformers
    - OpenAI embeddings
    - custom model later
    """

    def __init__(self, model: EmbeddingModel = None):
        self.model = model or self._default_model()

    def _default_model(self):
        # lightweight fallback (DO NOT use in production scale)
        import hashlib

        class HashEmbedding:
            def encode(self, text: str):
                h = hashlib.sha256(text.encode()).digest()
                vec = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
                return (vec / 255.0).tolist()

        return HashEmbedding()

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text)
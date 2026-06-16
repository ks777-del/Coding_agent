# intelligence/memory_core/memory_retriever.py

from typing import List, Dict
import math

from .memory_types import MemoryType, MemoryRecord
from .memory_manager import MemoryManager
from .memory_config import MemoryConfig


class MemoryRetriever:
    """
    Responsible for:
    - Finding relevant memories
    - Ranking memories
    - Filtering context for LLM
    """

    def __init__(self, manager: MemoryManager, config: MemoryConfig):
        self.manager = manager
        self.config = config

    def _score(self, memory: Dict, query: str) -> float:
        """
        Lightweight heuristic scorer (upgrade to embeddings later)
        """

        text = str(memory.get("content", {})).lower()
        query = query.lower()

        score = 0.0

        # keyword overlap
        for word in query.split():
            if word in text:
                score += 1.0

        # recency boost
        score += memory.get("access_count", 0) * 0.1

        return score

    def search(self, memory_type: MemoryType, query: str, top_k: int = None) -> List[Dict]:
        top_k = top_k or self.config.TOP_K_RETRIEVAL

        memories = self.manager.list_all(memory_type)

        scored = []

        for m in memories:
            score = self._score(m, query)
            scored.append((score, m))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [m for score, m in scored[:top_k] if score > 0]

    def get_project_context(self, project_name: str) -> List[Dict]:
        memories = self.manager.list_all(MemoryType.PROJECT)

        return [
            m for m in memories
            if m.get("content", {}).get("project_name") == project_name
        ]

    def get_recent_bugs(self, limit: int = 5) -> List[Dict]:
        memories = self.manager.list_all(MemoryType.BUG)

        sorted_mem = sorted(
            memories,
            key=lambda x: x.get("timestamp", 0),
            reverse=True
        )

        return sorted_mem[:limit]
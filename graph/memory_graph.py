# graph/memory_graph.py

from collections import defaultdict
from typing import Dict, List


class MemoryGraph:
    """
    Stores learned relationships from execution history.

    Example:
    - bug A → file X
    - fix B → pattern Y
    """

    def __init__(self):
        self.graph = defaultdict(list)

    def add_relation(self, source: str, target: str, meta: Dict = None):
        self.graph[source].append({
            "target": target,
            "meta": meta or {}
        })

    def get_related(self, node: str) -> List[Dict]:
        return self.graph.get(node, [])

    def find_common_patterns(self, node: str) -> List[str]:

        relations = self.graph.get(node, [])

        return list(set(
            r["meta"].get("pattern", "unknown")
            for r in relations
        ))
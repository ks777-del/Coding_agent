# graph/project_graph.py

from typing import Dict, List, Set
from collections import defaultdict


class ProjectGraph:
    """
    AAA-level unified project knowledge graph.

    Combines:
    - code structure
    - dependencies
    - memory relations
    """

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges = defaultdict(set)

    def add_node(self, node: str):
        self.nodes.add(node)

    def add_edge(self, src: str, dst: str, relation: str = "related"):
        self.nodes.update([src, dst])
        self.edges[src].add((dst, relation))

    def get_neighbors(self, node: str) -> List[str]:
        return [n for n, _ in self.edges.get(node, [])]

    def get_full_graph(self) -> Dict:
        return {
            "nodes": list(self.nodes),
            "edges": {
                k: list(v) for k, v in self.edges.items()
            }
        }
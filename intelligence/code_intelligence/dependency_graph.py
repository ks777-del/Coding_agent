# core/code_intelligence/dependency_graph.py

from collections import defaultdict
from typing import Dict, Set, List
import networkx as nx


class DependencyGraph:
    """
    AAA-level dependency intelligence system.

    Tracks:
    - imports
    - file relationships
    - module dependencies
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.file_deps: Dict[str, Set[str]] = defaultdict(set)

    def add_dependency(self, source: str, target: str, dep_type: str = "import"):
        """
        source -> target relationship
        """
        self.graph.add_edge(source, target, type=dep_type)
        self.file_deps[source].add(target)

    def get_dependencies(self, file_path: str) -> List[str]:
        return list(self.file_deps.get(file_path, []))

    def get_reverse_dependencies(self, file_path: str) -> List[str]:
        return [
            n for n in self.graph.predecessors(file_path)
        ]

    def impact_scope(self, file_path: str) -> Set[str]:
        """
        Full transitive impact analysis
        """
        impacted = set()

        def dfs(node):
            for neighbor in self.graph.successors(node):
                if neighbor not in impacted:
                    impacted.add(neighbor)
                    dfs(neighbor)

        dfs(file_path)
        return impacted
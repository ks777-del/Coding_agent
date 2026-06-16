# graph/dependency_graph.py

from typing import Dict, Set
from collections import defaultdict


class DependencyGraph:
    """
    Tracks file-level dependencies and coupling strength.
    """

    def __init__(self):
        self.graph = defaultdict(set)

    def add_dependency(self, file: str, depends_on: str):
        self.graph[file].add(depends_on)

    def get_dependencies(self, file: str) -> Set[str]:
        return self.graph.get(file, set())

    def get_reverse_dependencies(self, target: str) -> Set[str]:
        return {
            f for f, deps in self.graph.items()
            if target in deps
        }

    def impact_score(self, file: str) -> int:
        return len(self.get_reverse_dependencies(file))
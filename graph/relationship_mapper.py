# graph/relationship_mapper.py

from typing import Dict, List


class RelationshipMapper:
    """
    AAA-level relationship inference engine.

    Connects:
    - files
    - functions
    - bugs
    - patterns
    """

    def map_relationships(self, graph_data: Dict) -> List[Dict]:

        relationships = []

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", {})

        for src, connections in edges.items():
            for dst, relation in connections:

                weight = self._calculate_weight(relation)

                relationships.append({
                    "from": src,
                    "to": dst,
                    "relation": relation,
                    "weight": weight
                })

        return relationships

    def _calculate_weight(self, relation: str) -> float:

        weights = {
            "contains_function": 0.6,
            "contains_class": 0.8,
            "imports": 0.9,
            "imports_from": 0.85,
            "related": 0.5
        }

        return weights.get(relation, 0.3)
# core/context_engine.py

from typing import Dict, List


class ContextEngine:
    """
    AAA-level context builder.

    Selects ONLY relevant project context for LLM reasoning.
    """

    def build_context(self, query: str, project_map: Dict) -> Dict:

        relevant_files = []

        for file, content in project_map.items():
            if any(word in content.lower() for word in query.lower().split()):
                relevant_files.append(file)

        return {
            "query": query,
            "relevant_files": relevant_files[:10],
            "compressed": True
        }
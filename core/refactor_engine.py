# core/refactor_engine.py

from typing import Dict, List


class RefactorEngine:
    """
    AAA-level refactoring system.

    Performs structure-level improvements.
    """

    def suggest_refactors(self, code: str) -> List[str]:

        suggestions = []

        if "print(" in code:
            suggestions.append("Replace print statements with logger")

        if len(code.split("\n")) > 200:
            suggestions.append("Break file into modules")

        if "import *" in code:
            suggestions.append("Avoid wildcard imports")

        return suggestions
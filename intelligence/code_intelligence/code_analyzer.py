# core/code_intelligence/code_analyzer.py

import ast
from typing import Dict, List, Any


class CodeAnalyzer:
    """
    AAA-level AST intelligence layer.

    Extracts:
    - functions
    - classes
    - imports
    - calls
    """

    def analyze(self, source_code: str) -> Dict[str, Any]:
        tree = ast.parse(source_code)

        return {
            "functions": self._get_functions(tree),
            "classes": self._get_classes(tree),
            "imports": self._get_imports(tree),
            "calls": self._get_calls(tree)
        }

    def _get_functions(self, tree):
        return [
            n.name for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)
        ]

    def _get_classes(self, tree):
        return [
            n.name for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef)
        ]

    def _get_imports(self, tree):
        imports = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.append(alias.name)
        return imports

    def _get_calls(self, tree):
        calls = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                if hasattr(n.func, "id"):
                    calls.append(n.func.id)
        return calls
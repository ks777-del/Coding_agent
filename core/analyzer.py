# core/analyzer.py

import ast
from typing import Dict


class Analyzer:
    """
    AAA-level static code analyzer.
    """

    def analyze(self, code: str) -> Dict:

        tree = ast.parse(code)

        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        return {
            "functions": functions,
            "classes": classes,
            "complexity_hint": len(functions) + len(classes)
        }
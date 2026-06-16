# intelligence/rag/project_indexer.py

import os
from typing import Dict, List


class ProjectIndexer:
    """
    Scans codebase and builds semantic index
    """

    def __init__(self, root_path: str):
        self.root_path = root_path

    def scan_files(self) -> List[str]:
        code_files = []

        for root, _, files in os.walk(self.root_path):
            for file in files:
                if file.endswith((".py", ".js", ".cpp", ".ts")):
                    code_files.append(os.path.join(root, file))

        return code_files

    def extract_structure(self, file_path: str) -> Dict:
        """
        Lightweight structure extraction (upgrade later with AST parsing)
        """

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "file": file_path,
                "size": len(content),
                "imports": self._extract_imports(content),
                "functions": self._extract_functions(content),
            }

        except Exception:
            return {"file": file_path, "error": "read_failed"}

    def _extract_imports(self, content: str):
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("import") or line.strip().startswith("from")
        ]

    def _extract_functions(self, content: str):
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("def ")
        ]

    def build_index(self) -> List[Dict]:
        files = self.scan_files()
        return [self.extract_structure(f) for f in files]
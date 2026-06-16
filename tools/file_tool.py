# tools/file_tool.py

import os
from typing import List, Dict
from pathlib import Path


class FileTool:
    """
    AAA SAFE FILE SYSTEM TOOL

    - sandbox-aware
    - path validation
    - no traversal attacks
    """

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()

    def _safe_path(self, path: str) -> Path:
        full_path = (self.root / path).resolve()

        if not str(full_path).startswith(str(self.root)):
            raise PermissionError("Path escape blocked")

        return full_path

    def read(self, path: str) -> str:
        p = self._safe_path(path)
        return p.read_text(encoding="utf-8")

    def write(self, path: str, content: str):
        p = self._safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def list_files(self, directory: str = ".") -> List[str]:
        d = self._safe_path(directory)
        return [str(p.relative_to(self.root)) for p in d.rglob("*") if p.is_file()]

    def delete(self, path: str):
        p = self._safe_path(path)
        if p.exists():
            p.unlink()
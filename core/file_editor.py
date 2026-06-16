# core/file_editor.py

import os
from typing import Dict


class FileEditor:
    """
    Safe single-file editing engine.
    """

    def write_file(self, path: str, content: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def append_file(self, path: str, content: str):
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + content)
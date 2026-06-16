# core/code_intelligence/code_search_engine.py

from typing import List, Dict
import re


class CodeSearchEngine:
    """
    AAA-level semantic + structural code search.

    Supports:
    - symbol search
    - regex search
    - file-aware filtering
    """

    def __init__(self, symbol_tracker):
        self.symbol_tracker = symbol_tracker
        self.file_cache: Dict[str, str] = {}

    def index_file(self, file_path: str, content: str):
        self.file_cache[file_path] = content

    def search_symbol(self, query: str):
        results = []

        for symbol in self.symbol_tracker.symbols.values():
            if query.lower() in symbol.name.lower():
                results.append({
                    "name": symbol.name,
                    "file": symbol.file_path,
                    "type": symbol.type,
                    "line": symbol.line
                })

        return results

    def search_regex(self, pattern: str):
        compiled = re.compile(pattern)
        matches = []

        for file_path, content in self.file_cache.items():
            for i, line in enumerate(content.split("\n")):
                if compiled.search(line):
                    matches.append({
                        "file": file_path,
                        "line": i,
                        "content": line.strip()
                    })

        return matches

    def find_usage(self, symbol_name: str):
        results = []

        for file_path, content in self.file_cache.items():
            if symbol_name in content:
                results.append(file_path)

        return results
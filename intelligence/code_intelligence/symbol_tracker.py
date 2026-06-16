# core/code_intelligence/symbol_tracker.py

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import hashlib


@dataclass
class Symbol:
    name: str
    type: str  # function | class | variable | module
    file_path: str
    line: int
    references: Set[str] = field(default_factory=set)


class SymbolTracker:
    """
    AAA-level symbol registry.

    Purpose:
    - Track every symbol across project
    - Enable cross-file resolution
    - Power refactoring + impact analysis
    """

    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.file_index: Dict[str, Set[str]] = {}

    def _make_key(self, name: str, file_path: str) -> str:
        return hashlib.md5(f"{file_path}:{name}".encode()).hexdigest()

    def add_symbol(self, name: str, type_: str, file_path: str, line: int):
        key = self._make_key(name, file_path)

        symbol = Symbol(
            name=name,
            type=type_,
            file_path=file_path,
            line=line
        )

        self.symbols[key] = symbol

        if file_path not in self.file_index:
            self.file_index[file_path] = set()

        self.file_index[file_path].add(key)

    def get_symbol(self, name: str, file_path: str) -> Optional[Symbol]:
        key = self._make_key(name, file_path)
        return self.symbols.get(key)

    def get_file_symbols(self, file_path: str) -> List[Symbol]:
        return [
            self.symbols[k]
            for k in self.file_index.get(file_path, [])
        ]

    def link_reference(self, name: str, file_path: str, reference: str):
        symbol = self.get_symbol(name, file_path)
        if symbol:
            symbol.references.add(reference)
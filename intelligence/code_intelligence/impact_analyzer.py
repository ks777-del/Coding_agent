# core/code_intelligence/impact_analyzer.py

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class ImpactReport:
    target: str
    risk_level: str
    affected_files: Set[str]
    affected_symbols: Set[str]
    recommendations: List[str]


class ImpactAnalyzer:
    """
    AAA-level change prediction engine.

    This is what makes agents feel:
    → "careful"
    → "aware"
    → "Claude-like"
    """

    def __init__(self, dependency_graph, symbol_tracker):
        self.dependency_graph = dependency_graph
        self.symbol_tracker = symbol_tracker

    def analyze_file_change(self, file_path: str) -> ImpactReport:

        affected_files = self.dependency_graph.impact_scope(file_path)

        affected_symbols = set()
        for f in affected_files:
            symbols = self.symbol_tracker.get_file_symbols(f)
            for s in symbols:
                affected_symbols.add(s.name)

        risk = self._compute_risk(len(affected_files), len(affected_symbols))

        return ImpactReport(
            target=file_path,
            risk_level=risk,
            affected_files=affected_files,
            affected_symbols=affected_symbols,
            recommendations=self._generate_recommendations(risk)
        )

    def analyze_symbol_change(self, symbol_name: str) -> ImpactReport:
        affected_files = set()

        for symbol in self.symbol_tracker.symbols.values():
            if symbol_name in symbol.references:
                affected_files.add(symbol.file_path)

        risk = self._compute_risk(len(affected_files), 0)

        return ImpactReport(
            target=symbol_name,
            risk_level=risk,
            affected_files=affected_files,
            affected_symbols=set(),
            recommendations=self._generate_recommendations(risk)
        )

    def _compute_risk(self, files: int, symbols: int) -> str:
        score = files * 2 + symbols

        if score < 5:
            return "LOW"
        elif score < 15:
            return "MEDIUM"
        return "HIGH"

    def _generate_recommendations(self, risk: str) -> List[str]:
        if risk == "HIGH":
            return [
                "Run full test suite",
                "Review dependency chain",
                "Apply staged refactor"
            ]
        if risk == "MEDIUM":
            return [
                "Run unit tests",
                "Check imports"
            ]
        return [
            "Safe change",
            "Quick validation recommended"
        ]
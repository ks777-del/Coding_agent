# self_healing/regression_detector.py

from __future__ import annotations

import ast
import subprocess
import difflib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class RegressionIssue:
    file_path: str
    issue_type: str  # syntax_error | test_failure | behavior_change | import_break | semantic_drift
    severity: float
    message: str
    affected_symbol: Optional[str] = None


@dataclass
class RegressionReport:
    has_regression: bool
    issues: List[RegressionIssue]
    risk_score: float
    dependency_impact: Dict[str, int]
    semantic_drift_score: float
    summary: str


@dataclass
class FixPatch:
    file_path: str
    suggested_change: str
    reason: str
    confidence: float


@dataclass
class FixPlan:
    patches: List[FixPatch]
    strategy: str
    expected_recovery_score: float


# ============================================================
# CORE DETECTOR ENGINE
# ============================================================

class RegressionDetector:

    def __init__(
        self,
        project_root: str = ".",
        dependency_graph: Optional[Dict[str, List[str]]] = None,
        embeddings_index: Optional[Dict[str, List[float]]] = None
    ):
        self.project_root = Path(project_root)

        # Repo dependency graph:
        # file -> downstream files
        self.dependency_graph = dependency_graph or defaultdict(list)

        # "Semantic memory" embeddings (lightweight placeholder)
        # file_path -> vector
        self.embeddings_index = embeddings_index or {}

    # ========================================================
    # MAIN PIPELINE (SELF-HEAL LOOP ENTRY)
    # ========================================================

    def analyze(self, changed_files: List[str]) -> RegressionReport:

        issues: List[RegressionIssue] = []

        for f in changed_files:
            path = Path(f)

            issues.extend(self._check_syntax(path))
            issues.extend(self._check_imports(path))
            issues.extend(self._check_behavior_diff(path))
            issues.extend(self._check_semantic_drift(path))

        issues.extend(self._run_tests())

        dependency_impact = self._analyze_dependency_impact(changed_files)
        semantic_score = self._compute_semantic_drift(changed_files)

        risk = self._compute_risk(issues, dependency_impact, semantic_score)

        return RegressionReport(
            has_regression=len(issues) > 0,
            issues=issues,
            risk_score=risk,
            dependency_impact=dependency_impact,
            semantic_drift_score=semantic_score,
            summary=self._summarize(issues, dependency_impact, semantic_score, risk)
        )

    # ========================================================
    # 1. SYNTAX CHECK 🧠
    # ========================================================

    def _check_syntax(self, file_path: Path) -> List[RegressionIssue]:

        if not file_path.exists():
            return []

        try:
            ast.parse(file_path.read_text(encoding="utf-8"))
            return []
        except SyntaxError as e:
            return [RegressionIssue(
                file_path=str(file_path),
                issue_type="syntax_error",
                severity=1.0,
                message=str(e)
            )]

    # ========================================================
    # 2. IMPORT VALIDATION 🔗
    # ========================================================

    def _check_imports(self, file_path: Path) -> List[RegressionIssue]:

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))

            issues = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module is None:
                    issues.append(RegressionIssue(
                        file_path=str(file_path),
                        issue_type="import_break",
                        severity=0.8,
                        message="Broken import statement detected"
                    ))

            return issues

        except Exception:
            return [RegressionIssue(
                file_path=str(file_path),
                issue_type="import_break",
                severity=0.9,
                message="Failed import analysis"
            )]

    # ========================================================
    # 3. BEHAVIOR CHANGE DETECTION 🧩
    # ========================================================

    def _check_behavior_diff(self, file_path: Path) -> List[RegressionIssue]:

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()

            if len(lines) == 0:
                return [RegressionIssue(
                    file_path=str(file_path),
                    issue_type="behavior_change",
                    severity=0.7,
                    message="File became empty"
                )]

            return []

        except Exception:
            return []

    # ========================================================
    # 4. SEMANTIC DRIFT DETECTION 🧬
    # ========================================================

    def _check_semantic_drift(self, file_path: Path) -> List[RegressionIssue]:

        """
        Simulated embedding drift detection.
        In real system → replace with:
            - code embeddings (OpenAI / CodeBERT / custom model)
        """

        try:
            content = file_path.read_text(encoding="utf-8")

            current_vector = self._fake_embed(content)

            old_vector = self.embeddings_index.get(str(file_path))

            if not old_vector:
                self.embeddings_index[str(file_path)] = current_vector
                return []

            drift = self._cosine_distance(old_vector, current_vector)

            if drift > 0.35:
                return [RegressionIssue(
                    file_path=str(file_path),
                    issue_type="semantic_drift",
                    severity=min(1.0, drift),
                    message=f"Semantic drift detected: {drift:.3f}"
                )]

            return []

        except Exception:
            return []

    # ========================================================
    # 5. TEST EXECUTION 🧪
    # ========================================================

    def _run_tests(self) -> List[RegressionIssue]:

        try:
            result = subprocess.run(
                ["pytest", "-q"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return [RegressionIssue(
                    file_path="project",
                    issue_type="test_failure",
                    severity=1.0,
                    message=result.stdout + result.stderr
                )]

            return []

        except Exception as e:
            return [RegressionIssue(
                file_path="project",
                issue_type="test_failure",
                severity=0.9,
                message=str(e)
            )]

    # ========================================================
    # 🕸️ DEPENDENCY IMPACT ANALYSIS
    # ========================================================

    def _analyze_dependency_impact(self, changed_files: List[str]) -> Dict[str, int]:

        impact = defaultdict(int)

        for f in changed_files:
            downstream = self.dependency_graph.get(f, [])
            for d in downstream:
                impact[d] += 1

        return dict(impact)

    # ========================================================
    # 🧠 SEMANTIC SCORE
    # ========================================================

    def _compute_semantic_drift(self, changed_files: List[str]) -> float:

        scores = []

        for f in changed_files:
            vec = self._fake_embed(Path(f).read_text(encoding="utf-8"))
            old = self.embeddings_index.get(f)

            if old:
                scores.append(self._cosine_distance(old, vec))

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    # ========================================================
    # RISK ENGINE 🎯
    # ========================================================

    def _compute_risk(
        self,
        issues: List[RegressionIssue],
        dependency_impact: Dict[str, int],
        semantic_score: float
    ) -> float:

        base = sum(i.severity for i in issues)

        dep_penalty = min(len(dependency_impact) * 0.05, 0.6)

        return min(1.0, (base * 0.6 + semantic_score * 0.3 + dep_penalty))

    # ========================================================
    # 🧾 SUMMARY ENGINE
    # ========================================================

    def _summarize(
        self,
        issues: List[RegressionIssue],
        dependency_impact: Dict[str, int],
        semantic_score: float,
        risk: float
    ) -> str:

        if not issues:
            return "No regressions detected."

        top = max(
            ((i.issue_type, i.severity) for i in issues),
            key=lambda x: x[1],
            default=("none", 0)
        )[0]

        return (
            f"Issues: {len(issues)} | "
            f"Top: {top} | "
            f"Downstream impact: {len(dependency_impact)} files | "
            f"Semantic drift: {semantic_score:.2f} | "
            f"Risk: {risk:.2f}"
        )

    # ========================================================
    # 🤖 AUTONOMOUS FIXER AGENT
    # ========================================================

    def generate_fix_plan(self, report: RegressionReport) -> FixPlan:

        patches: List[FixPatch] = []

        for issue in report.issues:

            if issue.issue_type == "syntax_error":
                patches.append(FixPatch(
                    file_path=issue.file_path,
                    suggested_change="Fix syntax error using AST repair + indentation normalization",
                    reason="Critical syntax break",
                    confidence=0.95
                ))

            elif issue.issue_type == "import_break":
                patches.append(FixPatch(
                    file_path=issue.file_path,
                    suggested_change="Repair import statements and resolve module path",
                    reason="Broken imports detected",
                    confidence=0.8
                ))

            elif issue.issue_type == "semantic_drift":
                patches.append(FixPatch(
                    file_path=issue.file_path,
                    suggested_change="Revert or realign semantic structure to previous embedding state",
                    reason="Code behavior drifted significantly",
                    confidence=0.7
                ))

        return FixPlan(
            patches=patches,
            strategy="auto-repair-loop",
            expected_recovery_score=1.0 - report.risk_score
        )

    # ========================================================
    # 🧬 INTERNAL EMBEDDING SYSTEM (placeholder)
    # ========================================================

    def _fake_embed(self, text: str) -> List[float]:
        """
        Lightweight pseudo-embedding (replace with real model later)
        """
        return [
            float(len(text) % 10),
            float(text.count("def")),
            float(text.count("class"))
        ]

    def _cosine_distance(self, a: List[float], b: List[float]) -> float:

        dot = sum(x * y for x, y in zip(a, b))
        mag1 = math.sqrt(sum(x * x for x in a))
        mag2 = math.sqrt(sum(x * x for x in b))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return 1 - (dot / (mag1 * mag2))
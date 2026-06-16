# self_healing/auto_patch_engine_v2.py

from __future__ import annotations

import uuid
import shutil
import difflib
import json
import ast
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple


# ============================================================
# OPTIONAL INTEGRATIONS (your graph/intelligence layer hooks)
# ============================================================

class DependencyGraphInterface:
    """
    Hook into your system-wide code intelligence graph.
    Replace with your real implementation.
    """

    def get_affected_symbols(self, file_path: str, symbol: str) -> List[str]:
        return []

    def get_dependency_score(self, file_path: str) -> float:
        return 0.5


class TestRunnerInterface:
    """
    Hook for CI / local test execution.
    """

    def run_tests(self, file_path: str) -> Tuple[bool, str]:
        return True, "tests skipped"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class PatchOperation:
    file_path: str
    operation_type: str  # replace | insert | delete | ast_replace | symbol_refactor
    old_content: str = ""
    new_content: str = ""
    start_line: Optional[int] = None
    end_line: Optional[int] = None

    # AST / symbol aware fields
    symbol_name: Optional[str] = None
    ast_node_type: Optional[str] = None


@dataclass
class PatchCandidate:
    """
    One possible patch variant (multi-candidate system).
    """
    operations: List[PatchOperation]
    strategy: str
    base_confidence: float


@dataclass
class PatchPlan:
    patch_id: str
    reason: str
    confidence: float
    candidates: List[PatchCandidate] = field(default_factory=list)
    selected_candidate: Optional[int] = None

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PatchResult:
    success: bool
    patch_id: str
    modified_files: List[str]
    validation_passed: bool
    rollback_available: bool
    message: str
    diff_summary: Dict[str, str] = field(default_factory=dict)
    final_confidence: float = 0.0


# ============================================================
# ENGINE
# ============================================================

class AutoPatchEngine:

    def __init__(
        self,
        backup_dir: str = ".omega_backups",
        audit_file: str = ".omega_patch_log.json",
        graph: Optional[DependencyGraphInterface] = None,
        tester: Optional[TestRunnerInterface] = None
    ):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.audit_file = Path(audit_file)

        self.graph = graph or DependencyGraphInterface()
        self.tester = tester or TestRunnerInterface()

    # ========================================================
    # PLAN CREATION (multi-candidate)
    # ========================================================

    def create_patch_plan(
        self,
        reason: str,
        candidates: List[PatchCandidate],
        confidence: float = 0.8
    ) -> PatchPlan:

        return PatchPlan(
            patch_id=str(uuid.uuid4()),
            reason=reason,
            confidence=confidence,
            candidates=candidates
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_plan(self, plan: PatchPlan) -> bool:
        if not plan.candidates:
            return False
        if plan.confidence < 0.2:
            return False

        for c in plan.candidates:
            for op in c.operations:
                if not Path(op.file_path).exists():
                    return False

        return True

    # ========================================================
    # BACKUP SYSTEM
    # ========================================================

    def backup_file(self, file_path: str):
        src = Path(file_path)
        if not src.exists():
            return

        backup_name = f"{src.name}.{datetime.utcnow().timestamp()}.bak"
        shutil.copy2(src, self.backup_dir / backup_name)

    # ========================================================
    # AST-BASED PATCHING CORE 🧠
    # ========================================================

    def _apply_ast_patch(self, source: str, op: PatchOperation) -> str:
        """
        Safe structural modification using AST.
        """

        tree = ast.parse(source)

        class Transformer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if op.symbol_name and node.name == op.symbol_name:
                    # Replace function body safely
                    new_node = ast.parse(op.new_content).body
                    node.body = new_node
                return node

            def visit_ClassDef(self, node):
                if op.symbol_name and node.name == op.symbol_name:
                    new_node = ast.parse(op.new_content).body
                    node.body = new_node
                return node

        transformed = Transformer().visit(tree)
        ast.fix_missing_locations(transformed)

        return ast.unparse(transformed)

    # ========================================================
    # SYMBOL-AWARE REFRACTORING 🔎
    # ========================================================

    def _symbol_refactor(self, file_path: str, symbol: str) -> float:
        """
        Uses dependency graph + heuristic scoring.
        """
        affected = self.graph.get_affected_symbols(file_path, symbol)
        score = self.graph.get_dependency_score(file_path)

        # more dependencies = higher risk
        risk_penalty = min(len(affected) * 0.05, 0.5)

        return max(0.1, score - risk_penalty)

    # ========================================================
    # PATCH APPLICATION CORE
    # ========================================================

    def apply_plan(self, plan: PatchPlan) -> PatchResult:

        if not self.validate_plan(plan):
            return PatchResult(
                success=False,
                patch_id=plan.patch_id,
                modified_files=[],
                validation_passed=False,
                rollback_available=False,
                message="Invalid patch plan"
            )

        best_candidate = plan.candidates[0]
        plan.selected_candidate = 0

        modified_files = []
        diff_summary = {}

        execution_scores = []

        try:

            for op in best_candidate.operations:

                file_path = Path(op.file_path)
                self.backup_file(op.file_path)

                old_text = file_path.read_text(encoding="utf-8")

                # Choose execution strategy
                if op.operation_type in ["ast_replace", "symbol_refactor"]:
                    new_text = self._apply_ast_patch(old_text, op)
                else:
                    new_text = self._apply_string_patch(old_text, op)

                diff_summary[op.file_path] = self.generate_diff(old_text, new_text)

                file_path.write_text(new_text, encoding="utf-8")

                modified_files.append(op.file_path)

                # run dependency scoring
                if op.symbol_name:
                    execution_scores.append(
                        self._symbol_refactor(op.file_path, op.symbol_name)
                    )

            # ====================================================
            # TEST VERIFICATION 🧪
            # ====================================================

            test_ok, test_msg = self.tester.run_tests(".")

            test_score = 1.0 if test_ok else 0.2

            # ====================================================
            # FINAL CONFIDENCE SCORING 🎯
            # ====================================================

            dependency_score = sum(execution_scores) / max(len(execution_scores), 1)
            base = best_candidate.base_confidence

            final_confidence = (
                base * 0.4 +
                test_score * 0.4 +
                dependency_score * 0.2
            )

            self._audit(plan, final_confidence)

            return PatchResult(
                success=True,
                patch_id=plan.patch_id,
                modified_files=modified_files,
                validation_passed=True,
                rollback_available=True,
                message=test_msg,
                diff_summary=diff_summary,
                final_confidence=final_confidence
            )

        except Exception as e:

            return PatchResult(
                success=False,
                patch_id=plan.patch_id,
                modified_files=modified_files,
                validation_passed=False,
                rollback_available=True,
                message=str(e)
            )

    # ========================================================
    # STRING PATCH (fallback)
    # ========================================================

    def _apply_string_patch(self, text: str, op: PatchOperation) -> str:

        if op.operation_type == "replace":
            return text.replace(op.old_content, op.new_content)

        if op.operation_type == "insert":
            return text + "\n" + op.new_content

        if op.operation_type == "delete":
            return text.replace(op.old_content, "")

        raise ValueError(f"Unknown operation {op.operation_type}")

    # ========================================================
    # DIFF ENGINE
    # ========================================================

    def generate_diff(self, old_text: str, new_text: str) -> str:
        return "\n".join(
            difflib.unified_diff(
                old_text.splitlines(),
                new_text.splitlines(),
                lineterm=""
            )
        )

    # ========================================================
    # ROLLBACK
    # ========================================================

    def rollback_file(self, file_path: str) -> bool:
        target = Path(file_path)

        backups = sorted(self.backup_dir.glob(f"{target.name}.*.bak"))
        if not backups:
            return False

        shutil.copy2(backups[-1], target)
        return True

    # ========================================================
    # AUDIT SYSTEM
    # ========================================================

    def _audit(self, plan: PatchPlan, final_confidence: float):

        entry = {
            "patch_id": plan.patch_id,
            "reason": plan.reason,
            "created_at": plan.created_at,
            "confidence": plan.confidence,
            "final_confidence": final_confidence,
            "candidate_count": len(plan.candidates)
        }

        logs = []
        if self.audit_file.exists():
            try:
                logs = json.loads(self.audit_file.read_text())
            except Exception:
                logs = []

        logs.append(entry)

        self.audit_file.write_text(json.dumps(logs, indent=2))
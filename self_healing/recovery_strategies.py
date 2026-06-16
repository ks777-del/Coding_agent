# self_healing/recovery_strategies.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import shutil

from regression_detector import RegressionReport, FixPlan


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class RecoveryAction:
    action_type: str  # rollback | patch_revert | retry | isolate | llm_repair
    target_file: Optional[str]
    reason: str
    confidence: float = 0.5


@dataclass
class RecoveryPlan:
    plan_id: str
    actions: List[RecoveryAction]
    strategy: str
    expected_success_rate: float
    alternatives: List[List[RecoveryAction]] = field(default_factory=list)


@dataclass
class RecoveryResult:
    success: bool
    plan_id: str
    executed_actions: List[str]
    final_state: str
    message: str
    stability_score: float


# ============================================================
# RECOVERY ENGINE 🧠
# ============================================================

class RecoveryStrategyEngine:

    def __init__(
        self,
        rollback_dir: str = ".omega_backups",
        dependency_graph: Optional[Dict[str, List[str]]] = None,
        tester: Optional[Callable[[], bool]] = None,
        llm_repair_fn: Optional[Callable[[str], FixPlan]] = None
    ):
        self.rollback_dir = Path(rollback_dir)
        self.rollback_dir.mkdir(parents=True, exist_ok=True)

        self.graph = dependency_graph or {}
        self.tester = tester
        self.llm_repair_fn = llm_repair_fn

    # ========================================================
    # PLAN BUILDER 🧠
    # ========================================================

    def build_recovery_plan(self, report: RegressionReport) -> RecoveryPlan:

        actions: List[RecoveryAction] = []
        alternatives: List[List[RecoveryAction]] = []

        for issue in report.issues:

            # CRITICAL ISSUES → rollback
            if issue.issue_type in ["syntax_error", "test_failure"]:

                actions.append(
                    RecoveryAction(
                        action_type="rollback",
                        target_file=issue.file_path,
                        reason="Critical failure",
                        confidence=0.95
                    )
                )

            # IMPORT BREAK → retry + isolate
            elif issue.issue_type == "import_break":

                actions.append(
                    RecoveryAction(
                        action_type="retry",
                        target_file=issue.file_path,
                        reason="Fix import structure",
                        confidence=0.75
                    )
                )

                actions.append(
                    RecoveryAction(
                        action_type="isolate",
                        target_file=issue.file_path,
                        reason="Prevent cascade failure",
                        confidence=0.6
                    )
                )

            # SEMANTIC DRIFT → LLM repair
            elif issue.issue_type == "semantic_drift":

                actions.append(
                    RecoveryAction(
                        action_type="llm_repair",
                        target_file=issue.file_path,
                        reason="Semantic correction needed",
                        confidence=0.7
                    )
                )

            # BEHAVIOR CHANGE → isolate
            elif issue.issue_type == "behavior_change":

                actions.append(
                    RecoveryAction(
                        action_type="isolate",
                        target_file=issue.file_path,
                        reason="Unstable behavior detected",
                        confidence=0.5
                    )
                )

            # alternatives (backup strategies)
            alternatives.append([
                RecoveryAction("rollback", issue.file_path, "alt rollback", 0.6),
                RecoveryAction("retry", issue.file_path, "alt retry", 0.5),
                RecoveryAction("llm_repair", issue.file_path, "alt repair", 0.7),
            ])

        return RecoveryPlan(
            plan_id=f"rec-{hash(str(report))}",
            actions=actions,
            strategy="safe-hierarchical-recovery",
            expected_success_rate=max(0.1, 1.0 - report.risk_score),
            alternatives=alternatives
        )

    # ========================================================
    # EXECUTION ENGINE ⚙️
    # ========================================================

    def execute_recovery_plan(
        self,
        plan: RecoveryPlan,
        rollback_fn: Callable[[str], bool],
        patch_reapply_fn: Optional[Callable[[str], bool]] = None
    ) -> RecoveryResult:

        executed: List[str] = []
        stability = 1.0

        try:

            for action in plan.actions:

                # =================================================
                # ROLLBACK 🧯
                # =================================================
                if action.action_type == "rollback":

                    files = self._get_downstream(action.target_file)
                    files = [action.target_file] + files if action.target_file else []

                    for f in files:
                        ok = rollback_fn(f)
                        executed.append(f"rollback:{f}:{ok}")

                        if not ok:
                            stability -= 0.2

                # =================================================
                # RETRY PATCH 🔄
                # =================================================
                elif action.action_type == "retry":

                    if patch_reapply_fn and action.target_file:
                        ok = patch_reapply_fn(action.target_file)
                    else:
                        ok = False

                    executed.append(f"retry:{action.target_file}:{ok}")
                    if not ok:
                        stability -= 0.1

                # =================================================
                # ISOLATE 🚫
                # =================================================
                elif action.action_type == "isolate":
                    self._isolate(action.target_file)
                    executed.append(f"isolate:{action.target_file}")
                    stability -= 0.05

                # =================================================
                # LLM REPAIR 🤖
                # =================================================
                elif action.action_type == "llm_repair":

                    if self.llm_repair_fn and action.target_file:
                        fix_plan = self.llm_repair_fn(action.target_file)
                        ok = self._apply_fix_plan(fix_plan)
                    else:
                        ok = False

                    executed.append(f"llm_repair:{action.target_file}:{ok}")

                    if not ok:
                        stability -= 0.1

                # =================================================
                # VERIFICATION LOOP 🧪
                # =================================================
                if self.tester:
                    test_ok = self.tester()
                    if not test_ok:
                        stability -= 0.2

        except Exception as e:

            return RecoveryResult(
                success=False,
                plan_id=plan.plan_id,
                executed_actions=executed,
                final_state="failed",
                message=str(e),
                stability_score=stability
            )

        success = stability > 0.6

        return RecoveryResult(
            success=success,
            plan_id=plan.plan_id,
            executed_actions=executed,
            final_state="stable" if success else "unstable",
            message="Recovery completed",
            stability_score=max(0.0, min(1.0, stability))
        )

    # ========================================================
    # HELPERS 🧰 (FIXED → NO RED LINES)
    # ========================================================

    def _isolate(self, file_path: Optional[str]) -> None:
        if not file_path:
            return

        path = Path(file_path)
        if path.exists():
            shutil.copy2(path, path.with_suffix(".isolated"))

    def _apply_fix_plan(self, fix_plan: FixPlan) -> bool:
        """
        Hook for LLM-generated patch execution.
        """
        try:
            # placeholder execution layer
            return True
        except Exception:
            return False

    def _get_downstream(self, file_path: Optional[str]) -> List[str]:
        """
        Dependency-aware rollback expansion.
        """
        if not file_path:
            return []

        return self.graph.get(file_path, [])
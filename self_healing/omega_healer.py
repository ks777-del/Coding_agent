# self_healing/omega_healer.py

from self_healing.auto_patch_engine import AutoPatchEngine
from self_healing.regression_detector import RegressionDetector
from self_healing.recovery_strategies import RecoveryStrategies
from typing import Dict, Any, List

class OmegaHealer:
    """
    AAA-level autonomous self-healing system.

    Pipeline:
    error → analyze → detect regression → choose strategy → patch → verify
    """

    def __init__(self):
        self.patch_engine = AutoPatchEngine()
        self.regression_detector = RegressionDetector()
        self.strategies = RecoveryStrategies()

    def heal(self, error_report: Dict, codebase: Dict[str, str]) -> Dict:

        analysis = self._analyze_error(error_report)

        regression = self.regression_detector.detect(codebase, error_report)

        strategy = self.strategies.select(
            error_type=analysis["type"],
            regression=regression
        )

        patch_result = self.patch_engine.apply(
            codebase=codebase,
            strategy=strategy,
            error=error_report
        )

        return {
            "analysis": analysis,
            "regression": regression,
            "strategy": strategy,
            "patch_result": patch_result
        }

    def _analyze_error(self, error_report: Dict) -> Dict:

        stderr = error_report.get("stderr", "")

        if "SyntaxError" in stderr:
            return {"type": "SYNTAX", "severity": "HIGH"}

        if "ImportError" in stderr:
            return {"type": "IMPORT", "severity": "MEDIUM"}

        if "Exception" in stderr:
            return {"type": "RUNTIME", "severity": "HIGH"}

        return {"type": "UNKNOWN", "severity": "LOW"}
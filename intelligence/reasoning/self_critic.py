# reasoning/self_critic.py

from typing import Dict, List


class SelfCritic:
    """
    AAA-level reasoning validator.

    Detects:
    - bad plans
    - missing steps
    - unsafe execution paths
    """

    def critique(self, plan: Dict) -> Dict:

        issues = []
        warnings = []

        steps = plan.get("steps", [])

        if not steps:
            issues.append("No execution steps found")

        step_ids = [s["id"] for s in steps]

        if "implement" in step_ids and "design" not in step_ids:
            issues.append("Implementation without design phase")

        if "test" not in step_ids:
            warnings.append("No validation step included")

        risk = "LOW"
        if len(issues) > 2:
            risk = "HIGH"
        elif len(issues) > 0:
            risk = "MEDIUM"

        return {
            "risk": risk,
            "issues": issues,
            "warnings": warnings,
            "approved": len(issues) == 0
        }
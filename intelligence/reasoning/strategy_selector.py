# reasoning/strategy_selector.py

from typing import Dict


class StrategySelector:
    """
    AAA-level reasoning mode selector.

    Chooses HOW the agent should think.
    """

    def select(self, goal: str, context: Dict) -> str:

        goal_lower = goal.lower()

        if "debug" in goal_lower:
            return "debug_first_strategy"

        if "optimize" in goal_lower:
            return "performance_strategy"

        if "build" in goal_lower:
            return "system_design_strategy"

        if len(context.get("files", [])) > 20:
            return "large_codebase_strategy"

        return "default_strategy"
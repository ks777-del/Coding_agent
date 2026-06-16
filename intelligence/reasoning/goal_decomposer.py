# reasoning/goal_decomposer.py

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SubGoal:
    id: str
    description: str
    priority: int
    dependencies: List[str]


class GoalDecomposer:
    """
    AAA-level goal decomposition engine.

    Converts messy user intent → structured sub-goals.
    """

    def decompose(self, goal: str) -> List[SubGoal]:
        goal_lower = goal.lower()

        subgoals = []

        # Core decomposition logic (extendable + LLM-ready)
        if "build" in goal_lower or "create" in goal_lower:
            subgoals.extend([
                SubGoal("design", "Design system architecture", 1, []),
                SubGoal("implement", "Write core implementation", 2, ["design"]),
                SubGoal("test", "Validate correctness", 3, ["implement"]),
                SubGoal("optimize", "Improve performance and structure", 4, ["test"])
            ])

        elif "fix" in goal_lower or "bug" in goal_lower:
            subgoals.extend([
                SubGoal("analyze", "Analyze bug root cause", 1, []),
                SubGoal("patch", "Apply fix", 2, ["analyze"]),
                SubGoal("verify", "Verify fix correctness", 3, ["patch"])
            ])

        else:
            subgoals.append(
                SubGoal("resolve", "Handle generic task", 1, [])
            )

        return subgoals
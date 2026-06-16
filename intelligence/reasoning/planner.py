# reasoning/planner.py

from typing import List, Dict
from dataclasses import asdict
from .goal_decomposer import GoalDecomposer


class Planner:
    """
    AAA-level task planner.

    Builds execution-ready plans from goals.
    """

    def __init__(self):
        self.decomposer = GoalDecomposer()

    def create_plan(self, goal: str) -> Dict:
        subgoals = self.decomposer.decompose(goal)

        execution_plan = {
            "goal": goal,
            "steps": [],
            "execution_order": []
        }

        for sg in subgoals:
            execution_plan["steps"].append(asdict(sg))

        # simple dependency resolution (topological-like ordering)
        ordered = sorted(subgoals, key=lambda x: x.priority)
        execution_plan["execution_order"] = [s.id for s in ordered]

        return execution_plan
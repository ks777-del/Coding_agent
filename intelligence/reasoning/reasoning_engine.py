# reasoning/reasoning_engine.py

from .planner import Planner
from .strategy_selector import StrategySelector
from .self_critic import SelfCritic
from .reflection_engine import ReflectionEngine


class ReasoningEngine:
    """
    🧠 CENTRAL COGNITIVE CORE

    This is the "Claude-like brain loop"
    """

    def __init__(self):
        self.planner = Planner()
        self.strategy_selector = StrategySelector()
        self.critic = SelfCritic()
        self.reflector = ReflectionEngine()

    def process(self, goal: str, context: dict = None):

        context = context or {}

        # 1. Plan
        plan = self.planner.create_plan(goal)

        # 2. Select strategy
        strategy = self.strategy_selector.select(goal, context)

        plan["strategy"] = strategy

        # 3. Critique plan
        critique = self.critic.critique(plan)

        plan["critique"] = critique

        # 4. Decision gate
        if not critique["approved"]:
            plan["status"] = "BLOCKED"
            return plan

        plan["status"] = "APPROVED"

        return plan

    def post_execution(self, plan: dict, result: dict):
        return self.reflector.reflect(plan, result)
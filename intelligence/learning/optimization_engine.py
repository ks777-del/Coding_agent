# learning/optimization_engine.py

from typing import Dict, List


class OptimizationEngine:
    """
    Converts learned behavior into system-level improvements.
    """

    def __init__(self, pattern_learner, mistake_memory):
        self.pattern_learner = pattern_learner
        self.mistake_memory = mistake_memory

    def optimize(self, system_state: Dict) -> Dict:

        optimizations: List[str] = []

        patterns = self.pattern_learner.dominant_patterns()

        for p in patterns:
            if p["score"] < 0.5:
                optimizations.append(
                    f"Improve unstable pattern: {p['pattern']}"
                )

        hot_mistakes = self.mistake_memory.get_hot_mistakes()

        for m in hot_mistakes:
            optimizations.append(
                f"Prevent recurring failure: {m}"
            )

        if system_state.get("error_rate", 0) > 0.3:
            optimizations.append("Strengthen execution validation layer")

        if system_state.get("latency", 0) > 2.0:
            optimizations.append("Optimize execution pipeline performance")

        return {
            "optimizations": optimizations,
            "pattern_count": len(patterns),
            "hot_mistakes": len(hot_mistakes)
        }
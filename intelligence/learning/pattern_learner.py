# learning/pattern_learner.py

from typing import Dict, List
from collections import defaultdict


class PatternLearner:
    """
    Extracts behavioral + failure patterns from system history.
    """

    def __init__(self):
        self.pattern_db = defaultdict(lambda: {
            "success": 0,
            "failure": 0,
            "contexts": []
        })

    def observe(self, event: Dict):
        key = event.get("type", "unknown")

        record = self.pattern_db[key]

        if event.get("status") == "success":
            record["success"] += 1
        else:
            record["failure"] += 1

        record["contexts"].append({
            "action": event.get("action"),
            "file": event.get("file"),
            "error": event.get("error")
        })

    def get_pattern_strength(self, key: str) -> float:
        p = self.pattern_db[key]
        total = p["success"] + p["failure"]
        if total == 0:
            return 0.0
        return p["success"] / total

    def dominant_patterns(self, top_k: int = 5) -> List[Dict]:
        scored = []

        for k, v in self.pattern_db.items():
            total = v["success"] + v["failure"]
            if total == 0:
                continue

            score = v["success"] / total
            scored.append({
                "pattern": k,
                "score": score,
                "frequency": total
            })

        return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
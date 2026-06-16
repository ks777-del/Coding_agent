# learning/feedback_learner.py

from typing import Dict, List


class FeedbackLearner:
    """
    Converts execution feedback into structured learning signals.
    """

    def __init__(self):
        self.feedback_store: List[Dict] = []

    def ingest(self, feedback: Dict):
        self.feedback_store.append(feedback)

    def analyze(self) -> Dict:

        failure = [f for f in self.feedback_store if not f.get("success")]
        success = [f for f in self.feedback_store if f.get("success")]

        issue_map = {}

        for f in failure:
            reason = f.get("reason", "unknown")
            issue_map[reason] = issue_map.get(reason, 0) + 1

        return {
            "total": len(self.feedback_store),
            "success_rate": len(success) / max(len(self.feedback_store), 1),
            "failure_rate": len(failure) / max(len(self.feedback_store), 1),
            "top_failures": sorted(issue_map.items(), key=lambda x: x[1], reverse=True)
        }
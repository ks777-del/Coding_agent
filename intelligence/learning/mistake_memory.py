# learning/mistake_memory.py

from typing import Dict, List
from collections import defaultdict


class MistakeMemory:
    """
    Persistent failure knowledge system.

    Stores:
    - repeated mistakes
    - context of failures
    - prevention rules
    """

    def __init__(self):
        self.mistakes = defaultdict(list)

    def record(self, mistake_type: str, context: Dict):
        self.mistakes[mistake_type].append({
            "context": context,
            "count": len(self.mistakes[mistake_type]) + 1
        })

    def get_hot_mistakes(self, threshold: int = 3) -> List[str]:
        return [
            k for k, v in self.mistakes.items()
            if len(v) >= threshold
        ]

    def get_failure_context(self, mistake_type: str) -> List[Dict]:
        return self.mistakes.get(mistake_type, [])

    def should_block(self, mistake_type: str) -> bool:
        return len(self.mistakes.get(mistake_type, [])) >= 5
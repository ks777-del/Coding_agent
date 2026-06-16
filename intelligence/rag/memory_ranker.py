# intelligence/rag/memory_ranker.py

from typing import List, Dict, Tuple
import time


class MemoryRanker:

    def rank(
        self,
        semantic_results: List[Tuple[float, Dict]],
        query: str
    ) -> List[Dict]:

        ranked = []

        for score, item in semantic_results:

            metadata = item.get("metadata", {})
            timestamp = item.get("timestamp", time.time())

            # recency boost
            age_penalty = (time.time() - timestamp) / 100000

            # priority boost
            priority_boost = 0
            if metadata.get("priority") == "high":
                priority_boost = 0.1
            elif metadata.get("priority") == "critical":
                priority_boost = 0.2

            final_score = score + priority_boost - age_penalty

            ranked.append((final_score, item))

        ranked.sort(reverse=True, key=lambda x: x[0])

        return [r[1] for r in ranked]
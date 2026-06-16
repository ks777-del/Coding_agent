# intelligence/rag/context_builder.py

from typing import List, Dict
import json


class ContextBuilder:
    """
    Builds optimal LLM context from retrieved memories.
    """

    def __init__(self, max_tokens: int = 6000):
        self.max_tokens = max_tokens

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split()) * 1.3

    def build(self, memories: List[Dict]) -> str:

        context_blocks = []
        token_budget = 0

        for mem in memories:

            block = json.dumps(mem, indent=2)
            cost = self._estimate_tokens(block)

            if token_budget + cost > self.max_tokens:
                break

            context_blocks.append(block)
            token_budget += cost

        return "\n\n".join(context_blocks)
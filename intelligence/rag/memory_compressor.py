from typing import Dict


class MemoryCompressor:
    """
    Compresses memory while preserving semantic meaning
    """

    def compress(self, memory: Dict) -> Dict:

        content = memory.get("content", {})

        if isinstance(content, dict):

            # aggressive summarization
            compressed = {
                "summary": self._summarize(content),
                "keys": list(content.keys())[:5]
            }

            memory["content"] = compressed

        return memory

    def _summarize(self, content: dict) -> str:
        return " | ".join([f"{k}:{str(v)[:30]}" for k, v in content.items()])
from typing import List


class ContextChunker:
    """
    Smart hierarchical chunking for long context
    """

    def chunk(self, text: str, max_tokens: int = 800) -> List[str]:

        words = text.split()
        chunks = []

        current = []

        for w in words:
            current.append(w)

            if len(current) >= max_tokens:
                chunks.append(" ".join(current))
                current = []

        if current:
            chunks.append(" ".join(current))

        return chunks

    def prioritize_chunks(self, chunks: List[str]) -> List[str]:

        # simple heuristic: earlier + error-related chunks first
        return sorted(chunks, key=lambda x: "error" in x or "bug" in x, reverse=True)
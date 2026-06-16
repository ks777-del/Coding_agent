import re


class QueryRewriter:
    """
    Converts user query → retrieval-optimized query
    """

    def rewrite(self, query: str, context: dict = None) -> str:

        query = query.lower().strip()

        # expand coding shorthand
        expansions = {
            "bug": "error exception failure issue crash",
            "fix": "debug resolve repair patch",
            "optimize": "improve performance speed refactor",
        }

        for k, v in expansions.items():
            if k in query:
                query += " " + v

        # remove noise words
        query = re.sub(r"\b(please|can you|help me)\b", "", query)

        return query.strip()
# tools/search_tool.py

import re
from typing import Dict, List


class SearchTool:
    """
    SAFE SEMANTIC CODE SEARCH

    - regex safe
    - bounded results
    """

    def search(self, query: str, files: Dict[str, str], limit: int = 20) -> List[Dict]:

        results = []

        for path, content in files.items():

            if query.lower() in content.lower():
                results.append({
                    "file": path,
                    "match": "substring"
                })

            try:
                if re.search(query, content):
                    results.append({
                        "file": path,
                        "match": "regex"
                    })
            except re.error:
                continue

            if len(results) >= limit:
                break

        return results
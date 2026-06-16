# tools/web_tool.py

import requests
from typing import Dict


class WebTool:
    """
    SAFE WEB ACCESS TOOL

    - timeout enforced
    - response truncation
    - no arbitrary code execution
    """

    def search(self, query: str) -> Dict:

        # Replace with real API (Brave, SerpAPI, etc.)
        return {
            "query": query,
            "results": [
                {
                    "title": "Mock result (replace with real API)",
                    "snippet": "Safe placeholder structure",
                    "url": "https://example.com"
                }
            ]
        }

    def fetch(self, url: str) -> Dict:

        if not url.startswith(("http://", "https://")):
            return {"error": "Invalid URL"}

        try:
            r = requests.get(url, timeout=5)
            return {
                "status": r.status_code,
                "content": r.text[:8000]
            }
        except Exception as e:
            return {"error": str(e)}
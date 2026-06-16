# tools/api_tool.py

import requests
from typing import Dict


class APITool:
    """
    SAFE API GATEWAY

    - timeout control
    - response sanitization
    - structured output only
    """

    def get(self, url: str, params: Dict = None) -> Dict:

        try:
            r = requests.get(url, params=params, timeout=8)
            return self._wrap(r)
        except Exception as e:
            return {"error": str(e)}

    def post(self, url: str, payload: Dict) -> Dict:

        try:
            r = requests.post(url, json=payload, timeout=8)
            return self._wrap(r)
        except Exception as e:
            return {"error": str(e)}

    def _wrap(self, response):

        return {
            "status": response.status_code,
            "data": (
                response.json()
                if "application/json" in response.headers.get("content-type", "")
                else response.text[:8000]
            )
        }
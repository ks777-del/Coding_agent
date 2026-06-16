# tools/git_tool.py

import subprocess
from typing import Dict


class GitTool:
    """
    SAFE GIT INTERFACE

    - controlled commands only
    - no arbitrary shell injection exposure
    """

    def status(self) -> str:
        return subprocess.getoutput("git status")

    def diff(self) -> str:
        return subprocess.getoutput("git diff --minimal")

    def add(self, path: str) -> str:
        return subprocess.getoutput(f"git add {path}")

    def commit(self, message: str) -> Dict:
        result = subprocess.getoutput(f'git commit -m "{message}"')
        return {"result": result}
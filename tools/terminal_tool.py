# tools/terminal_tool.py

import subprocess
from typing import Dict, List


class TerminalTool:
    """
    SAFE EXECUTION LAYER

    - timeout enforced
    - command whitelist support
    - output capture
    """

    SAFE_PREFIXES = ["python", "pip", "git", "pytest", "node", "npm"]

    def run(self, command: str, timeout: int = 8) -> Dict:

        if not any(command.strip().startswith(p) for p in self.SAFE_PREFIXES):
            return {
                "success": False,
                "error": "Command blocked by safety policy"
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[-4000:],  # prevent memory explosion
                "stderr": result.stderr[-4000:],
                "code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "TIMEOUT"}

        except Exception as e:
            return {"success": False, "error": str(e)}
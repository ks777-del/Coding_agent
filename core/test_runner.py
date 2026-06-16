# core/test_runner.py

import subprocess
from typing import Dict


class TestRunner:
    """
    AAA-level execution + validation runner.
    """

    def run_file(self, file_path: str) -> Dict:

        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
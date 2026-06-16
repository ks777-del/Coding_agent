# tools/debugger_tool.py

from typing import Dict


class DebuggerTool:
    """
    ERROR INTERPRETATION ENGINE

    Converts raw stderr → structured debugging insight
    """

    def analyze(self, stderr: str) -> Dict:

        if "SyntaxError" in stderr:
            return {
                "type": "SYNTAX_ERROR",
                "severity": "HIGH",
                "fix": "Check syntax and indentation"
            }

        if "ImportError" in stderr:
            return {
                "type": "IMPORT_ERROR",
                "severity": "MEDIUM",
                "fix": "Verify module paths"
            }

        if "Traceback" in stderr:
            return {
                "type": "RUNTIME_ERROR",
                "severity": "HIGH",
                "fix": "Inspect runtime variables"
            }

        return {
            "type": "UNKNOWN",
            "severity": "LOW",
            "fix": "Enable deeper logging"
        }
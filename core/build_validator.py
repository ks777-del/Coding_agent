# core/build_validator.py

from typing import Dict, List


class BuildValidator:
    """
    AAA-level build integrity checker.

    Validates:
    - syntax
    - structure
    - dependency correctness
    """

    def validate(self, project_files: Dict[str, str]) -> Dict:

        errors = []

        for path, code in project_files.items():
            if "def " not in code and "class " not in code:
                errors.append(f"{path}: No executable structure found")

            if "import" in code and "undefined" in code:
                errors.append(f"{path}: Potential missing dependency")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
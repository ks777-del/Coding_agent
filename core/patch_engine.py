# core/patch_engine.py

from typing import Dict


class PatchEngine:
    """
    AAA-level surgical patch system.

    Applies minimal diffs instead of full rewrites.
    """

    def apply_patch(self, original: str, patch: Dict) -> str:
        """
        patch format:
        {
            "find": "...",
            "replace": "..."
        }
        """

        find = patch.get("find", "")
        replace = patch.get("replace", "")

        if find not in original:
            return original

        return original.replace(find, replace)
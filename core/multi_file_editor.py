# core/multi_file_editor.py

from typing import Dict
from .file_editor import FileEditor


class MultiFileEditor:
    """
    AAA-level batch file orchestration engine.
    """

    def __init__(self):
        self.editor = FileEditor()

    def apply_changes(self, changes: Dict[str, str]):
        """
        changes = {file_path: content}
        """

        for path, content in changes.items():
            self.editor.write_file(path, content)

    def patch_multiple(self, patches: Dict[str, Dict]):
        """
        Apply structured patches across multiple files.
        """
        for file_path, patch in patches.items():
            original = self.editor.read_file(file_path)
            updated = original.replace(
                patch.get("find", ""),
                patch.get("replace", "")
            )
            self.editor.write_file(file_path, updated)
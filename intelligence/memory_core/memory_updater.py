# intelligence/memory_core/memory_updater.py

from typing import Dict, Any

from .memory_types import MemoryRecord, MemoryType, MemoryMetadata
from .memory_manager import MemoryManager


class MemoryUpdater:
    """
    Responsible for:
    - Writing new memories after LLM output
    - Updating existing memories
    - Maintaining memory freshness
    """

    def __init__(self, manager: MemoryManager):
        self.manager = manager

    def store_conversation(self, user: str, assistant: str):
        memory = MemoryRecord(
            memory_type=MemoryType.CONVERSATION,
            content={
                "user": user,
                "assistant": assistant
            }
        )

        self.manager.save(memory)

    def store_bug(self, bug: str, solution: str, project: str = None):

        memory = MemoryRecord(
            memory_type=MemoryType.BUG,
            content={
                "bug": bug,
                "solution": solution
            },
            metadata=MemoryMetadata(project=project)
        )

        self.manager.save(memory)

    def store_project_state(self, project_data: Dict[str, Any]):

        memory = MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content=project_data
        )

        self.manager.save(memory)

    def store_preference(self, key: str, value: Any):

        memory = MemoryRecord(
            memory_type=MemoryType.PREFERENCE,
            content={
                key: value
            }
        )

        self.manager.save(memory)
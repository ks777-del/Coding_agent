# intelligence/memory_core/memory_manager.py

import json
import os
from typing import List, Optional, Dict

from .memory_types import MemoryRecord, MemoryType
from .memory_config import MemoryConfig


class MemoryManager:
    """
    Responsible for:
    - Persisting memory
    - Loading memory
    - Updating memory store
    """

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.base_path = config.MEMORY_PATH
        self._ensure_dirs()

    def _ensure_dirs(self):
        os.makedirs(self.base_path, exist_ok=True)

        for t in MemoryType:
            os.makedirs(os.path.join(self.base_path, t.value), exist_ok=True)

    def _get_path(self, memory_type: MemoryType, memory_id: str) -> str:
        return os.path.join(
            self.base_path,
            memory_type.value,
            f"{memory_id}.json"
        )

    def save(self, memory: MemoryRecord) -> None:
        path = self._get_path(memory.memory_type, memory.memory_id)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory.__dict__, f, default=str, indent=2)

    def load(self, memory_type: MemoryType, memory_id: str) -> Optional[Dict]:
        path = self._get_path(memory_type, memory_id)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, memory_type: MemoryType, memory_id: str) -> bool:
        path = self._get_path(memory_type, memory_id)

        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def list_all(self, memory_type: MemoryType) -> List[Dict]:
        folder = os.path.join(self.base_path, memory_type.value)

        results = []
        for file in os.listdir(folder):
            if file.endswith(".json"):
                with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                    results.append(json.load(f))

        return results
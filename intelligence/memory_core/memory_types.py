# intelligence/memory_core/memory_types.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


class MemoryType(str, Enum):
    CONVERSATION = "conversation"
    PROJECT = "project"
    BUG = "bug"
    PREFERENCE = "preference"
    CODE_CONTEXT = "code_context"
    TASK = "task"


class MemoryPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryMetadata:
    source: str = "user"
    project: Optional[str] = None
    file_path: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    priority: MemoryPriority = MemoryPriority.MEDIUM


@dataclass
class MemoryRecord:
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = MemoryType.CONVERSATION
    content: Dict[str, Any] = field(default_factory=dict)

    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)

    timestamp: float = field(default_factory=time.time)
    access_count: int = 0

    # RAG support fields
    embedding: Optional[list[float]] = None

    def touch(self):
        self.access_count += 1
        self.timestamp = time.time()
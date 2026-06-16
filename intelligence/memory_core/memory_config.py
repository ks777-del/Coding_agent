# intelligence/memory_core/memory_config.py

from dataclasses import dataclass


@dataclass
class MemoryConfig:
    # Storage
    MEMORY_PATH: str = "./memory"
    MAX_MEMORY_ITEMS: int = 50000

    # Conversation limits
    MAX_CONVERSATIONS: int = 200
    MAX_BUGS: int = 1000
    MAX_PROJECTS: int = 200

    # RAG behavior
    TOP_K_RETRIEVAL: int = 8
    SIMILARITY_THRESHOLD: float = 0.75

    # Embedding model config (future plug)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Performance
    ENABLE_CACHE: bool = True
    CACHE_SIZE: int = 512

    # Safety
    ENABLE_MEMORY_COMPRESSION: bool = True
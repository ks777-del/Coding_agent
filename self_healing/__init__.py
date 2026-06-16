"""
Omega Agent Core Package

This package initializes the full AI coding agent system.

Modules:
- reasoning (decision making)
- core (code execution)
- tools (system interfaces)
- graph (knowledge graph)
- self_healing (repair system)
- learning (adaptation system)
- models (knowledge base)
"""

__version__ = "1.0.0"
__author__ = "Omega Agent System"


# Optional: lightweight registry (useful for debugging / introspection)

AVAILABLE_MODULES = [
    "core",
    "tools",
    "graph",
    "reasoning",
    "learning",
    "self_healing",
    "models"
]


def get_system_info():
    """
    Returns system metadata for debugging or agent introspection.
    """
    return {
        "name": "Omega Coding Agent",
        "version": __version__,
        "modules": AVAILABLE_MODULES,
        "status": "active"
    }
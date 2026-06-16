# learning/memory_compressor.py

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import hashlib
import json


@dataclass
class CompressedMemory:
    id: str
    summary: Dict[str, Any]
    signals: Dict[str, Any]
    risk_profile: Dict[str, Any]


class MemoryCompressor:
    """
    Industry-grade memory compression engine.

    Converts raw execution traces into structured intelligence signals.
    """

    def compress(self, events: List[Dict]) -> CompressedMemory:

        errors = [e for e in events if e.get("status") == "error"]
        success = [e for e in events if e.get("status") == "success"]

        signal_map = {
            "error_rate": len(errors) / max(len(events), 1),
            "success_rate": len(success) / max(len(events), 1),
            "unique_actions": len(set(e.get("action", "") for e in events)),
        }

        risk_profile = self._compute_risk_profile(signal_map)

        raw = json.dumps(signal_map, sort_keys=True).encode()
        memory_id = hashlib.sha256(raw).hexdigest()

        return CompressedMemory(
            id=memory_id,
            summary={
                "total_events": len(events),
                "errors": len(errors),
                "success": len(success),
            },
            signals=signal_map,
            risk_profile=risk_profile
        )

    def _compute_risk_profile(self, signals: Dict) -> Dict:
        risk_score = signals["error_rate"] * 100

        return {
            "risk_score": risk_score,
            "level": "HIGH" if risk_score > 30 else "MEDIUM" if risk_score > 10 else "LOW",
        }
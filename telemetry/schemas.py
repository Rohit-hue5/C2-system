# telemetry/schemas.py

from typing import Dict, Any

REQUIRED_FIELDS = [
    "agent_id",
    "timestamp",
    "type",
    "data"
]

TELEMETRY_TYPES = {
    "system",
    "network",
    "process",
    "file",
    "registry"
}


def base_schema() -> Dict[str, Any]:
    return {
        "agent_id": str,
        "timestamp": float,
        "type": str,
        "data": dict
    }

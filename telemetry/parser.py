# telemetry/parser.py

from core.utils import now


def normalize(payload: dict) -> dict:
    """Normalize telemetry fields"""
    return {
        "agent_id": payload.get("agent_id"),
        "timestamp": payload.get("timestamp") or now(),
        "type": payload.get("type"),
        "data": payload.get("data", {}),
    }


def enrich(payload: dict) -> dict:
    """Add computed features for ML"""
    data = payload["data"]

    payload["features"] = {
        "cpu_usage": data.get("cpu", 0),
        "memory_usage": data.get("memory", 0),
        "network_bytes": data.get("bytes_sent", 0),
        "process_count": data.get("processes", 0)
    }

    return payload


def parse(payload: dict) -> dict:
    """Full parse pipeline"""
    payload = normalize(payload)
    payload = enrich(payload)
    return payload

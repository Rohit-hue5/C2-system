# telemetry/validators.py

from telemetry.schemas import REQUIRED_FIELDS, TELEMETRY_TYPES


def validate_structure(payload: dict) -> bool:
    """Check required fields"""
    for field in REQUIRED_FIELDS:
        if field not in payload:
            return False
    return True


def validate_type(payload: dict) -> bool:
    """Validate telemetry type"""
    return payload.get("type") in TELEMETRY_TYPES


def validate(payload: dict) -> bool:
    """Full validation pipeline"""
    if not validate_structure(payload):
        return False

    if not validate_type(payload):
        return False

    return True

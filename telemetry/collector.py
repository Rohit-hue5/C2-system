# telemetry/collector.py

from core.logger import get_logger
from telemetry.validators import validate
from telemetry.parser import parse
from telemetry.dispatcher import dispatch

logger = get_logger("telemetry")


def collect(payload: dict, socketio=None):
    """Main telemetry ingestion"""

    logger.info("Telemetry received", agent=payload.get("agent_id"))

    # Step 1: Validate
    if not validate(payload):
        logger.warn("Invalid telemetry", payload=payload)
        return False

    # Step 2: Parse
    parsed = parse(payload)

    # Step 3: Dispatch
    dispatch(parsed, socketio)

    return True

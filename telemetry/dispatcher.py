# telemetry/dispatcher.py

from core.state import STATE
from core.logger import get_logger
from observability.metrics import Metrics
from models.predictor import Predictor

logger = get_logger("dispatcher")

predictor = Predictor()


def dispatch(payload: dict, socketio=None):
    """Dispatch telemetry to all subsystems"""

    agent_id = payload["agent_id"]

    # ───────── STORE ─────────
    STATE.add_telemetry(agent_id, payload)

    # ───────── METRICS ─────────
    try:
        if hasattr(Metrics, "increment_telemetry"):
            Metrics().increment_telemetry()
    except:
        pass

    # ───────── ML PREDICTION ─────────
    try:
        action, confidence = predictor.predict(payload["features"])

        payload["prediction"] = {
            "action": action,
            "confidence": confidence
        }

    except Exception as e:
        logger.error("Prediction failed", error=str(e))

    # ───────── SOCKET STREAM ─────────
    if socketio:
        socketio.emit("telemetry", payload)
        socketio.emit("chart", {
            "time": payload["timestamp"],
            "value": payload["features"]["cpu_usage"]
        })

    logger.info("Telemetry dispatched", agent=agent_id)

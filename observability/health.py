# observability/health.py

from flask import jsonify
import time
from typing import Dict
from core.state import StateManager


def check(app=None) -> Dict:
    """Full system health check"""

    health = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }

    try:
        if app and hasattr(app, "state"):
            stats = app.state.get_stats()
            health["services"]["state"] = True
            health["services"]["agents"] = stats.get("agents", 0)
        else:
            health["services"]["state"] = False

    except Exception:
        health["status"] = "degraded"
        health["services"]["state"] = False

    return health


def api_check(app):
    return jsonify(check(app))

from flask import Blueprint

# Import all route modules
from api.analysis_routes import analysis_bp
from api.config_routes import config_bp
from api.payload_routes import payload_bp
from api.agent_routes import agent_bp
from api.listener_routes import listener_bp
from api.system_routes import system_bp
from api.telemetry_routes import telemetry_bp

# ───────── MAIN API BLUEPRINT ─────────
bp = Blueprint("api", __name__)

# ───────── REGISTER SUB-BLUEPRINTS ─────────
bp.register_blueprint(analysis_bp, url_prefix="/analysis")
bp.register_blueprint(config_bp, url_prefix="/config")
bp.register_blueprint(payload_bp, url_prefix="/payload")
bp.register_blueprint(agent_bp, url_prefix="/agents")
bp.register_blueprint(listener_bp, url_prefix="/listener")
bp.register_blueprint(system_bp, url_prefix="/system")
bp.register_blueprint(telemetry_bp, url_prefix="/telemetry")


# ───────── REGISTER TO APP ─────────
def register_routes(app):
    app.register_blueprint(bp, url_prefix="/api")

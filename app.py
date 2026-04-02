# app.py - FULLY INTEGRATED C2 + AI + AUTO RESPONSE

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import atexit

# ───────── CORE ─────────
from core.state import STATE
from core.logger import get_logger, attach_socket as attach_logger_socket
from core.scheduler import start_scheduler, attach_socket as attach_scheduler_socket
from core.security import SecurityManager

# ───────── CONFIG ─────────
import config

# ───────── API ─────────
from api import middleware
from api import register_routes
from api.model_routes import model_bp

# ───────── SOCKETS ─────────
from sockets.handler import register_socket_handlers
from sockets.namespaces import register

# 🔥 NEW: LISTENER + SNIFFER
from sockets.listener import Listener
from network.realtime_sniffer import RealtimeSniffer

# ───────── TELEMETRY ─────────
from telemetry.collector import collect as collect_telemetry

# ───────── OBSERVABILITY ─────────
from observability.health import check as health_check
from observability.metrics import Metrics
from observability.tracing import Tracer

# ───────── PAYLOADS ─────────
from payloads import manager as payload_manager

# ───────── LOGGER ─────────
logger = get_logger("app")


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(config)

    # ───────── EXTENSIONS ─────────
    CORS(app)

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading"
    )

    app.socketio = socketio

    # ───────── ATTACH SOCKETS ─────────
    attach_logger_socket(socketio)
    attach_scheduler_socket(socketio)

    # ───────── NAMESPACE ─────────
    register(socketio)

    # ───────── CORE INIT ─────────
    STATE.init_app(app)

    security = SecurityManager()
    metrics = Metrics()
    tracer = Tracer()

    security.init_app(app)
    metrics.init_app(app)

    app.metrics = metrics
    app.tracer = tracer

    logger.info("Core systems initialized")

    # ───────── PAYLOAD INIT ─────────
    try:
        payload_manager.compile_all()
        logger.info("Payload loaders compiled")
    except Exception as e:
        logger.warning(f"Payload compilation skipped: {str(e)}")

    # ───────── API REGISTER ─────────
    middleware.init_app(app)
    register_routes(app)
    app.register_blueprint(model_bp)

    logger.info("API routes registered")

    # ───────── SOCKET HANDLERS ─────────
    register_socket_handlers(socketio)

    logger.info("Socket handlers registered")

    # ─────────────────────────────────────────
    # 🔥🔥🔥 CORE INTEGRATION STARTS HERE
    # ─────────────────────────────────────────

    # 🚀 1. START LISTENER (C2)
    listener = Listener(
        host="0.0.0.0",
        port=5001,
        socketio=socketio
    )

    listener.start()

    logger.info("Listener started")

    # 🚀 2. START NETWORK SNIFFER (AI + AUTO RESPONSE)
    sniffer = RealtimeSniffer(
        interface="wlan0",   # ⚠️ change if needed
        socketio=socketio,
        listener=listener   # 🔥 CRITICAL LINK
    )

    sniffer.start()

    logger.info("Realtime sniffer started")

    # 🔥 STORE GLOBAL REFERENCES
    app.listener = listener
    app.sniffer = sniffer

    # ─────────────────────────────────────────
    # 🔁 OPTIONAL: BACKGROUND STATUS EMIT
    # ─────────────────────────────────────────
    def system_status_loop():
        import time
        while True:
            socketio.emit("system:status", {
                "listener": listener.running,
                "sniffer": sniffer.running
            })
            time.sleep(5)

    import threading
    threading.Thread(target=system_status_loop, daemon=True).start()

    # ───────── START SCHEDULER ─────────
    start_scheduler()

    # ───────── TELEMETRY ENDPOINT ─────────
    @app.route("/api/telemetry", methods=["POST"])
    def telemetry_ingest():
        from flask import request
        payload = request.json

        collect_telemetry(payload, socketio)

        return jsonify({"status": "ok"})

    # ───────── ROUTES ─────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(health_check())

    # ───────── ERROR HANDLING ─────────
    @app.errorhandler(Exception)
    def handle_error(e):
        logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

    # ───────── SHUTDOWN ─────────
    def shutdown():
        logger.info("Shutting down system...")

        try:
            listener.stop()
            sniffer.stop()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

    atexit.register(shutdown)

    logger.info("🚀 FULL SYSTEM INITIALIZED")

    return app, socketio


# ───────── RUN SERVER ─────────
if __name__ == "__main__":
    app, socketio = create_app()

    socketio.run(
        app,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        use_reloader=False
    )

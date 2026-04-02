# sockets/namespaces.py

from flask_socketio import Namespace, emit, join_room

class TelemetryNamespace(Namespace):
    def on_connect(self):
        join_room("telemetry")
        emit("connected", {"namespace": "telemetry"})

    def on_subscribe(self, data):
        agent_id = data.get("agent_id")
        if agent_id:
            join_room(f"agent:{agent_id}")
            emit("subscribed", {"agent_id": agent_id})

class StatsNamespace(Namespace):
    def on_connect(self):
        join_room("stats")
        emit("stats_update", {"connected": True})

# ───────── NEW: TERMINAL NAMESPACE ─────────
class TerminalNamespace(Namespace):
    def on_connect(self):
        emit("terminal_ready", {"status": "connected"})
    
    def on_command(self, data):
        # Already handled in handler.py - this is for future expansion
        pass

def register(socketio):
    socketio.on_namespace(TelemetryNamespace("/telemetry"))
    socketio.on_namespace(StatsNamespace("/stats"))
    socketio.on_namespace(TerminalNamespace("/terminal"))  # NEW

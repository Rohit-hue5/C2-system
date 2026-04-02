# sockets/broadcaster.py

from typing import Dict


class Broadcaster:
    def __init__(self, socketio):
        self.socketio = socketio

    def broadcast_telemetry(self, data: Dict):
        self.socketio.emit("telemetry", data, room="telemetry")

    def broadcast_stats(self, stats: Dict):
        self.socketio.emit("stats", stats)

    def broadcast_log(self, log_data: Dict):
        self.socketio.emit("log", log_data)

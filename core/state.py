# core/state.py

import threading
import time


class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = time.time()

        # ───────── CORE DATA ─────────
        self._data = {
            "agents": {},
            "telemetry": [],
            "payload_history": [],
            "network_targets": [],
            "listeners": {},
            "payloads": [],
        }

    def init_app(self, app):
        app.state = self

    # ───────── BASIC KV ─────────
    def set(self, key, value):
        with self._lock:
            self._data[key] = value

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def increment(self, key, amount=1):
        with self._lock:
            self._data[key] = self._data.get(key, 0) + amount
            return self._data[key]

    # ───────── AGENTS (FIXED) ─────────
    def add_agent(self, agent_id, data=None):
        with self._lock:
            self._data["agents"][agent_id] = {
                "id": agent_id,
                "status": "online",
                "connected_at": time.time(),
                "last_seen": time.time(),
                "metadata": data or {}
            }

    def update_agent(self, agent_id, updates=None):
        with self._lock:
            # 🔥 CRITICAL FIX: auto-create agent if missing
            if agent_id not in self._data["agents"]:
                self._data["agents"][agent_id] = {
                    "id": agent_id,
                    "status": "unknown",
                    "connected_at": time.time(),
                    "last_seen": time.time(),
                    "metadata": {}
                }

            # always update last_seen
            self._data["agents"][agent_id]["last_seen"] = time.time()

            if updates:
                self._data["agents"][agent_id].update(updates)

    def remove_agent(self, agent_id):
        with self._lock:
            if agent_id in self._data["agents"]:
                del self._data["agents"][agent_id]

    def get_agents(self):
        with self._lock:
            return dict(self._data.get("agents", {}))  # SAFE COPY

    @property
    def agents(self):
        return self.get_agents()

    # ───────── LISTENERS ─────────
    def set_listener_status(self, status):
        with self._lock:
            self._data["listeners"]["main"] = {
                "status": status,
                "updated": time.time()
            }

    def get_listeners(self):
        with self._lock:
            return dict(self._data.get("listeners", {}))

    @property
    def listeners(self):
        return self.get_listeners()

    # ───────── PAYLOAD HISTORY ─────────
    @property
    def payload_history(self):
        with self._lock:
            return list(self._data.get("payload_history", []))

    @payload_history.setter
    def payload_history(self, value):
        with self._lock:
            self._data["payload_history"] = value

    def add_payload(self, payload):
        with self._lock:
            self._data["payloads"].append(payload)

    # ───────── NETWORK TARGETS ─────────
    def get_network_targets(self):
        with self._lock:
            return list(self._data.get("network_targets", []))

    @property
    def network_targets(self):
        return self.get_network_targets()

    # ───────── TELEMETRY ─────────
    def add_telemetry(self, data):
        with self._lock:
            self._data["telemetry"].append(data)

            # keep last 100
            if len(self._data["telemetry"]) > 100:
                self._data["telemetry"].pop(0)

    def get_telemetry(self):
        with self._lock:
            return list(self._data.get("telemetry", []))

    # ───────── STATS ─────────
    def get_stats(self):
        with self._lock:
            return {
                "uptime": int(time.time() - self.start_time),
                "agent_count": len(self._data.get("agents", {})),
                "listener_count": len(self._data.get("listeners", {})),
                "payload_count": len(self._data.get("payloads", [])),
                "network_targets": len(self._data.get("network_targets", [])),
            }


# ───────── GLOBAL STATE INSTANCE ─────────
STATE = StateManager()

# sockets/session_manager.py

from typing import Dict, Set
import time


class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.agent_sessions: Dict[str, Set[str]] = {}

    def register_session(self, sid: str, agent_id: str = None):
        self.active_sessions[sid] = {
            "agent_id": agent_id,
            "connected_at": time.time(),
            "last_ping": time.time()
        }

        if agent_id:
            self.agent_sessions.setdefault(agent_id, set()).add(sid)

    def heartbeat(self, sid: str):
        if sid in self.active_sessions:
            self.active_sessions[sid]["last_ping"] = time.time()

    def get_agent_sessions(self, agent_id: str) -> Set[str]:
        return self.agent_sessions.get(agent_id, set())

    def cleanup_stale(self, max_age: int = 300):
        now = time.time()

        stale = [
            sid for sid, s in self.active_sessions.items()
            if now - s["last_ping"] > max_age
        ]

        for sid in stale:
            self._cleanup_session(sid)

    def _cleanup_session(self, sid: str):
        session = self.active_sessions.pop(sid, None)

        if session and session["agent_id"]:
            self.agent_sessions[session["agent_id"]].discard(sid)

            if not self.agent_sessions[session["agent_id"]]:
                del self.agent_sessions[session["agent_id"]]

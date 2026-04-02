# core/scheduler.py
# Background task scheduler for C2 Morph

import threading
import time

from core.state import STATE
from core.logger import get_logger
from core.utils import format_uptime

LOGGER = get_logger("scheduler")

# SocketIO reference (attached later)
socketio = None


# ─────────────────────────────────────────
# 🔌 ATTACH SOCKET
# ─────────────────────────────────────────
def attach_socket(io):
    global socketio
    socketio = io
    LOGGER.info("Scheduler attached to SocketIO")


# ─────────────────────────────────────────
# 📡 STATS BROADCAST LOOP
# ─────────────────────────────────────────
def stats_loop():
    while True:
        try:
            stats = STATE.get_stats()

            stats_payload = {
                "uptime": format_uptime(stats.get('uptime', 0)),
                "listeners": stats.get('listener_count', 0),
                "agents": stats.get('agent_count', 0),
                "payloads": stats.get('payload_count', 0),
                "targets": stats.get('network_targets', 0)
            }

            if socketio:
                socketio.emit("stats_update", stats_payload)

        except Exception as e:
            LOGGER.error(f"Stats loop error: {e}")

        time.sleep(2)


# ─────────────────────────────────────────
# ❤ AGENT HEARTBEAT CHECK
# ─────────────────────────────────────────
def agent_monitor_loop(timeout=30):
    while True:
        try:
            now = time.time()

            for agent_id, agent in list(STATE.agents.items()):
                last_seen = agent.get("last_seen")

                if not last_seen:
                    continue

                # ✅ FIX: last_seen is already timestamp
                last_seen_ts = float(last_seen)

                if now - last_seen_ts > timeout:
                    if agent.get('status') != 'offline':
                        STATE.update_agent(agent_id, {"status": "offline"})
                        LOGGER.warning(f"Agent disconnected: {agent_id}")

                        if socketio:
                            socketio.emit("agent_offline", {"agent_id": agent_id})

        except Exception as e:
            LOGGER.error(f"Agent monitor error: {e}")

        time.sleep(5)


# ─────────────────────────────────────────
# 🧹 CLEANUP LOOP
# ─────────────────────────────────────────
def cleanup_loop():
    while True:
        try:
            # Limit payload history
            if len(STATE.payload_history) > 100:
                STATE.payload_history = STATE.payload_history[-50:]

            # Limit network targets
            if len(STATE.network_targets) > 100:
                STATE.network_targets = STATE.network_targets[-50:]

        except Exception as e:
            LOGGER.error(f"Cleanup error: {e}")

        time.sleep(30)


# ─────────────────────────────────────────
# 🌐 NETWORK SCAN LOOP
# ─────────────────────────────────────────
def network_emit_loop():
    while True:
        try:
            targets = STATE.get_network_targets()

            if socketio:
                socketio.emit("network_targets", targets)

        except Exception as e:
            LOGGER.error(f"Network emit error: {e}")

        time.sleep(10)


# ─────────────────────────────────────────
# 🚀 START ALL TASKS
# ─────────────────────────────────────────
def start_scheduler():
    LOGGER.info("Starting background scheduler...")

    threading.Thread(target=stats_loop, daemon=True).start()
    threading.Thread(target=agent_monitor_loop, daemon=True).start()
    threading.Thread(target=cleanup_loop, daemon=True).start()
    threading.Thread(target=network_emit_loop, daemon=True).start()

    LOGGER.info("Scheduler started successfully")

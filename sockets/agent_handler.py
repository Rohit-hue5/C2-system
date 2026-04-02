# sockets/agent_handler.py

import threading
import json
import queue
import time

from core.logger import log
from core.utils import now

# 🔥 GLOBAL TASK QUEUE (agent_id → queue)
AGENT_TASKS = {}


# ─────────────────────────────────────────
# 🚀 START AGENT SESSION
# ─────────────────────────────────────────
def start_agent_listener(agent_id, sock, socketio):
    try:
        from flask import current_app

        # ✅ INIT TASK QUEUE
        AGENT_TASKS[agent_id] = queue.Queue()

        # ✅ REGISTER AGENT
        if hasattr(current_app, "state"):
            current_app.state.add_agent(agent_id, {
                "id": agent_id,
                "status": "online",
                "connected_at": now(),
                "last_seen": now(),
                "hostname": "unknown",
                "os": "unknown",
                "ip": sock.getpeername()[0]
            })

        log(f"[AGENT] Registered: {agent_id}")

        # 🔥 Notify UI
        if socketio:
            socketio.emit("agent_connected", {
                "agent_id": agent_id
            })

    except Exception as e:
        log(f"[ERROR] Agent registration failed: {e}")

    # ✅ START THREADS
    threading.Thread(
        target=agent_recv_loop,
        args=(agent_id, sock, socketio),
        daemon=True
    ).start()

    threading.Thread(
        target=agent_send_loop,
        args=(agent_id, sock),
        daemon=True
    ).start()


# ─────────────────────────────────────────
# 📥 RECEIVE LOOP (AGENT → SERVER)
# ─────────────────────────────────────────
def agent_recv_loop(agent_id, sock, socketio):
    log(f"[AGENT] RX loop started: {agent_id}")

    buffer = b""

    try:
        while True:
            data = sock.recv(4096)

            if not data:
                break

            buffer += data

            # 🔥 SIMPLE DELIMITER PROTOCOL
            if b"\n" not in buffer:
                continue

            messages = buffer.split(b"\n")
            buffer = messages[-1]

            for msg in messages[:-1]:
                handle_agent_message(agent_id, msg, socketio)

    except Exception as e:
        log(f"[AGENT ERROR] {agent_id}: {e}")

    finally:
        handle_disconnect(agent_id, socketio)


# ─────────────────────────────────────────
# 📤 SEND LOOP (SERVER → AGENT)
# ─────────────────────────────────────────
def agent_send_loop(agent_id, sock):
    log(f"[AGENT] TX loop started: {agent_id}")

    try:
        while True:
            task = AGENT_TASKS[agent_id].get()

            if task is None:
                break

            message = json.dumps(task) + "\n"
            sock.sendall(message.encode())

    except Exception as e:
        log(f"[SEND ERROR] {agent_id}: {e}")


# ─────────────────────────────────────────
# 🧠 HANDLE MESSAGE
# ─────────────────────────────────────────
def handle_agent_message(agent_id, raw_msg, socketio):
    try:
        data = json.loads(raw_msg.decode())

        msg_type = data.get("type")

        from flask import current_app

        # ✅ HEARTBEAT
        if msg_type == "heartbeat":
            if hasattr(current_app, "state"):
                current_app.state.update_agent(agent_id, {
                    "last_seen": now(),
                    "status": "online"
                })

        # ✅ REGISTER METADATA
        elif msg_type == "register":
            if hasattr(current_app, "state"):
                current_app.state.update_agent(agent_id, {
                    "hostname": data.get("hostname"),
                    "os": data.get("os")
                })

        # ✅ COMMAND RESULT
        elif msg_type == "result":
            output = data.get("output", "")

            if socketio:
                socketio.emit("terminal_output", {
                    "agent_id": agent_id,
                    "output": output
                })

        # ✅ TELEMETRY (ADVANCED)
        elif msg_type == "telemetry":
            if socketio:
                socketio.emit("telemetry", data)

        else:
            log(f"[UNKNOWN MESSAGE] {agent_id}: {data}")

    except Exception as e:
        log(f"[PARSE ERROR] {agent_id}: {e}")


# ─────────────────────────────────────────
# 📡 SEND COMMAND TO AGENT
# ─────────────────────────────────────────
def send_command(agent_id, command):
    if agent_id not in AGENT_TASKS:
        log(f"[ERROR] Agent not found: {agent_id}")
        return False

    AGENT_TASKS[agent_id].put({
        "type": "command",
        "command": command
    })

    return True


# ─────────────────────────────────────────
# 🔌 DISCONNECT HANDLER
# ─────────────────────────────────────────
def handle_disconnect(agent_id, socketio):
    log(f"[AGENT] Disconnected: {agent_id}")

    try:
        from flask import current_app

        if hasattr(current_app, "state"):
            current_app.state.update_agent(agent_id, {
                "status": "offline",
                "last_seen": now()
            })

    except Exception as e:
        log(f"[STATE ERROR] {e}")

    # cleanup queue
    if agent_id in AGENT_TASKS:
        AGENT_TASKS[agent_id].put(None)
        del AGENT_TASKS[agent_id]

    if socketio:
        socketio.emit("agent_offline", {
            "agent_id": agent_id
        })

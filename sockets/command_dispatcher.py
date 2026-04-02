# sockets/command_dispatcher.py

from core.logger import log

def dispatch_command(agent_id, command, socketio):
    try:
        from flask import current_app

        state = getattr(current_app, "state", None)

        if not state:
            log("State not initialized")
            return

        agent = state.agents.get(agent_id)

        if not agent:
            log(f"Agent {agent_id} not found")
            return

        sock = agent.get("sock")

        if not sock:
            log(f"No socket for agent {agent_id}")
            return

        sock.send((command + "\n").encode())

        log(f"Sent command to {agent_id}: {command}")

    except Exception as e:
        log(f"Command dispatch failed: {e}")

        try:
            state.update_agent(agent_id, {"status": "offline"})
        except:
            pass

        if socketio:
            socketio.emit("agent_offline", {"agent_id": agent_id})

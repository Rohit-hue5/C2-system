# api/agent_routes.py

from flask import Blueprint, jsonify, request
from core.state import STATE

# ───────── BLUEPRINT ─────────
agent_bp = Blueprint("agents", __name__)


# ─────────────────────────────────────────
# 📡 GET ALL AGENTS
# ─────────────────────────────────────────
@agent_bp.route("/", methods=["GET"])
def get_agents():
    agents = STATE.get_agents()
    return jsonify(list(agents.values()))


# ─────────────────────────────────────────
# ➕ REGISTER NEW AGENT
# ─────────────────────────────────────────
@agent_bp.route("/register", methods=["POST"])
def register_agent():
    data = request.json or {}

    agent_id = data.get("id")
    if not agent_id:
        return jsonify({"error": "Agent ID required"}), 400

    STATE.add_agent(agent_id, data)

    return jsonify({
        "status": "registered",
        "agent_id": agent_id
    })


# ─────────────────────────────────────────
# 🔄 HEARTBEAT (UPDATE LAST SEEN)
# ─────────────────────────────────────────
@agent_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json or {}

    agent_id = data.get("id")
    if not agent_id:
        return jsonify({"error": "Agent ID required"}), 400

    STATE.update_agent(agent_id)

    return jsonify({"status": "alive"})


# ─────────────────────────────────────────
# ❌ REMOVE AGENT
# ─────────────────────────────────────────
@agent_bp.route("/<agent_id>", methods=["DELETE"])
def remove_agent(agent_id):
    agents = STATE.get_agents()

    if agent_id in agents:
        del agents[agent_id]
        return jsonify({"status": "removed"})

    return jsonify({"error": "Agent not found"}), 404


# ─────────────────────────────────────────
# 📊 SINGLE AGENT DETAILS
# ─────────────────────────────────────────
@agent_bp.route("/<agent_id>", methods=["GET"])
def get_agent(agent_id):
    agents = STATE.get_agents()

    if agent_id in agents:
        return jsonify(agents[agent_id])

    return jsonify({"error": "Agent not found"}), 404

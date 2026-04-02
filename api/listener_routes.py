from flask import Blueprint, jsonify, request
import socket
import subprocess

from flask import current_app
from core.state import STATE
from network.realtime_sniffer import RealtimeSniffer
from analysis.pipeline import process_devices

# ───────── BLUEPRINT ─────────
listener_bp = Blueprint("listener", __name__)

# ───────── GLOBAL STORE ─────────
SNIFFERS = {}   # name → sniffer instance


# ─────────────────────────────────────────
# 🛠 UTIL: CHECK PORT
# ─────────────────────────────────────────
def is_port_available(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, int(port))) != 0
    except:
        return False


# ─────────────────────────────────────────
# 🛠 UTIL: CHECK INTERFACE
# ─────────────────────────────────────────
def interface_exists(interface):
    try:
        result = subprocess.run(
            ["ip", "link", "show", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except:
        return False


# ─────────────────────────────────────────
# 🛠 UTIL: MONITOR MODE CHECK
# ─────────────────────────────────────────
def is_monitor_mode(interface):
    try:
        result = subprocess.check_output(["iwconfig", interface]).decode()
        return "Mode:Monitor" in result
    except:
        return False


# ─────────────────────────────────────────
# 📡 GET ALL LISTENERS
# ─────────────────────────────────────────
@listener_bp.route("/", methods=["GET"])
def get_listeners():
    return jsonify(list((STATE.get("listeners") or {}).values()))


# ─────────────────────────────────────────
# ➕ CREATE / RESTART LISTENER
# ─────────────────────────────────────────
@listener_bp.route("/create", methods=["POST"])
def create_listener():
    data = request.json or {}

    name = data.get("name")
    host = data.get("host", "0.0.0.0")
    port = data.get("port", 5051)
    interface = data.get("interface", "wlan0")

    if not name:
        return jsonify({"error": "Listener name required"}), 400

    listeners = STATE.get("listeners") or {}

    # ✅ IF EXISTS → CLEAN RESTART (IMPORTANT FIX)
    if name in listeners:
        try:
            if name in SNIFFERS:
                SNIFFERS[name].stop()
                del SNIFFERS[name]
        except:
            pass

        del listeners[name]
        STATE.set("listeners", listeners)

    # ❌ Port check
    if not is_port_available(host, port):
        return jsonify({"error": f"Port {port} already in use"}), 400

    # ❌ Interface check
    if not interface_exists(interface):
        return jsonify({"error": f"Interface {interface} not found"}), 400

    # ❌ Monitor mode
    if not is_monitor_mode(interface):
        return jsonify({"error": f"{interface} is NOT in monitor mode"}), 400

    try:
        # ✅ Start sniffer
        sniffer = RealtimeSniffer(
    interface=interface,
    socketio=current_app.socketio   # 🔥 THIS ENABLES REALTIME
)
        sniffer.start()

        SNIFFERS[name] = sniffer

        listener_obj = {
            "name": name,
            "host": host,
            "port": port,
            "interface": interface,
            "status": "running"
        }

        listeners[name] = listener_obj
        STATE.set("listeners", listeners)

        return jsonify({
            "status": "created",
            "listener": listener_obj
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# ⏹ STOP LISTENER (FULL CLEAN)
# ─────────────────────────────────────────
@listener_bp.route("/stop/<name>", methods=["POST"])
def stop_listener(name):
    listeners = STATE.get("listeners") or {}

    if name not in listeners:
        return jsonify({"error": "Listener not found"}), 404

    try:
        if name in SNIFFERS:
            SNIFFERS[name].stop()
            del SNIFFERS[name]

        # ✅ REMOVE COMPLETELY (CRITICAL FIX)
        del listeners[name]
        STATE.set("listeners", listeners)

        return jsonify({"status": "stopped"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# ❌ DELETE LISTENER
# ─────────────────────────────────────────
@listener_bp.route("/<name>", methods=["DELETE"])
def delete_listener(name):
    listeners = STATE.get("listeners") or {}

    if name not in listeners:
        return jsonify({"error": "Listener not found"}), 404

    try:
        if name in SNIFFERS:
            SNIFFERS[name].stop()
            del SNIFFERS[name]

        del listeners[name]
        STATE.set("listeners", listeners)

        return jsonify({"status": "deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# 📡 GET NETWORK DATA
# ─────────────────────────────────────────
@listener_bp.route("/network/<name>", methods=["GET"])
def get_network(name):
    if name not in SNIFFERS:
        return jsonify({"error": "Sniffer not running"}), 404

    try:
        devices = SNIFFERS[name].get_devices()

        return jsonify({
            "count": len(devices),
            "devices": devices
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# 🧠 INTELLIGENCE
# ─────────────────────────────────────────
@listener_bp.route("/network/<name>/intel", methods=["GET"])
def get_network_intel(name):
    if name not in SNIFFERS:
        return jsonify({"error": "Sniffer not running"}), 404

    try:
        devices = SNIFFERS[name].get_devices()
        enriched = process_devices(devices)

        return jsonify({
            "count": len(enriched),
            "devices": enriched
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# 🔄 RESET DEVICES
# ─────────────────────────────────────────
@listener_bp.route("/network/<name>/reset", methods=["POST"])
def reset_network(name):
    if name not in SNIFFERS:
        return jsonify({"error": "Sniffer not running"}), 404

    try:
        SNIFFERS[name].devices.clear()
        return jsonify({"status": "reset"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

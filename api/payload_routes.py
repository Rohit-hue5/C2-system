# api/payload_routes.py

from flask import Blueprint, jsonify, request, send_file
import os
import subprocess

# ✅ FIX: added url_prefix
payload_bp = Blueprint("payload", __name__, url_prefix="/api/payload")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOADERS_DIR = os.path.join(BASE_DIR, "payloads", "loaders")
OUTPUT_DIR = os.path.join(BASE_DIR, "payloads", "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────
# GET LOADERS
# ─────────────────────────────
@payload_bp.route("/loaders", methods=["GET"])
def get_loaders():
    files = [
        f.replace(".cpp", "")
        for f in os.listdir(LOADERS_DIR)
        if f.endswith(".cpp")
    ]
    return jsonify(files)


# ─────────────────────────────
# GET CERTIFICATES
# ─────────────────────────────
@payload_bp.route("/certificates", methods=["GET"])
def get_certs():
    try:
        cert_dir = os.path.join(BASE_DIR, "certificates")

        if not os.path.exists(cert_dir):
            return jsonify({
                "error": "Certificates directory not found",
                "path": cert_dir
            }), 500

        files = []

        for f in os.listdir(cert_dir):
            if f.endswith(".json"):
                files.append(f.replace(".json", ""))

        return jsonify(files)

    except Exception as e:
        return jsonify({
            "error": "Failed to load certificates",
            "details": str(e)
        }), 500

# ─────────────────────────────
# GENERATE PAYLOAD (REAL BUILD)
# ─────────────────────────────
@payload_bp.route("/generate", methods=["POST"])
def generate_payload():
    data = request.json

    loader = data.get("loader")
    cert = data.get("certificate")

    if not loader:
        return jsonify({"error": "Loader required"}), 400

    cpp_file = os.path.join(LOADERS_DIR, f"{loader}.cpp")
    output_file = os.path.join(OUTPUT_DIR, f"{loader}.exe")

    if not os.path.exists(cpp_file):
        return jsonify({"error": "Loader not found"}), 404

    try:
        compile_cmd = [
            "x86_64-w64-mingw32-g++",
            cpp_file,
            "-o",
            output_file,
            "-lws2_32",
            "-lwininet",
            "-lcrypt32",
            "-static",
            "-s"
        ]

        result = subprocess.run(
            compile_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                "error": "Compilation failed",
                "details": result.stderr
            }), 500

        return jsonify({
            "status": "success",
            "file": f"/api/payload/download/{loader}.exe"
        })

    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "details": str(e)
        }), 500


# ─────────────────────────────
# DOWNLOAD FILE
# ─────────────────────────────
@payload_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

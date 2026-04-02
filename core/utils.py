# core/utils.py

import socket
import hashlib
import os
import time
import base64
import random
import string
import subprocess
from datetime import datetime


# -----------------------------------------
# 🌐 NETWORK UTILITIES
# -----------------------------------------

def get_local_ip():
    """Get primary local IP"""
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        if s:
            s.close()


def get_free_port():
    """Find available port"""
    s = socket.socket()
    try:
        s.bind(('', 0))
        return s.getsockname()[1]
    finally:
        s.close()


def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except Exception:
        return False


# -----------------------------------------
# 🆔 ID GENERATION
# -----------------------------------------

def generate_id(prefix="", length=8):
    raw = f"{prefix}{time.time()}{random.random()}"
    return hashlib.md5(raw.encode()).hexdigest()[:length]


def generate_agent_id(ip, port):
    return hashlib.md5(f"{ip}{port}{time.time()}".encode()).hexdigest()[:8]


# -----------------------------------------
# 🔐 HASHING / ENCODING
# -----------------------------------------

def sha256(data: str):
    return hashlib.sha256(data.encode()).hexdigest()


def xor_encode(data: bytes, key: int):
    return bytes([b ^ key for b in data])


def base64_encode(data: bytes):
    return base64.b64encode(data).decode()


def base64_decode(data: str):
    return base64.b64decode(data)


# -----------------------------------------
# 🧪 RANDOM GENERATION
# -----------------------------------------

def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def random_filename(ext="exe"):
    return f"{random_string(6)}_{int(time.time())}.{ext}"


def random_xor_key():
    return random.randint(1, 254)


# -----------------------------------------
# ⏱ TIME HELPERS
# -----------------------------------------

def now():
    return datetime.now().isoformat()

def format_uptime(seconds):
    seconds = int(seconds)

    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)

    return f"{hrs:02d}:{mins:02d}:{sec:02d}"

#------------------------------------------
# ⚙ SYSTEM COMMAND EXECUTION
# -----------------------------------------

def run_command(cmd):
    """Run shell command safely"""
    try:
        result = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10
        )
        return result.decode(errors="ignore")

    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")

    except Exception as e:
        return str(e)


# -----------------------------------------
# 📦 FILE HELPERS
# -----------------------------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_binary(path, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def read_binary(path):
    with open(path, "rb") as f:
        return f.read()


# -----------------------------------------
# 💣 PAYLOAD HELPERS
# -----------------------------------------

def generate_payload_name(loader, cert):
    return f"{loader}_{cert}_{int(time.time())}.exe"


def calculate_size_kb(data: bytes):
    return round(len(data) / 1024, 2)

# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ───────── NETWORK ─────────
LHOST = os.environ.get("LHOST", "127.0.0.1")
LPORT = int(os.environ.get("LPORT", 4444))

# ───────── FLASK ─────────
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

SECRET_KEY = os.environ.get("SECRET_KEY", "c2lab-secret")

# ───────── SANDBOX ─────────
LITTERBOX_API = os.environ.get("LITTERBOX_API", "http://127.0.0.1:1337")

# ───────── RL CONFIG ─────────
LOADERS = [
    "apc",
    "classic",
    "earlybird",
    "mokingjay",
    "original",
]

CERTIFICATES = [
    "microsoft", "adobe", "apple",
    "oracle", "google", "mozilla", "ibm"
]

XOR_KEYS = list(range(1, 255))

EPISODES = int(os.environ.get("EPISODES", 5))
MAX_STEPS = int(os.environ.get("MAX_STEPS", 30))
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", 0.1))

# ───────── PATHS ─────────
PAYLOADS_DIR = os.path.join(BASE_DIR, "payloads")
LOADERS_DIR = os.path.join(PAYLOADS_DIR, "loaders")
OUTPUT_DIR = os.path.join(PAYLOADS_DIR, "output")

CERT_DIR = os.path.join(BASE_DIR, "certificates")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
for d in [OUTPUT_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)

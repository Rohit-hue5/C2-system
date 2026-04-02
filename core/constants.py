# core/constants.py

# ───────── AGENT STATES ─────────
AGENT_ONLINE = "online"
AGENT_OFFLINE = "offline"
AGENT_SUSPICIOUS = "suspicious"
AGENT_COMPROMISED = "compromised"


# ───────── TELEMETRY TYPES ─────────
TELEMETRY_SYSTEM = "system"
TELEMETRY_NETWORK = "network"
TELEMETRY_FILE = "file"
TELEMETRY_PROCESS = "process"
TELEMETRY_REGISTRY = "registry"


# ───────── MODEL ACTIONS ─────────
MODEL_EVADE = "evade"
MODEL_PERSIST = "persist"
MODEL_EXFIL = "exfil"
MODEL_LATERAL = "lateral"


# ───────── CACHE TTLs (seconds) ─────────
CACHE_TELEMETRY = 3600        # 1 hour
CACHE_ANALYSIS = 86400        # 24 hours
CACHE_MODEL = 300             # 5 minutes


# ───────── FILE EXTENSIONS ─────────
ALLOWED_EXTENSIONS = {
    ".exe",
    ".dll",
    ".ps1",
    ".bat",
    ".py",
    ".json"
}


# ───────── SECURITY THRESHOLDS ─────────
ALERT_THRESHOLD_HIGH = 0.9
ALERT_THRESHOLD_MEDIUM = 0.7


# ───────── OPTIONAL (INTEGRATION HELPERS) ─────────
# These help avoid magic strings across modules (NO logic change)

DEFAULT_AGENT_STATE = AGENT_OFFLINE
DEFAULT_TELEMETRY_TYPE = TELEMETRY_SYSTEM

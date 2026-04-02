# analysis/pipeline.py

import time


def process_devices(devices):
    """
    Enrich scanned/sniffed devices with intelligence
    """

    enriched = []

    for d in devices:
        try:
            enriched.append({
                "ip": d.get("ip"),
                "mac": d.get("mac"),
                "hostname": d.get("hostname", "unknown"),
                "vendor": d.get("vendor", "Unknown"),
                "open_ports": d.get("open_ports", []),
                "last_seen": d.get("last_seen", time.time()),

                # 🧠 Derived intelligence
                "is_router": d.get("ip", "").endswith(".1"),
                "risk": calculate_risk(d),
                "device_type": classify_device(d)
            })

        except Exception:
            continue

    return enriched


# ─────────────────────────────
# 🧠 RISK ENGINE (BASIC)
# ─────────────────────────────
def calculate_risk(device):
    ports = device.get("open_ports", [])

    if 23 in ports:
        return "HIGH"  # Telnet
    if 445 in ports:
        return "MEDIUM"  # SMB
    if 3389 in ports:
        return "MEDIUM"  # RDP

    return "LOW"


# ─────────────────────────────
# 📱 DEVICE CLASSIFIER
# ─────────────────────────────
def classify_device(device):
    vendor = (device.get("vendor") or "").lower()

    if "apple" in vendor or "samsung" in vendor:
        return "mobile"

    if "tp-link" in vendor or device.get("ip", "").endswith(".1"):
        return "router"

    return "computer"

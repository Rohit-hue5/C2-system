from typing import Dict, Any, List
import time
import numpy as np


class ScoringEngine:
    def __init__(self):
        # 🔥 BASELINE STORAGE (learning normal behavior)
        self.baseline = {}
        self.history = []

        # config
        self.window_size = 20
        self.anomaly_threshold = 2.5  # std deviation multiplier

    # ─────────────────────────────────────────
    # 📊 MAIN SCORING FUNCTION
    # ─────────────────────────────────────────
    def score_devices(self, devices: List[Dict[str, Any]]):
        now = time.time()

        scores = []
        total_packets = sum(d.get("packets", 0) for d in devices)

        # store history
        self.history.append(total_packets)
        if len(self.history) > self.window_size:
            self.history.pop(0)

        avg = np.mean(self.history) if self.history else 0
        std = np.std(self.history) if self.history else 1

        anomaly = False

        # 🔥 GLOBAL TRAFFIC ANOMALY
        if std > 0 and abs(total_packets - avg) > self.anomaly_threshold * std:
            anomaly = True

        for d in devices:
            score, level = self._score_device(d, avg, std)
            scores.append({
                "ip": d.get("ip"),
                "score": score,
                "risk": level,
                "packets": d.get("packets"),
                "last_seen": d.get("last_seen")
            })

        return {
            "total_packets": total_packets,
            "average": avg,
            "std_dev": std,
            "anomaly": anomaly,
            "devices": scores
        }

    # ─────────────────────────────────────────
    # 🧠 PER DEVICE SCORING
    # ─────────────────────────────────────────
    def _score_device(self, device, avg, std):
        packets = device.get("packets", 0)
        ip = device.get("ip")

        baseline = self.baseline.get(ip, {
            "avg_packets": packets,
            "last_seen": time.time()
        })

        # 🔥 UPDATE BASELINE (LEARNING)
        baseline["avg_packets"] = (baseline["avg_packets"] + packets) / 2
        baseline["last_seen"] = time.time()
        self.baseline[ip] = baseline

        # ─────────────────────────────
        # ⚠️ ANOMALY DETECTION
        # ─────────────────────────────
        deviation = abs(packets - baseline["avg_packets"])

        score = 0

        # packet-based scoring
        if packets > baseline["avg_packets"] * 2:
            score += 40

        if deviation > 10:
            score += 20

        if std > 0 and packets > avg + (2 * std):
            score += 30

        # new device bonus risk
        if ip not in self.baseline:
            score += 25

        score = min(score, 100)

        # ─────────────────────────────
        # 🚨 RISK LEVEL
        # ─────────────────────────────
        if score >= 80:
            level = "CRITICAL"
        elif score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, level

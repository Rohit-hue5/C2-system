import os
from core.logger import log
from datetime import datetime


class AutoResponseEngine:
    def __init__(self, listener=None, socketio=None):
        self.listener = listener
        self.socketio = socketio

        # ⚙️ thresholds (tune later)
        self.block_threshold = 4
        self.alert_threshold = 2

        self.blocked_ips = set()

    # ─────────────────────────────
    # 🚨 MAIN ENTRY
    # ─────────────────────────────
    def process(self, devices):
        for d in devices:
            score = d.get("anomaly_score", 0)
            ip = d.get("ip")

            if not ip:
                continue

            # 🚫 BLOCK
            if score >= self.block_threshold:
                self.block_ip(ip)

            # ⚠ ALERT
            elif score >= self.alert_threshold:
                self.raise_alert(ip, score)

    # ─────────────────────────────
    # 🚫 BLOCK IP
    # ─────────────────────────────
    def block_ip(self, ip):
        if ip in self.blocked_ips:
            return

        try:
            os.system(f"iptables -A INPUT -s {ip} -j DROP")
            self.blocked_ips.add(ip)

            log(f"[AUTO] Blocked IP: {ip}")

            if self.socketio:
                self.socketio.emit("auto:block", {
                    "ip": ip,
                    "time": str(datetime.now())
                })

        except Exception as e:
            log(f"[AUTO ERROR] Block failed: {e}")

    # ─────────────────────────────
    # ⚠ ALERT
    # ─────────────────────────────
    def raise_alert(self, ip, score):
        log(f"[AUTO] Alert: {ip} score={score}")

        if self.socketio:
            self.socketio.emit("auto:alert", {
                "ip": ip,
                "score": score,
                "time": str(datetime.now())
            })

    # ─────────────────────────────
    # 🤖 COMMAND AGENT
    # ─────────────────────────────
    def respond_to_agent(self, agent_id, command):
        if not self.listener:
            return

        success = self.listener.send_to_agent(agent_id, command)

        if success:
            log(f"[AUTO] Command sent to {agent_id}: {command}")

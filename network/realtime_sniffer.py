from scapy.all import sniff, ARP, IP, IPv6
import threading
import time
import subprocess

from analysis.scoring import ScoringEngine


class RealtimeSniffer:
    def __init__(self, interface, socketio=None, listener=None):
        self.interface = interface
        self.socketio = socketio
        self.listener = listener

        self.devices = {}
        self.lock = threading.Lock()

        self.running = False

        # CONFIG
        self.device_timeout = 60  # remove inactive devices

        # METRICS
        self.total_packets = 0
        self.prev_total_packets = 0
        self.pps = 0

        # AI
        self.scorer = ScoringEngine()

        # AUTO RESPONSE
        self.blocked_ips = set()
        self.last_action = {}
        self.cooldown = 30

    # ─────────────────────────────
    # 📦 PROCESS PACKET (IPv4 + IPv6 FIXED)
    # ─────────────────────────────
    def _process_packet(self, packet):
        try:
            ip = None
            mac = None

            # ARP
            if packet.haslayer(ARP):
                ip = packet[ARP].psrc
                mac = packet[ARP].hwsrc

            # IPv4
            elif packet.haslayer(IP):
                ip = packet[IP].src

            # IPv6
            elif packet.haslayer(IPv6):
                ip = packet[IPv6].src

            if not ip:
                return

            now = time.time()

            # DEBUG
            print(f"[PACKET] {ip}")

            with self.lock:
                self.total_packets += 1

                if ip not in self.devices:
                    self.devices[ip] = {
                        "ip": ip,
                        "mac": mac or "unknown",
                        "first_seen": now,
                        "last_seen": now,
                        "packets": 1,
                        "pps": 0,
                        "risk": "LOW",
                        "score": 0
                    }
                else:
                    d = self.devices[ip]
                    d["last_seen"] = now
                    d["packets"] += 1

        except Exception as e:
            print("[ERROR] Packet processing:", e)

    # ─────────────────────────────
    # 📊 METRICS + CLEANUP
    # ─────────────────────────────
    def _metrics_loop(self):
        while self.running:
            time.sleep(1)

            with self.lock:
                current = self.total_packets
                self.pps = current - self.prev_total_packets
                self.prev_total_packets = current

                now = time.time()

                # update PPS per device
                for d in self.devices.values():
                    duration = max(now - d["first_seen"], 1)
                    d["pps"] = round(d["packets"] / duration, 2)

                # 🔥 CLEANUP OLD DEVICES
                self.devices = {
                    ip: d for ip, d in self.devices.items()
                    if now - d["last_seen"] < self.device_timeout
                }

    # ─────────────────────────────
    # 🧠 AI ANALYSIS
    # ─────────────────────────────
    def _analysis_loop(self):
        while self.running:
            time.sleep(2)

            with self.lock:
                devices = list(self.devices.values())

            if not devices:
                continue

            try:
                result = self.scorer.score_devices(devices)
                enriched = result["devices"]

                with self.lock:
                    for d in self.devices.values():
                        for e in enriched:
                            if d["ip"] == e["ip"]:
                                d["score"] = e["score"]
                                d["risk"] = e["risk"]

                # AUTO RESPONSE
                for d in enriched:
                    self._auto_response(d)

                # GLOBAL ANOMALY
                if result.get("anomaly") and self.socketio:
                    self.socketio.emit("network_anomaly", {
                        "type": "TRAFFIC_SPIKE",
                        "total_packets": result.get("total_packets", 0)
                    })

            except Exception as e:
                print("[ERROR] Analysis:", e)

    # ─────────────────────────────
    # 🚨 AUTO RESPONSE
    # ─────────────────────────────
    def _auto_response(self, device):
        ip = device["ip"]
        risk = device["risk"]

        now = time.time()

        if ip in self.last_action:
            if now - self.last_action[ip] < self.cooldown:
                return

        if risk == "CRITICAL" and ip not in self.blocked_ips:
            self._block_ip(ip)
            self.last_action[ip] = now

        elif risk == "HIGH":
            if self.listener:
                for agent_id in self.listener.connections:
                    self.listener.send_to_agent(agent_id, f"monitor {ip}")
            self.last_action[ip] = now

    # ─────────────────────────────
    # 🚫 BLOCK IP
    # ─────────────────────────────
    def _block_ip(self, ip):
        try:
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                check=True
            )
            self.blocked_ips.add(ip)

            print(f"[AUTO] Blocked {ip}")

            if self.socketio:
                self.socketio.emit("auto_action", {
                    "action": "BLOCK_IP",
                    "ip": ip
                })

        except Exception as e:
            print("[ERROR] Block IP:", e)

    # ─────────────────────────────
    # 🚨 ALERTS
    # ─────────────────────────────
    def _detect_alerts(self, devices):
        alerts = []

        for d in devices:
            if d["risk"] in ["HIGH", "CRITICAL"]:
                alerts.append({
                    "ip": d["ip"],
                    "severity": d["risk"],
                    "score": d["score"],
                    "reason": f"Score: {d['score']}"
                })

        return alerts

    # ─────────────────────────────
    # 📡 EMIT
    # ─────────────────────────────
    def _emit_loop(self):
        while self.running:
            time.sleep(2)

            if not self.socketio:
                continue

            with self.lock:
                devices = list(self.devices.values())

                metrics = {
                    "pps": self.pps,
                    "total_packets": self.total_packets,
                    "device_count": len(devices)
                }

            alerts = self._detect_alerts(devices)

            print("[EMIT]", metrics)

            self.socketio.emit("devices_update", {
                "devices": devices,
                "metrics": metrics,
                "alerts": alerts
            })

    # ─────────────────────────────
    # ▶ START
    # ─────────────────────────────
    def start(self):
        if self.running:
            return

        self.running = True

        threading.Thread(target=self._sniff, daemon=True).start()
        threading.Thread(target=self._metrics_loop, daemon=True).start()
        threading.Thread(target=self._analysis_loop, daemon=True).start()
        threading.Thread(target=self._emit_loop, daemon=True).start()

    def _sniff(self):
        print(f"[SNIFFER] Listening on {self.interface}")

        try:
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False
            )
        except Exception as e:
            print("[ERROR] Sniffer failed:", e)

    def stop(self):
        self.running = False

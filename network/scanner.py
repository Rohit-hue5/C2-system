# network/scanner.py

from scapy.all import ARP, Ether, srp
import socket
import netifaces
import threading
import time
from typing import List, Dict


class NetworkScanner:
    def __init__(self, interface: str = None, timeout: float = 1.5):
        self.timeout = timeout
        self.interface = interface
        self.devices = []

    # ─────────────────────────────
    # 🌐 GET LOCAL NETWORK RANGE
    # ─────────────────────────────
    def get_local_network(self) -> str:
        try:
            iface = self.interface or netifaces.gateways()['default'][netifaces.AF_INET][1]
            addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
            ip = addr['addr']

            network = ip.rsplit('.', 1)[0] + ".0/24"
            return network

        except Exception as e:
            raise Exception(f"Failed to get network: {e}")

    # ─────────────────────────────
    # 🔍 ARP SCAN (REAL DEVICE DISCOVERY)
    # ─────────────────────────────
    def arp_scan(self, network: str) -> List[Dict]:
        try:
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")

            packet = ether / arp

            result = srp(
                packet,
                timeout=self.timeout,
                iface=self.interface,
                verbose=0
            )[0]

            devices = []

            for sent, received in result:
                devices.append({
                    "ip": received.psrc,
                    "mac": received.hwsrc,
                    "hostname": self.resolve_hostname(received.psrc),
                    "vendor": self.get_vendor(received.hwsrc),
                    "last_seen": time.time()
                })

            return devices

        except Exception as e:
            return [{"error": str(e)}]

    # ─────────────────────────────
    # 🔌 PORT SCANNING (PARALLEL)
    # ─────────────────────────────
    def scan_port(self, host: str, port: int) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)

        try:
            return sock.connect_ex((host, port)) == 0
        except Exception:
            return False
        finally:
            sock.close()

    def scan_ports_parallel(self, host: str, ports: List[int]) -> List[int]:
        open_ports = []
        threads = []

        def worker(port):
            if self.scan_port(host, port):
                open_ports.append(port)

        for port in ports:
            t = threading.Thread(target=worker, args=(port,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return open_ports

    # ─────────────────────────────
    # 🧠 HOSTNAME RESOLUTION
    # ─────────────────────────────
    def resolve_hostname(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "unknown"

    # ─────────────────────────────
    # 🏭 MAC → VENDOR LOOKUP
    # ─────────────────────────────
    def get_vendor(self, mac: str) -> str:
        try:
            # Simple OUI lookup (can expand later)
            prefix = mac.upper()[0:8]

            vendors = {
                "00:1A:2B": "Cisco",
                "00:1B:63": "Apple",
                "00:1C:B3": "Samsung",
                "FC:FB:FB": "Google",
                "F4:F5:D8": "TP-Link"
            }

            return vendors.get(prefix, "Unknown")

        except Exception:
            return "Unknown"

    # ─────────────────────────────
    # 🚀 FULL NETWORK SCAN
    # ─────────────────────────────
    def full_scan(self) -> Dict:
        network = self.get_local_network()

        devices = self.arp_scan(network)

        # Add port scan info
        for device in devices:
            if "ip" in device:
                device["open_ports"] = self.scan_ports_parallel(
                    device["ip"],
                    [21, 22, 80, 443, 445, 3389]
                )

        return {
            "network": network,
            "count": len(devices),
            "devices": devices,
            "timestamp": time.time()
        }


# ─────────────────────────────
# 🎯 FUNCTION USED BY TERMINAL
# ─────────────────────────────
def scan_network(interface: str = None):
    scanner = NetworkScanner(interface=interface)
    return scanner.full_scan()

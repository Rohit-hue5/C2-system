from scapy.all import sniff, IP
from typing import List, Dict
import time

class NetworkSniffer:
    def __init__(self, interface="wlan1"):
        self.interface = interface
        self.devices = {}

    def process_packet(self, packet):
        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst

            now = time.time()

            if src not in self.devices:
                self.devices[src] = {
                    "ip": src,
                    "first_seen": now,
                    "last_seen": now,
                    "count": 1
                }
            else:
                self.devices[src]["last_seen"] = now
                self.devices[src]["count"] += 1

    def start_sniffing(self, timeout=10) -> List[Dict]:
        self.devices = {}

        sniff(
            iface=self.interface,
            prn=self.process_packet,
            store=False,
            timeout=timeout
        )

        return list(self.devices.values())

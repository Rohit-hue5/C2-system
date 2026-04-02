# network/monitor.py

import time
import psutil
from typing import Dict


class NetworkMonitor:
    def __init__(self):
        self.last_stats = psutil.net_io_counters()

    def get_stats(self) -> Dict:
        """Get current network stats"""

        try:
            stats = psutil.net_io_counters()

            data = {
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv,
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "timestamp": time.time()
            }

            return data

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": time.time()
            }

    def get_connections(self):
        """Get active connections"""

        try:
            conns = psutil.net_connections(kind="inet")

            result = []

            for c in conns[:50]:  # limit for performance
                result.append({
                    "fd": c.fd,
                    "family": str(c.family),
                    "type": str(c.type),
                    "laddr": str(c.laddr),
                    "raddr": str(c.raddr),
                    "status": c.status
                })

            return result

        except Exception as e:
            return [{"error": str(e)}]

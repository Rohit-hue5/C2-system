# integrations/exporters.py

from typing import Dict, Any
import json


class ExporterManager:
    def __init__(self):
        self.exporters = {
            'json': self.export_json,
            'csv': self.export_csv
        }

    def export(self, data: Dict, format: str = 'json') -> str:
        """Export data in specified format"""
        exporter = self.exporters.get(format)

        if exporter:
            return exporter(data)

        raise ValueError(f"Unknown format: {format}")

    def export_json(self, data: Dict) -> str:
        return json.dumps(data, indent=2)

    def export_csv(self, data: Dict) -> str:
        # Minimal CSV (same logic, just safer)
        headers = ["id", "timestamp", "type"]
        row = [
            str(data.get("id", "1")),
            str(data.get("timestamp", "0")),
            str(data.get("type", "unknown"))
        ]

        return ",".join(headers) + "\n" + ",".join(row)

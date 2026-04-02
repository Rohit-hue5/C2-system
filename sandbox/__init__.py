# sandbox/__init__.py
# Unified sandbox interface

from sandbox.client import SandboxClient
from sandbox.analyzer import SandboxAnalyzer
from sandbox.reports import store_report, format_report

from core.logger import LOGGER


class Sandbox:
    def __init__(self, api_url):
        self.client = SandboxClient(api_url)
        self.analyzer = SandboxAnalyzer()

    # ─────────────────────────────
    # 🚀 FULL ANALYSIS PIPELINE
    # ─────────────────────────────
    def analyze_payload(self, payload):
        """
        Full pipeline:
        Upload → Poll → Analyze → Store
        """

        LOGGER.info(f"Starting sandbox analysis for {payload['id']}")

        task_id = self.client.upload_file(payload)

        if not task_id:
            LOGGER.error("Sandbox upload failed")
            return None

        result = self.client.get_result(task_id)

        if not result:
            LOGGER.warn("Sandbox returned no result")
            return None

        # Analyze
        detection = self.analyzer.extract_detection(result)
        metadata = self.analyzer.extract_metadata(result)

        # Store
        report = store_report(payload["id"], detection, metadata)

        return report

    # ─────────────────────────────
    # ⚡ QUICK SCORE ONLY (for RL)
    # ─────────────────────────────
    def quick_score(self, payload):
        task_id = self.client.upload_file(payload)

        if not task_id:
            return 1.0

        result = self.client.get_result(task_id)

        if not result:
            return 1.0

        return self.analyzer.extract_detection(result)

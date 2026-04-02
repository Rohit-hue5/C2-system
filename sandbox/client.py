# sandbox/client.py

import requests
import time

from core.logger import log
from core.utils import base64_decode


class SandboxClient:
    def __init__(self, api_url):
        self.api_url = api_url.rstrip("/")

    # ─────────────────────────────
    # 📤 Upload payload
    # ─────────────────────────────
    def upload_file(self, payload):
        try:
            binary = base64_decode(payload["payload"])

            files = {
                "file": (payload["filename"], binary)
            }

            response = requests.post(
                f"{self.api_url}/upload",
                files=files,
                timeout=10
            )

            if response.status_code != 200:
                log(f"Sandbox upload failed | status={response.status_code}")
                return None

            data = response.json()
            task_id = data.get("task_id")

            log(f"Sandbox upload success: {task_id}")
            return task_id

        except Exception as e:
            log(f"Sandbox upload error: {e}")
            return None

    # ─────────────────────────────
    # 📥 Poll result
    # ─────────────────────────────
    def get_result(self, task_id, retries=10):
        for attempt in range(retries):
            try:
                response = requests.get(
                    f"{self.api_url}/result/{task_id}",
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "completed":
                        log(f"Sandbox result ready: {task_id}")
                        return data

                log(f"Sandbox polling... attempt {attempt+1}/{retries}")
                time.sleep(3)

            except Exception as e:
                log(f"Sandbox polling error: {e}")
                break

        log(f"Sandbox timeout: {task_id}")
        return None

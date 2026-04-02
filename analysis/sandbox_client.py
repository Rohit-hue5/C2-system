import requests
import json
from typing import Dict, Any
from core import logger, exceptions

class SandboxClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    async def submit_sample(self, sample_hash: str, sample_data: bytes) -> Dict:
        """Submit sample to sandbox"""
        try:
            response = requests.post(
                f"{self.base_url}/analyze",
                json={"hash": sample_hash, "size": len(sample_data)},
                timeout=300
            )
            return response.json()
        except Exception as e:
            logger.error("Sandbox submission failed", error=str(e))
            raise exceptions.C2LabError(f"Sandbox error: {str(e)}")
    
    async def get_report(self, analysis_id: str) -> Dict:
        """Get sandbox report"""
        response = requests.get(f"{self.base_url}/report/{analysis_id}")
        return response.json()

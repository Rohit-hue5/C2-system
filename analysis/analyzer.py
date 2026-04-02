import time
import asyncio
from typing import Dict, Any

class Analyzer:
    def __init__(self):
        pass

    async def analyze_async(self, sample_hash: str) -> Dict[str, Any]:
        await asyncio.sleep(2)

        return {
            'hash': sample_hash,
            'behavior': ['network', 'persistence'],
            'ioc_count': 5,
            'suspicious_strings': ['cmd.exe'],
            'analysis_time': time.time(),
            'verdict': 'MALICIOUS'
        }

    def analyze(self, sample_hash: str) -> Dict[str, Any]:
        """SYNC wrapper for Flask"""
        return asyncio.run(self.analyze_async(sample_hash))

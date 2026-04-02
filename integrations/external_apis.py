# integrations/external_apis.py

import requests
import os
from typing import Dict


class ExternalAPIClient:
    def __init__(self):
        self.apis = {
            'virustotal': 'https://www.virustotal.com/api/v3/',
            'hybrid_analysis': 'https://www.hybrid-analysis.com/api/v2/'
        }

    def scan_hash(self, hash_value: str, api_name: str = 'virustotal') -> Dict:
        """Scan hash with external API"""

        api_key = os.getenv(f"{api_name.upper()}_API_KEY")

        if not api_key:
            return {'error': 'API key missing'}

        # Placeholder (your logic untouched)
        return {
            'status': 'scanned',
            'hash': hash_value,
            'provider': api_name
        }

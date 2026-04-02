# tests/test_api.py

import requests

BASE = "http://127.0.0.1:5000/api"


def test_health():
    r = requests.get(f"{BASE}/system/health")
    assert r.status_code == 200

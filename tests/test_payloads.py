# tests/test_payloads.py

import requests

def test_generate_payload():
    r = requests.post("http://127.0.0.1:5000/api/payload/generate", json={
        "loader": "apc",
        "cert": "google"
    })

    assert r.status_code == 200
    assert "payload" in r.json()

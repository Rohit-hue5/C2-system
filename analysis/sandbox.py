# analysis/sandbox.py

import os
import math
import subprocess

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0

    entropy = 0
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / len(data)
        if p_x > 0:
            entropy -= p_x * math.log2(p_x)

    return round(entropy, 4)


def extract_strings(file_path):
    try:
        result = subprocess.run(
            ["strings", file_path],
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()[:50]  # limit
    except:
        return []


def analyze_file(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        entropy = calculate_entropy(data)
        strings = extract_strings(file_path)

        return {
            "file": os.path.basename(file_path),
            "size": len(data),
            "entropy": entropy,
            "strings": strings[:20]
        }

    except Exception as e:
        return {"error": str(e)}

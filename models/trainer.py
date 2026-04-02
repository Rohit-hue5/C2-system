# models/trainer.py

import threading
from typing import Dict
from stable_baselines3 import PPO
from models.environment import EvasionEnv
import pickle
import time
import os


class Trainer:
    def __init__(self):
        self.env = EvasionEnv()
        self.model = None
        self.tasks = {}

    def start_training(self, config: Dict) -> str:
        """Start training task"""

        task_id = f"train_{int(time.time())}"
        self.tasks[task_id] = {"status": "running"}

        def train_loop():
            try:
                self.model = PPO("MlpPolicy", self.env, verbose=1)
                self.model.learn(total_timesteps=10000)

                # Safe path
                base_dir = os.path.dirname(os.path.abspath(__file__))
                save_path = os.path.join(base_dir, "saved", "final_agent.pkl")

                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                with open(save_path, "wb") as f:
                    pickle.dump(self.model, f)

                self.tasks[task_id] = {"status": "completed"}

            except Exception as e:
                self.tasks[task_id] = {
                    "status": "failed",
                    "error": str(e)
                }

        # ✅ FIX: Thread instead of asyncio
        thread = threading.Thread(target=train_loop, daemon=True)
        thread.start()

        return task_id

    def get_status(self, task_id: str) -> Dict:
        return self.tasks.get(task_id, {"status": "unknown"})

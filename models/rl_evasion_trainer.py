from stable_baselines3 import SAC
from models.environment import EvasionEnv
import os


class RLEvasionTrainer:
    def __init__(self, model_path="models/saved/final_agent"):
        self.env = EvasionEnv()
        self.model_path = model_path

        # Load existing model if exists
        if os.path.exists(model_path + ".zip"):
            print("[RL] Loading existing model...")
            self.model = SAC.load(model_path, env=self.env)
        else:
            print("[RL] Creating new model...")
            self.model = SAC(
                "MlpPolicy",
                self.env,
                policy_kwargs={"net_arch": [256, 256]},
                verbose=1,
                device="cpu"
            )

    def train(self, timesteps: int = 50000):
        """Train or continue training"""
        print(f"[RL] Training for {timesteps} timesteps...")

        self.model.learn(total_timesteps=timesteps)

        return self.model

    def save(self):
        """Save trained model"""
        self.model.save(self.model_path)
        print(f"[RL] Model saved → {self.model_path}")

    def evaluate(self, episodes: int = 100):
        """Evaluate trained model"""

        obs, _ = self.env.reset()
        total_reward = 0.0

        for _ in range(episodes):
            action, _ = self.model.predict(obs, deterministic=True)

            obs, reward, terminated, truncated, _ = self.env.step(action)
            total_reward += reward

            if terminated or truncated:
                obs, _ = self.env.reset()

        avg_reward = total_reward / episodes if episodes > 0 else 0.0

        print(f"[RL] Evaluation reward: {avg_reward}")

        return avg_reward

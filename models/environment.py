import gymnasium as gym
import numpy as np
from gymnasium import spaces


class EvasionEnv(gym.Env):
    """RL Environment for evasion training"""

    def __init__(self):
        super(EvasionEnv, self).__init__()

        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0], dtype=np.float32),
            high=np.array([1, 1, 1000, 1], dtype=np.float32),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(6)

        self.current_step = 0
        self.max_steps = 100

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0

        obs = np.array([0.5, 0.1, 10, 0.3], dtype=np.float32)
        return obs, {}

    def step(self, action):
        reward = self._calculate_reward(action)

        detection_prob = 0.1 if reward > 0 else 0.8

        terminated = np.random.random() < detection_prob
        truncated = self.current_step >= self.max_steps

        self.current_step += 1

        obs = self._next_observation()

        return obs, reward, terminated, truncated, {}

    def _calculate_reward(self, action):
        rewards = {
            0: 0.1,
            1: 0.8,
            2: 0.6,
            3: 0.4,
            4: 0.3,
            5: 0.2
        }
        return rewards.get(action, -1.0)

    def _next_observation(self):
        return np.random.random(4).astype(np.float32)

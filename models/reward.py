# models/reward.py

from typing import Dict


class RewardCalculator:
    def __init__(self):
        self.weights = {
            'evasion_success': 1.0,
            'persistence': 0.5,
            'lateral_success': 0.8,
            'detection': -1.0,
            'network_spike': -0.3
        }

    def calculate(self, telemetry: Dict) -> float:
        """Calculate reward from telemetry"""

        reward = 0.0

        if telemetry.get('evasion_success'):
            reward += self.weights['evasion_success']

        if telemetry.get('detection_event'):
            reward += self.weights['detection']

        return float(reward)

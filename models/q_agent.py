import torch
import torch.nn as nn
import numpy as np
from typing import Tuple


class QAgent(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super(QAgent, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)

    def predict(self, state: np.ndarray) -> Tuple[int, float]:
        self.eval()  # ✅ ensure inference mode

        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():  # ✅ performance + safety
            q_values = self(state_tensor)

        action = torch.argmax(q_values).item()
        confidence = torch.max(q_values).item()

        return action, confidence

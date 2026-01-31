import torch
import torch.nn as nn

class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Linear(4, 2)
        self.decoder = nn.Linear(2, 4)

    def forward(self, x):
        return self.decoder(self.encoder(x))


class AEAnomaly:
    def __init__(self):
        self.model = AutoEncoder()
        self.threshold = 0.1

    def score(self, features):
        x = torch.tensor([
            features["latency_ms"],
            features["retry_count"],
            features["success_rate"],
            features["avg_latency"]
        ], dtype=torch.float32)

        recon = self.model(x)
        loss = torch.mean((x - recon) ** 2).item()

        return min(loss, 1.0)

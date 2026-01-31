import numpy as np
from sklearn.ensemble import IsolationForest

class IFAnomaly:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)
        self.buffer = []

    def score(self, features):
        vector = np.array([
            features["latency_ms"],
            features["retry_count"],
            features["success_rate"],
            features["avg_latency"]
        ])

        self.buffer.append(vector)

        if len(self.buffer) < 50:
            return 0.0

        if len(self.buffer) == 50:
            self.model.fit(self.buffer)

        score = -self.model.score_samples([vector])[0]
        return min(score, 1.0)

class EWMAAnomaly:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.ema = None

    def score(self, features):
        value = features["latency_ms"]

        if self.ema is None:
            self.ema = value
            return 0.0

        self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        deviation = abs(value - self.ema)

        return min(deviation / 1000, 1.0)

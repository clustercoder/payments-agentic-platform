from collections import deque
import random

class ReplayBuffer:
    def __init__(self, size=10000):
        self.buffer = deque(maxlen=size)

    def add(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size=32):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

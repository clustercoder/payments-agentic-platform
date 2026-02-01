import gymnasium as gym
import numpy as np

class PaymentEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(5,), dtype=np.float32
        )

    def reset(self, *, seed=None, options=None):
        self.state = np.random.rand(5)
        return self.state, {}

    def step(self, action):
        success_rate, latency, retries, cost, risk = self.state

        reward = (
            success_rate * 2
            - latency
            - retries * 0.5
            - cost * 0.2
            - risk * 2
        )

        self.state = np.clip(
            self.state + np.random.normal(0, 0.05, size=5), 0, 1
        )

        done = False
        return self.state, reward, done, False, {}

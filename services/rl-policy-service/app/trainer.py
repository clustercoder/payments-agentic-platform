import torch
import torch.optim as optim
from app.policy import PolicyNet
from app.memory import ReplayBuffer

policy = PolicyNet()
optimizer = optim.Adam(policy.parameters(), lr=1e-3)
memory = ReplayBuffer()

def train_step():
    if len(memory) < 32:
        return

    batch = memory.sample(32)
    states, actions, rewards = zip(*batch)

    states = torch.tensor(states, dtype=torch.float32)
    actions = torch.tensor(actions)
    rewards = torch.tensor(rewards)

    logits = policy(states)
    selected = logits.gather(1, actions.unsqueeze(1)).squeeze()

    loss = -torch.mean(selected * rewards)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

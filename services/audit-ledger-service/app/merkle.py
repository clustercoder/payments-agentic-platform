import hashlib
import json
from typing import List

class MerkleTree:
    def __init__(self):
        self.leaves: List[str] = []

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def add_leaf(self, data: dict):
        serialized = json.dumps(data, sort_keys=True)
        self.leaves.append(self._hash(serialized))

    def get_root(self) -> str:
        nodes = self.leaves.copy()
        if not nodes:
            return None

        while len(nodes) > 1:
            temp = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                temp.append(self._hash(left + right))
            nodes = temp
        return nodes[0]

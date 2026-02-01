from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))

def anchor_root(root_hash: str):
    # Stub — real tx optional
    print(f"[ETH] Anchoring root: {root_hash}")

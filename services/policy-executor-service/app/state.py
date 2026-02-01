import redis
import json

class StateClient:
    def __init__(self):
        self.redis = redis.Redis(host="redis", port=6379, decode_responses=True)

    def set_retry_policy(self, issuer, max_retries, backoff_ms):
        key = f"issuer:{issuer}:retry_policy"
        self.redis.set(key, json.dumps({
            "max_retries": max_retries,
            "backoff_ms": backoff_ms
        }))

    def open_circuit(self, issuer):
        self.redis.set(f"issuer:{issuer}:circuit_open", "true")

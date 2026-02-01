import os
# Ensure you set your key before running: export OPENAI_API_KEY=sk-...
from app.nodes.reasoning import reasoning_node

# Mock anomaly data similar to what the anomaly-detector produces
mock_state = {
    "anomaly": {
        "issuer": "HDFC", 
        "severity": 0.85,
        "features": {
            "latency_ms": 4500,
            "success_rate": 0.65,
            "error_code": "TIMEOUT"
        }
    }
}

print("Running Reasoning Node...")
result = reasoning_node(mock_state)
print("\nHypothesis Generated:")
print(result["hypotheses"][0])
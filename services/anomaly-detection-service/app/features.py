from app.redis_state import get_issuer_snapshot


def extract_features(event):
    snapshot = get_issuer_snapshot(event["issuer"])

    return {
        "latency_ms": event["latency_ms"],
        "is_failure": int(event["is_failure"]),
        "hour": event["hour"],
        "success_rate": snapshot["success_rate"] if snapshot else 1.0,
        "avg_latency": snapshot["avg_latency"] if snapshot else event["latency_ms"],
        "retry_count": event["retry_count"]
    }

# services/stream-processor-service/app/enricher.py
from datetime import datetime


def enrich_event(event):
    event["hour"] = datetime.fromisoformat(event["timestamp"]).hour
    event["is_failure"] = event["status"] == "failure"
    event["high_latency"] = event["latency_ms"] > 3000
    return event

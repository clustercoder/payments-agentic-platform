# services/stream-processor-service/app/metrics.py
from prometheus_client import Counter

events_processed = Counter(
    "events_processed_total",
    "Total processed payment events",
    ["issuer", "event_type", "status"]
)

from prometheus_client import Counter, Histogram

payment_requests = Counter(
    "payment_requests_total",
    "Total payment requests",
    ["issuer", "method", "status"]
)

payment_latency = Histogram(
    "payment_latency_ms",
    "Payment latency",
    ["issuer", "method"]
)

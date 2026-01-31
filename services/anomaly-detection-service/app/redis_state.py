import redis

# Connect to the shared Redis instance
r = redis.Redis(host="redis", port=6379, decode_responses=True)

def get_issuer_snapshot(issuer):
    key = f"issuer:{issuer}"
    data = r.hgetall(key)

    if not data:
        return None

    count = int(data.get("count", 1))
    success = int(data.get("success", 0))
    latency_sum = float(data.get("latency_sum", 0))

    # Return the historical averages to compare against
    return {
        "success_rate": success / count,
        "avg_latency": latency_sum / count,
        "total_events": count
    }
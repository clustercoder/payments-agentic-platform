# services/stream-processor-service/app/redis_state.py
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)


def update_issuer_metrics(issuer, success, latency):
    key = f"issuer:{issuer}"

    r.hincrby(key, "count", 1)
    if success:
        r.hincrby(key, "success", 1)
    else:
        r.hincrby(key, "failure", 1)

    r.hincrbyfloat(key, "latency_sum", latency)


def get_issuer_snapshot(issuer):
    key = f"issuer:{issuer}"
    data = r.hgetall(key)

    if not data:
        return None

    count = int(data.get("count", 1))
    success = int(data.get("success", 0))
    latency_sum = float(data.get("latency_sum", 0))

    return {
        "success_rate": success / count,
        "avg_latency": latency_sum / count,
        "total_events": count
    }

import random
import time

ISSUER_FAILURE_RATES = {
    "HDFC": 0.05,
    "ICICI": 0.03,
    "SBI": 0.08,
    "AXIS": 0.04,
}

BASE_LATENCY = {
    "card": 800,
    "upi": 1200,
    "netbanking": 1500,
}


def simulate_latency(payment_method):
    base = BASE_LATENCY[payment_method]
    jitter = random.randint(-200, 400)
    latency = max(100, base + jitter)
    time.sleep(latency / 1000)
    return latency


def simulate_failure(issuer):
    return random.random() < ISSUER_FAILURE_RATES.get(issuer, 0.05)

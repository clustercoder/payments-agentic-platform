import json
from kafka import KafkaProducer
from uuid import uuid4
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers="redpanda:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def publish_anomaly(data):
    event = {
        "anomaly_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "issuer": data["issuer"],
        "anomaly_type": "payment_degradation",
        "severity": max(data["scores"].values()),
        "confidence": sum(data["scores"].values()) / 3,
        "features": data["features"],
        "explanation": f"Latency and success-rate deviation detected for {data['issuer']}"
    }

    producer.send("agent.anomalies", event)
    producer.flush()

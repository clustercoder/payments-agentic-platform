# services/payment-gateway-service/app/kafka_producer.py
import json
import time
import logging
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

logger = logging.getLogger(__name__)

BOOTSTRAP_SERVERS = ["redpanda:9092"]
TOPIC = "payments.raw"

_producer = None


def get_producer(retries=10, backoff=3):
    global _producer

    if _producer:
        return _producer

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Connecting to Kafka (attempt {attempt})...")
            _producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                linger_ms=10,
                request_timeout_ms=30000,
            )
            logger.info("Kafka producer connected successfully")
            return _producer
        except NoBrokersAvailable:
            logger.warning("Kafka broker not available yet")
            time.sleep(backoff)

    raise RuntimeError("Kafka broker not available after retries")


def publish_event(event):
    producer = get_producer()
    producer.send(TOPIC, event.dict())
    producer.flush()

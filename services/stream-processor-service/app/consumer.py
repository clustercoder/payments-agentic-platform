# services/stream-processor-service/app/consumer.py
import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from app.enricher import enrich_event
from app.redis_state import update_issuer_metrics
from app.clickhouse import insert_event
from app.metrics import events_processed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream-processor")

consumer = KafkaConsumer(
    "payments.raw",
    bootstrap_servers="redpanda:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

producer = KafkaProducer(
    bootstrap_servers="redpanda:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def start():
    logger.info("Stream processor started, waiting for messages...")
    for msg in consumer:
        try:
            event = msg.value
            enriched = enrich_event(event)

            insert_event(enriched)

            update_issuer_metrics(
                enriched["issuer"],
                enriched["status"] == "success",
                enriched["latency_ms"]
            )

            events_processed.labels(
                enriched["issuer"],
                enriched["event_type"],
                enriched["status"]
            ).inc()

            producer.send("payments.enriched", enriched)
            producer.flush()

            logger.info(f"Processed event {enriched['event_id']}")

        except Exception as e:
            logger.exception(f"Failed to process event: {e}")

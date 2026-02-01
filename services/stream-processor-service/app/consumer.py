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

            # --- START NEW CODE: FEEDBACK GENERATION ---
            # Calculate Reward (simplified version of the logic in rl-policy-service/app/env.py)
            # Reward: +1 for success, -penalty for latency/failure
            success = 1.0 if enriched["status"] == "success" else 0.0
            latency_penalty = min(enriched["latency_ms"] / 5000.0, 1.0) # Normalize latency
            reward = success - latency_penalty
            
            # Construct Feedback Payload
            # Note: Ideally 'action' comes from Redis/Policy Executor. 
            # Here we use a placeholder '0' (NO_OP) or derive it if available.
            feedback_payload = {
                "anomaly_id": enriched.get("event_id"), # correlating ID
                "state": [
                    success,
                    latency_penalty,
                    enriched.get("retry_count", 0) / 5.0, # Normalize retries
                    0.0, # cost placeholder
                    0.0  # risk placeholder
                ],
                "action": 0, # Placeholder for "action taken"
                "reward": reward,
                "timestamp": enriched["timestamp"]
            }
            
            # Produce to agent.feedback
            producer.send("agent.feedback", feedback_payload)
            # --- END NEW CODE ---

            producer.send("payments.enriched", enriched)
            producer.flush()

            logger.info(f"Processed event {enriched['event_id']}")

        except Exception as e:
            logger.exception(f"Failed to process event: {e}")
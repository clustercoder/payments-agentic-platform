import json
import logging
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
from app.graph import agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-brain")

# Retry logic for Kafka connection
consumer = None
while not consumer:
    try:
        consumer = KafkaConsumer(
            "agent.anomalies",
            bootstrap_servers="redpanda:9092",
            value_deserializer=lambda v: json.loads(v.decode()),
            auto_offset_reset='latest' # Prevent processing old stale anomalies on restart
        )
        logger.info("Connected to Kafka Consumer")
    except NoBrokersAvailable:
        logger.warning("Waiting for Kafka...")
        time.sleep(5)

producer = KafkaProducer(
    bootstrap_servers="redpanda:9092",
    value_serializer=lambda v: json.dumps(v).encode()
)

logger.info("Agent Brain Service Started")

for msg in consumer:
    try:
        logger.info(f"Received anomaly: {msg.value.get('anomaly_id', 'unknown')}")
        
        # Invoke the LangGraph agent
        result = agent.invoke({
            "anomaly": msg.value
        })

        # The result from LangGraph contains the full state. 
        # We generally want to publish the final decision/explanation.
        action_payload = {
            "anomaly_id": msg.value.get("anomaly_id"),
            "issuer": msg.value.get("issuer"),
            "proposed_action": result.get("proposed_action"),
            "explanation": result.get("explanation"),
            "timestamp": time.time()
        }

        producer.send("agent.actions", action_payload)
        producer.flush()
        logger.info(f"Published action for {msg.value.get('anomaly_id')}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
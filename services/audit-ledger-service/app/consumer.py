import json
import logging
from kafka import KafkaConsumer
from app.merkle import MerkleTree

logging.basicConfig(level=logging.INFO)

consumer = KafkaConsumer(
    "agent.actions",
    bootstrap_servers="redpanda:9092",
    value_deserializer=lambda m: json.loads(m.decode()),
    auto_offset_reset="earliest"
)

tree = MerkleTree()

def consume():
    for msg in consumer:
        event = msg.value

        audit_entry = {
            "action_id": event.get("action_id"),
            "timestamp": event.get("timestamp"),
            "issuer": event.get("issuer"),
            "decision": event.get("action_type"),
            "confidence": event.get("confidence"),
            "policy_result": event.get("execution_status"),
            "anomaly_id": event.get("source_anomaly_id")
        }

        tree.add_leaf(audit_entry)
        root = tree.get_root()

        logging.info(f"[AUDIT] New leaf added | Merkle Root: {root}")

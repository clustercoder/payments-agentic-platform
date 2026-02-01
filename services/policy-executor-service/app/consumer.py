from kafka import KafkaConsumer
import json

def get_consumer():
    return KafkaConsumer(
        "agent.actions",
        bootstrap_servers="redpanda:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="policy-executor"
    )

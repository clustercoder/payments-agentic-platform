import json
from kafka import KafkaConsumer
from app.trainer import memory, train_step

consumer = KafkaConsumer(
    "agent.feedback",
    bootstrap_servers="redpanda:9092",
    value_deserializer=lambda m: json.loads(m.decode()),
)

def start():
    for msg in consumer:
        fb = msg.value
        memory.add((
            fb["state"],
            fb["action"],
            fb["reward"]
        ))
        train_step()

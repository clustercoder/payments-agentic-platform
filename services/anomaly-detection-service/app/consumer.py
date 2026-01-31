import json
import logging
from kafka import KafkaConsumer
from app.features import extract_features
from app.detectors.ewma import EWMAAnomaly
from app.detectors.isolation_forest import IFAnomaly
from app.detectors.autoencoder import AEAnomaly
from app.publisher import publish_anomaly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-detector")

consumer = KafkaConsumer(
    "payments.enriched",
    bootstrap_servers="redpanda:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest", 
    enable_auto_commit=True
)

ewma = EWMAAnomaly()
iso = IFAnomaly()
ae = AEAnomaly()


def start():
    logger.info("Anomaly detector started")

    for msg in consumer:
        event = msg.value
        features = extract_features(event)

        ewma_score = ewma.score(features)
        iso_score = iso.score(features)
        ae_score = ae.score(features)

        combined_score = max(ewma_score, iso_score, ae_score)

        if combined_score > 0.7:
            anomaly = {
                "issuer": event["issuer"],
                "features": features,
                "scores": {
                    "ewma": ewma_score,
                    "iforest": iso_score,
                    "autoencoder": ae_score
                }
            }
            publish_anomaly(anomaly)

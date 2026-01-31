# services/stream-processor-service/app/clickhouse.py
import time
import logging
from clickhouse_driver import Client
from datetime import datetime

logger = logging.getLogger(__name__)

client = None


def get_client(retries=10, delay=3):
    global client
    if client:
        return client

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Connecting to ClickHouse (attempt {attempt})")
            # UPDATE THIS LINE:
            client = Client(host="clickhouse", user="default", password="password")
            
            client.execute("SELECT 1")
            logger.info("Connected to ClickHouse")
            return client
        except Exception as e:
            logger.warning(f"ClickHouse not ready: {e}")
            time.sleep(delay)

    raise RuntimeError("ClickHouse not available")


def insert_event(event: dict):
    ch = get_client()
    
    dt_timestamp = datetime.fromisoformat(event["timestamp"])

    ch.execute(
        "INSERT INTO payments VALUES",
        [(
            event["event_id"],
            dt_timestamp,  
            event["merchant_id"],
            event["payment_id"],
            event["issuer"],
            event["payment_method"],
            event["event_type"],
            event["status"],
            event["latency_ms"],
            event["retry_count"],
            event["error_code"],
            event["cost"]
        )]
    )
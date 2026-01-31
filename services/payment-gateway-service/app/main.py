from fastapi import FastAPI
from fastapi import BackgroundTasks

from uuid import uuid4
from app.models import create_base_event, PaymentMethod
from app.kafka_producer import publish_event
from app.simulator import simulate_latency, simulate_failure
from app.metrics import payment_requests, payment_latency
from prometheus_client import generate_latest
from fastapi.responses import PlainTextResponse
import logging

logger = logging.getLogger("payment-gateway")
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Mock Payment Gateway Service")


@app.post("/authorize")
def authorize_payment(
    merchant_id: str,
    issuer: str,
    payment_method: PaymentMethod,
    amount: float,
    background_tasks: BackgroundTasks
):


    payment_id = str(uuid4())
    retry_count = 0

    latency = simulate_latency(payment_method)
    failed = simulate_failure(issuer)

    status = "failure" if failed else "success"
    error_code = "ISSUER_TIMEOUT" if failed else None

    event = create_base_event(
        merchant_id=merchant_id,
        payment_id=payment_id,
        issuer=issuer,
        payment_method=payment_method,
        event_type="authorization",
        status=status,
        latency_ms=latency,
        retry_count=retry_count,
        error_code=error_code,
        cost=amount * 0.02
    )


    background_tasks.add_task(publish_event, event)


    payment_requests.labels(issuer, payment_method, status).inc()
    payment_latency.labels(issuer, payment_method).observe(latency)

    return {
        "payment_id": payment_id,
        "status": status,
        "latency_ms": latency
    }



@app.post("/capture")
def capture_payment(
    payment_id: str,
    issuer: str,
    payment_method: PaymentMethod,
    background_tasks: BackgroundTasks
):
    latency = simulate_latency(payment_method)
    failed = simulate_failure(issuer)

    status = "failure" if failed else "success"

    event = create_base_event(
        merchant_id="unknown",
        payment_id=payment_id,
        issuer=issuer,
        payment_method=payment_method,
        event_type="capture",
        status=status,
        latency_ms=latency,
        retry_count=0,
        error_code=None if not failed else "CAPTURE_FAILED",
        cost=0.0
    )

    background_tasks.add_task(publish_event, event)
    return {"payment_id": payment_id, "status": status}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type="text/plain")

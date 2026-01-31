# services/stream-processor-service/app/main.py
from threading import Thread
from fastapi import FastAPI
from prometheus_client import generate_latest
from fastapi.responses import PlainTextResponse
from app.consumer import start

app = FastAPI(title="Stream Processor Service")


@app.on_event("startup")
def startup():
    Thread(target=start, daemon=True).start()


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type="text/plain")

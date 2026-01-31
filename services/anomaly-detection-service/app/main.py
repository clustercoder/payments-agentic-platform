from threading import Thread
from fastapi import FastAPI
from app.consumer import start

app = FastAPI(title="Anomaly Detection Service")


@app.on_event("startup")
def startup():
    Thread(target=start, daemon=True).start()

from fastapi import FastAPI
import threading
from app.consumer import start

app = FastAPI()

@app.on_event("startup")
def boot():
    threading.Thread(target=start, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "rl-online"}

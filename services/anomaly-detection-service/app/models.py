from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class AnomalyEvent(BaseModel):
    anomaly_id: str
    timestamp: str
    issuer: str
    anomaly_type: str
    severity: float
    confidence: float
    features: Dict
    explanation: str

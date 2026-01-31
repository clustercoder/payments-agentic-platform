from pydantic import BaseModel
from typing import Optional
from enum import Enum
from uuid import uuid4
from datetime import datetime


class PaymentMethod(str, Enum):
    card = "card"
    upi = "upi"
    netbanking = "netbanking"


class PaymentEvent(BaseModel):
    event_id: str
    timestamp: str
    merchant_id: str
    payment_id: str
    issuer: str
    payment_method: PaymentMethod
    event_type: str
    status: str
    latency_ms: int
    retry_count: int
    error_code: Optional[str]
    cost: float


def create_base_event(**kwargs):
    return PaymentEvent(
        event_id=str(uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )

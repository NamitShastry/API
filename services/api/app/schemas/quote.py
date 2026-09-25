"""Pydantic schemas for fare quotes and live ticker streams."""

from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


class FareQuoteCreate(BaseModel):
    source_id: str = ""
    route_id: str = ""
    flight_number: str = ""
    airline_code: str = ""
    departure_datetime: str = ""
    arrival_datetime: str = ""
    fare_amount: float = 0.0
    currency: str = "INR"
    tax_amount: float = 0.0
    fare_class: str = "ECONOMY"
    is_direct: bool = True
    observed_at: Optional[str] = None


class LiveTickerItem(BaseModel):
    id: int = 0
    route_id: str = ""
    airline_code: str = ""
    flight_number: str = ""
    departure_date: str = ""
    bucket_id: str = ""
    base_fare: float = 0.0
    total_fare: float = 0.0
    taxes: float = 0.0
    observed_at: str = ""
    e2e_latency_ms: int = 0
    source_id: str = ""
    direction: str = "UP"

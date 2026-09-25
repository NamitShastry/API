"""Pydantic schemas for Index data, ticks, series, and analytics."""

from __future__ import annotations

import datetime
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


class IndexTick(BaseModel):
    """Real-time FLASH index tick emitted via WebSocket."""

    event_type: str = "INDEX_TICK"
    timestamp: str = ""
    data_mode: str = "SIMULATED_LIVE"
    series_id: str = "APIX-NAT-COMP"
    index_value: float = 100.0
    change_1d: float = 0.0
    e2e_latency_ms: int = 0
    coverage_pct: float = 100.0
    quote_count: int = 0
    status: str = "FRESH"


class CurrentIndexResponse(BaseModel):
    series_id: str = "APIX-NAT-COMP"
    series_name: str = ""
    index_value: float = 100.0
    change_1d: float = 0.0
    change_7d: float = 0.0
    change_30d: float = 0.0
    change_yoy: Optional[float] = None
    coverage_pct: float = 100.0
    e2e_latency_ms: int = 0
    quote_count: int = 0
    data_mode: str = "SIMULATED_LIVE"
    status: str = "FRESH"
    last_updated: str = ""


class SeriesPoint(BaseModel):
    date: str = ""
    index_value: float = 100.0
    change_1d: float = 0.0
    coverage_pct: float = 100.0
    is_frozen: bool = False


class SeriesHistoryResponse(BaseModel):
    series_id: str = ""
    series_name: str = ""
    points: list[SeriesPoint] = []


class RouteHeatmapCell(BaseModel):
    route_id: str = ""
    origin: str = ""
    destination: str = ""
    bucket_id: str = ""
    bucket_name: str = ""
    avg_price: float = 0.0
    index_value: float = 100.0
    quote_count: int = 0
    day_change_pct: float = 0.0


class WaterfallItem(BaseModel):
    category: str = ""
    name: str = ""
    impact_points: float = 0.0
    direction: str = "UP"


class LeadElasticityItem(BaseModel):
    bucket_id: str = ""
    bucket_name: str = ""
    min_days: int = 0
    max_days: int = 0
    avg_fare: float = 0.0
    base_price: float = 0.0
    premium_factor: float = 1.0

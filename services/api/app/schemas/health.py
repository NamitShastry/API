"""Pydantic schemas for platform health, service heartbeats, and source circuit states."""

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


class ServiceHeartbeat(BaseModel):
    service_name: str = ""
    status: str = "HEALTHY"
    last_heartbeat: str = ""
    uptime_seconds: int = 0
    details: Optional[dict] = None


class SourceHealthItem(BaseModel):
    source_id: str = ""
    source_name: str = ""
    source_type: str = ""
    status: str = "ACTIVE"
    quotes_last_hour: int = 0
    error_rate_pct: float = 0.0
    avg_latency_ms: int = 0
    last_success_at: str = ""


class SystemHealthResponse(BaseModel):
    system_status: str = "OPERATIONAL"
    data_mode: str = "SIMULATED_LIVE"
    overall_freshness: str = "FRESH"
    last_tick_timestamp: str = ""
    e2e_latency_ms: int = 0
    quotes_today: int = 0
    coverage_pct: float = 100.0
    active_services: list[ServiceHeartbeat] = []
    sources: list[SourceHealthItem] = []

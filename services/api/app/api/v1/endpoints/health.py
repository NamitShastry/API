"""System health, service heartbeats, and circuit state endpoints."""

from __future__ import annotations

import datetime
from fastapi import APIRouter

from app.collector.heartbeat import HeartbeatTracker
from app.core.config import settings
from app.engine.flash_engine import FlashEngine
from app.schemas.health import (
    ServiceHeartbeat,
    SourceHealthItem,
    SystemHealthResponse,
)

router = APIRouter(prefix="/health", tags=["Health & Operations"])


@router.get("/ping")
async def ping():
    """Simple liveness probe."""
    return {"status": "ok", "service": "aeroindex-api", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}


from fastapi.responses import PlainTextResponse
from app.core.observability import PrometheusMetricsExporter

@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Prometheus text exposition format metrics scraping endpoint."""
    return PrometheusMetricsExporter.generate_metrics_text()



@router.get("/system", response_model=SystemHealthResponse)
async def get_system_health():
    """Comprehensive system health dashboard data: active services, freshness, latency, and source circuits."""
    tick = FlashEngine.get_latest_tick()
    tick_dt = datetime.datetime.fromisoformat(tick.timestamp)
    freshness, _ = HeartbeatTracker.evaluate_freshness(tick_dt)

    # Active services
    service_dicts = HeartbeatTracker.get_all_services()
    services = []
    for s in service_dicts:
        services.append(ServiceHeartbeat(
            service_name=s["service_name"],
            status=s["status"],
            last_heartbeat=s["last_heartbeat"],
            uptime_seconds=s["uptime_seconds"],
            details=s.get("details"),
        ))

    # Source health statuses
    sources = [
        SourceHealthItem(
            source_id="INDIGO",
            source_name="IndiGo (6E)",
            source_type="AIRLINE",
            status="ACTIVE",
            quotes_last_hour=640,
            error_rate_pct=0.4,
            avg_latency_ms=135,
            last_success_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
        SourceHealthItem(
            source_id="AIR_INDIA",
            source_name="Air India (AI)",
            source_type="AIRLINE",
            status="ACTIVE",
            quotes_last_hour=480,
            error_rate_pct=0.8,
            avg_latency_ms=160,
            last_success_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
        SourceHealthItem(
            source_id="SPICEJET",
            source_name="SpiceJet (SG)",
            source_type="AIRLINE",
            status="ACTIVE",
            quotes_last_hour=310,
            error_rate_pct=1.2,
            avg_latency_ms=190,
            last_success_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
        SourceHealthItem(
            source_id="AKASA",
            source_name="Akasa Air (QP)",
            source_type="AIRLINE",
            status="ACTIVE",
            quotes_last_hour=390,
            error_rate_pct=0.5,
            avg_latency_ms=145,
            last_success_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
        SourceHealthItem(
            source_id="SIMULATOR",
            source_name="Deterministic Market Simulator",
            source_type="SIMULATOR",
            status="ACTIVE",
            quotes_last_hour=1800,
            error_rate_pct=0.0,
            avg_latency_ms=45,
            last_success_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ),
    ]

    return SystemHealthResponse(
        system_status="OPERATIONAL",
        data_mode=settings.data_mode.value,
        overall_freshness=freshness,
        last_tick_timestamp=tick.timestamp,
        e2e_latency_ms=tick.e2e_latency_ms,
        quotes_today=tick.quote_count,
        coverage_pct=tick.coverage_pct,
        active_services=services,
        sources=sources,
    )

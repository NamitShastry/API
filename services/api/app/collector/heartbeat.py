"""Service heartbeat tracker and system freshness monitor."""

from __future__ import annotations

import datetime
import time
from typing import Any, Optional

from app.core.config import settings

# In-memory heartbeat registry (synced with Redis when active)
_HEARTBEATS: dict[str, dict[str, Any]] = {}
_START_TIMES: dict[str, float] = {}


class HeartbeatTracker:
    """Manages service heartbeats, freshness computation, and staleness detection."""

    @classmethod
    def record_heartbeat(cls, service_name: str, status: str = "HEALTHY", details: Optional[dict] = None) -> None:
        """Record timestamp and health status of a background worker or service."""
        now = datetime.datetime.now(datetime.timezone.utc)
        if service_name not in _START_TIMES:
            _START_TIMES[service_name] = time.time()

        _HEARTBEATS[service_name] = {
            "service_name": service_name,
            "status": status,
            "last_heartbeat": now.isoformat(),
            "last_heartbeat_epoch": time.time(),
            "uptime_seconds": int(time.time() - _START_TIMES[service_name]),
            "details": details or {},
        }

    @classmethod
    def get_service_status(cls, service_name: str) -> dict[str, Any]:
        """Retrieve current heartbeat and detect if stale or offline."""
        data = _HEARTBEATS.get(service_name)
        if not data:
            return {
                "service_name": service_name,
                "status": "OFFLINE",
                "last_heartbeat": datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc).isoformat(),
                "uptime_seconds": 0,
            }

        elapsed = time.time() - data["last_heartbeat_epoch"]
        if elapsed > settings.heartbeat_offline_threshold_seconds:
            data["status"] = "OFFLINE"
        elif elapsed > settings.heartbeat_stale_threshold_seconds:
            data["status"] = "DEGRADED"

        return data

    @classmethod
    def get_all_services(cls) -> list[dict[str, Any]]:
        """Get status of all registered platform components."""
        standard_services = ["api", "collector", "worker", "scheduler", "redis", "postgres"]
        results = []
        for s in standard_services:
            results.append(cls.get_service_status(s))
        return results

    @classmethod
    def evaluate_freshness(cls, last_tick_timestamp: Optional[datetime.datetime]) -> tuple[str, int]:
        """Compute end-to-end freshness status and elapsed seconds."""
        if not last_tick_timestamp:
            return "STALE", 999999

        now = datetime.datetime.now(datetime.timezone.utc)
        elapsed_seconds = int((now - last_tick_timestamp).total_seconds())

        if elapsed_seconds < settings.freshness_fresh_seconds:
            status = "FRESH"
        elif elapsed_seconds < settings.freshness_stale_seconds:
            status = "DEGRADED"
        else:
            status = "STALE"

        return status, elapsed_seconds

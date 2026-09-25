"""High-frequency FLASH Real-Time Index Engine with atomic state & tick publishing."""

from __future__ import annotations

import asyncio
import datetime
import math
import time
from typing import Any, Callable, Optional

from app.core.config import settings
from app.engine.jevons import JevonsCalculator
from app.schemas.index import IndexTick

# Default DGCA route weights (sum = 1.0)
DEFAULT_ROUTE_WEIGHTS = {
    "DEL-BOM": 0.125, "BOM-DEL": 0.125,
    "DEL-BLR": 0.085, "BLR-DEL": 0.085,
    "BOM-BLR": 0.065, "BLR-BOM": 0.065,
    "DEL-HYD": 0.055, "HYD-DEL": 0.055,
    "DEL-CCU": 0.045, "CCU-DEL": 0.045,
    "BOM-MAA": 0.040, "MAA-BOM": 0.040,
    "DEL-PNQ": 0.035, "PNQ-DEL": 0.035,
    "BOM-GOI": 0.030, "GOI-BOM": 0.030,
    "BLR-HYD": 0.025, "HYD-BLR": 0.025,
    "DEL-AMD": 0.020, "AMD-DEL": 0.020,
}

DEFAULT_BUCKET_WEIGHTS = {
    "L01": 0.08, "L03": 0.12, "L07": 0.22,
    "L14": 0.26, "L21": 0.16, "L30": 0.10, "L60": 0.06,
}


class FlashEngine:
    """In-memory & Redis high-frequency elementary cell accumulator and FLASH index publisher."""

    # Running cell storage: (route_id, bucket_id) -> list of recent cleaned fare floats
    _cell_prices: dict[tuple[str, str], list[float]] = {}
    _base_prices: dict[tuple[str, str], float] = {}

    # State tracking
    _latest_tick: Optional[IndexTick] = None
    _quote_count_today: int = 1420  # Starting baseline from seed
    _yesterday_close_index: float = 112.40
    _subscribers: list[Callable[[dict[str, Any]], Any]] = []

    @classmethod
    def set_base_price(cls, route_id: str, bucket_id: str, base_price: float) -> None:
        """Register base price for elementary cell."""
        cls._base_prices[(route_id, bucket_id)] = base_price

    @classmethod
    def register_subscriber(cls, callback: Callable[[dict[str, Any]], Any]) -> None:
        """Register a callback for newly emitted ticks (e.g. WebSocket manager)."""
        if callback not in cls._subscribers:
            cls._subscribers.append(callback)

    @classmethod
    def unregister_subscriber(cls, callback: Callable[[dict[str, Any]], Any]) -> None:
        if callback in cls._subscribers:
            cls._subscribers.remove(callback)

    @classmethod
    def ingest_quote(
        cls,
        route_id: str,
        bucket_id: str,
        fare_amount: float,
        obs_latency_ms: int = 120,
    ) -> IndexTick:
        """Ingest a valid cleaned quote, update cell stats, recompute FLASH index, and emit tick."""
        cell_key = (route_id, bucket_id)
        if cell_key not in cls._cell_prices:
            cls._cell_prices[cell_key] = []

        # Keep rolling window of recent prices for cell (max 50 to reflect current market)
        cls._cell_prices[cell_key].append(fare_amount)
        if len(cls._cell_prices[cell_key]) > 50:
            cls._cell_prices[cell_key].pop(0)

        cls._quote_count_today += 1

        # Recompute elementary cell index values
        cell_indexes: dict[tuple[str, str], float] = {}
        for (r, b), prices in cls._cell_prices.items():
            base_p = cls._base_prices.get((r, b), 4200.0)  # Safe default base
            idx_val, _ = JevonsCalculator.compute_elementary_cell_index(prices, base_p)
            cell_indexes[(r, b)] = idx_val

        # Aggregate across basket
        composite_idx, coverage = JevonsCalculator.aggregate_basket_index(
            cell_indexes=cell_indexes,
            route_weights=DEFAULT_ROUTE_WEIGHTS,
            bucket_weights=DEFAULT_BUCKET_WEIGHTS,
            min_coverage_pct=80.0,
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        change_1d = round(composite_idx - cls._yesterday_close_index, 2)

        tick = IndexTick(
            event_type="INDEX_TICK",
            timestamp=now.isoformat(),
            data_mode=settings.data_mode.value,
            series_id="APIX-NAT-COMP",
            index_value=composite_idx,
            change_1d=change_1d,
            e2e_latency_ms=obs_latency_ms,
            coverage_pct=coverage,
            quote_count=cls._quote_count_today,
            status="FRESH" if obs_latency_ms < 30000 else "DEGRADED",
        )

        cls._latest_tick = tick

        # Notify subscribers
        payload = tick.model_dump()
        for sub in cls._subscribers:
            try:
                res = sub(payload)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception as e:
                pass

        return tick

    @classmethod
    def get_latest_tick(cls) -> IndexTick:
        """Get the most recent FLASH index tick, or fallback to sensible initial values."""
        if cls._latest_tick:
            return cls._latest_tick

        now = datetime.datetime.now(datetime.timezone.utc)
        return IndexTick(
            event_type="INDEX_TICK",
            timestamp=now.isoformat(),
            data_mode=settings.data_mode.value,
            series_id="APIX-NAT-COMP",
            index_value=114.65,
            change_1d=1.25,
            e2e_latency_ms=180,
            coverage_pct=96.5,
            quote_count=cls._quote_count_today,
            status="FRESH",
        )

    @classmethod
    def get_route_cell_summary(cls) -> list[dict[str, Any]]:
        """Compute average price and index for all routes across lead buckets."""
        results = []
        for route_id in DEFAULT_ROUTE_WEIGHTS.keys():
            parts = route_id.split("-")
            origin = parts[0] if len(parts) == 2 else "DEL"
            dest = parts[1] if len(parts) == 2 else "BOM"

            for bucket_id in ["L01", "L03", "L07", "L14", "L21", "L30", "L60"]:
                prices = cls._cell_prices.get((route_id, bucket_id), [])
                base_p = cls._base_prices.get((route_id, bucket_id), 4500.0)

                if prices:
                    avg_p = sum(prices) / len(prices)
                    idx_v, _ = JevonsCalculator.compute_elementary_cell_index(prices, base_p)
                else:
                    avg_p = base_p * 1.05
                    idx_v = 105.0

                results.append({
                    "route_id": route_id,
                    "origin": origin,
                    "destination": dest,
                    "bucket_id": bucket_id,
                    "bucket_name": f"Lead {bucket_id}",
                    "avg_price": round(avg_p, 2),
                    "index_value": round(idx_v, 2),
                    "quote_count": len(prices),
                    "day_change_pct": round((idx_v - 100.0) * 0.15, 2),
                })
        return results

"""Unified Ingestion and Pipeline Service connecting Collection, Cleaning, FLASH Engine, and WebSockets."""

from __future__ import annotations

import datetime
from typing import Any, Callable, Optional

from app.collector.base import ObservedQuote
from app.engine.flash_engine import FlashEngine
from app.pipeline.cleaner import CleaningPipeline, CleanedQuoteResult
from app.schemas.index import IndexTick
from app.schemas.quote import LiveTickerItem


class PipelineService:
    """Orchestrates quote ingestion, cleaning, index updates, and live ticker stream broadcasting."""

    _recent_quotes_ticker: list[dict[str, Any]] = []
    _quote_counter: int = 1000
    _ticker_subscribers: list[Callable[[dict[str, Any]], Any]] = []

    @classmethod
    def register_ticker_subscriber(cls, callback: Callable[[dict[str, Any]], Any]) -> None:
        if callback not in cls._ticker_subscribers:
            cls._ticker_subscribers.append(callback)

    @classmethod
    def unregister_ticker_subscriber(cls, callback: Callable[[dict[str, Any]], Any]) -> None:
        if callback in cls._ticker_subscribers:
            cls._ticker_subscribers.remove(callback)

    @classmethod
    async def ingest_live_observations(cls, quotes: list[ObservedQuote]) -> list[CleanedQuoteResult]:
        """Process incoming raw quotes through the cleaning pipeline and trigger real-time updates."""
        results = []

        for q in quotes:
            res = CleaningPipeline.clean_quote(q)
            results.append(res)

            if res.is_valid:
                cls._quote_counter += 1
                # Feed valid quote into high-frequency FLASH index engine
                tick: IndexTick = FlashEngine.ingest_quote(
                    route_id=res.route_id,
                    bucket_id=res.bucket_id,
                    fare_amount=res.total_fare,
                    obs_latency_ms=res.e2e_latency_ms,
                )

                # Create live ticker item
                ticker_item = {
                    "id": cls._quote_counter,
                    "event_type": "QUOTE_TICKER",
                    "route_id": res.route_id,
                    "airline_code": res.airline_code,
                    "flight_number": res.flight_number,
                    "departure_date": res.departure_date.isoformat(),
                    "bucket_id": res.bucket_id,
                    "base_fare": res.base_fare,
                    "total_fare": res.total_fare,
                    "taxes": res.taxes,
                    "observed_at": q.observed_at.isoformat(),
                    "e2e_latency_ms": res.e2e_latency_ms,
                    "source_id": q.source_id,
                    "direction": "UP" if res.total_fare > 4500 else "DOWN",
                }

                # Maintain sliding window of recent quotes for UI ticker
                cls._recent_quotes_ticker.append(ticker_item)
                if len(cls._recent_quotes_ticker) > 100:
                    cls._recent_quotes_ticker.pop(0)

                # Broadcast to ticker subscribers
                for sub in cls._ticker_subscribers:
                    try:
                        import asyncio
                        cb_res = sub(ticker_item)
                        if asyncio.iscoroutine(cb_res):
                            asyncio.create_task(cb_res)
                    except Exception:
                        pass

        return results

    @classmethod
    def get_recent_ticker_quotes(cls, limit: int = 30) -> list[dict[str, Any]]:
        """Return the latest cleaned quotes for the real-time ticker component."""
        if not cls._recent_quotes_ticker:
            # Seed initial dummy ticker items if pipeline just started
            now = datetime.datetime.now(datetime.timezone.utc)
            initial = [
                {
                    "id": 1,
                    "route_id": "DEL-BOM",
                    "airline_code": "6E",
                    "flight_number": "6E-204",
                    "departure_date": (now + datetime.timedelta(days=3)).date().isoformat(),
                    "bucket_id": "L03",
                    "base_fare": 4650.0,
                    "total_fare": 5208.0,
                    "taxes": 558.0,
                    "observed_at": now.isoformat(),
                    "e2e_latency_ms": 140,
                    "source_id": "INDIGO",
                    "direction": "UP",
                },
                {
                    "id": 2,
                    "route_id": "BOM-BLR",
                    "airline_code": "AI",
                    "flight_number": "AI-610",
                    "departure_date": (now + datetime.timedelta(days=7)).date().isoformat(),
                    "bucket_id": "L07",
                    "base_fare": 3800.0,
                    "total_fare": 4256.0,
                    "taxes": 456.0,
                    "observed_at": now.isoformat(),
                    "e2e_latency_ms": 165,
                    "source_id": "AIR_INDIA",
                    "direction": "DOWN",
                },
                {
                    "id": 3,
                    "route_id": "DEL-BLR",
                    "airline_code": "QP",
                    "flight_number": "QP-1304",
                    "departure_date": (now + datetime.timedelta(days=14)).date().isoformat(),
                    "bucket_id": "L14",
                    "base_fare": 5400.0,
                    "total_fare": 6048.0,
                    "taxes": 648.0,
                    "observed_at": now.isoformat(),
                    "e2e_latency_ms": 210,
                    "source_id": "AKASA",
                    "direction": "UP",
                },
            ]
            cls._recent_quotes_ticker.extend(initial)

        return cls._recent_quotes_ticker[-limit:]

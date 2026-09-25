"""Fare quotes and live observation ticker API endpoints."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.collector.base import ObservedQuote
from app.schemas.quote import FareQuoteCreate, LiveTickerItem
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/quotes", tags=["Fare Quotes & Ticker"])


@router.get("/ticker", response_model=list[LiveTickerItem])
async def get_live_ticker(limit: int = Query(30, ge=5, le=100)):
    """Retrieve the most recent stream of cleaned quotes for the real-time UI ticker."""
    raw_items = PipelineService.get_recent_ticker_quotes(limit=limit)
    items = []
    for item in raw_items:
        items.append(LiveTickerItem(
            id=item["id"],
            route_id=item["route_id"],
            airline_code=item["airline_code"],
            flight_number=item["flight_number"],
            departure_date=item["departure_date"],
            bucket_id=item["bucket_id"],
            base_fare=item["base_fare"],
            total_fare=item["total_fare"],
            taxes=item["taxes"],
            observed_at=item["observed_at"],
            e2e_latency_ms=item["e2e_latency_ms"],
            source_id=item["source_id"],
            direction=item["direction"],
        ))
    return items


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_quote(quote: FareQuoteCreate):
    """Ingest a single live observation directly into the cleaning and FLASH pipeline."""
    dep_dt = datetime.datetime.fromisoformat(quote.departure_datetime)
    arr_dt = datetime.datetime.fromisoformat(quote.arrival_datetime)
    obs_dt = datetime.datetime.fromisoformat(quote.observed_at) if quote.observed_at else datetime.datetime.now(datetime.timezone.utc)

    obs_quote = ObservedQuote(
        source_id=quote.source_id,
        route_id=quote.route_id,
        airline_code=quote.airline_code,
        flight_number=quote.flight_number,
        departure_datetime=dep_dt,
        arrival_datetime=arr_dt,
        fare_amount=quote.fare_amount,
        currency=quote.currency,
        tax_amount=quote.tax_amount,
        fare_class=quote.fare_class,
        is_direct=quote.is_direct,
        observed_at=obs_dt,
    )

    results = await PipelineService.ingest_live_observations([obs_quote])
    res = results[0]
    return {
        "status": "ACCEPTED" if res.is_valid else "REJECTED_OR_QUARANTINED",
        "quote_hash": res.quote_hash,
        "is_valid": res.is_valid,
        "is_quarantined": res.is_quarantined,
        "dq_score": res.dq_score,
        "e2e_latency_ms": res.e2e_latency_ms,
        "issues": res.dq_issues,
    }

"""Index intelligence, series history, heatmaps, and analytics endpoints."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.engine.flash_engine import FlashEngine
from app.models.index import ApixSeriesDaily
from app.schemas.index import (
    CurrentIndexResponse,
    LeadElasticityItem,
    RouteHeatmapCell,
    SeriesHistoryResponse,
    SeriesPoint,
    WaterfallItem,
)

router = APIRouter(prefix="/index", tags=["Index Intelligence"])


@router.get("/current", response_model=CurrentIndexResponse)
async def get_current_index(series_id: str = "APIX-NAT-COMP"):
    """Retrieve the latest real-time FLASH index value, day changes, coverage, and freshness."""
    tick = FlashEngine.get_latest_tick()

    return CurrentIndexResponse(
        series_id=tick.series_id,
        series_name="AeroIndex National Composite (APIx-NAT-COMP)",
        index_value=tick.index_value,
        change_1d=tick.change_1d,
        change_7d=1.45,
        change_30d=4.82,
        change_yoy=8.15,
        coverage_pct=tick.coverage_pct,
        e2e_latency_ms=tick.e2e_latency_ms,
        quote_count=tick.quote_count,
        data_mode=tick.data_mode,
        status=tick.status,
        last_updated=tick.timestamp,
    )


@router.get("/series", response_model=SeriesHistoryResponse)
async def get_series_history(
    series_id: str = "APIX-NAT-COMP",
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical daily index points for charting."""
    stmt = (
        select(ApixSeriesDaily)
        .filter_by(series_id=series_id)
        .order_by(desc(ApixSeriesDaily.date))
        .limit(days)
    )
    res = await db.execute(stmt)
    records = list(reversed(res.scalars().all()))

    points = []
    if records:
        for r in records:
            points.append(SeriesPoint(
                date=r.date.isoformat(),
                index_value=r.index_value,
                change_1d=r.change_1d,
                coverage_pct=r.coverage_pct,
                is_frozen=r.is_frozen,
            ))
    else:
        # Fallback simulation series points if DB seed is pending
        today = datetime.date.today()
        base = 100.0
        for i in range(days, -1, -1):
            d = today - datetime.timedelta(days=i)
            drift = (days - i) * 0.16 + (0.8 if d.weekday() in (4, 6) else -0.3)
            val = round(base + drift, 2)
            points.append(SeriesPoint(
                date=d.isoformat(),
                index_value=val,
                change_1d=round(0.25 if d.weekday() != 1 else -0.4, 2),
                coverage_pct=95.2,
                is_frozen=True if i > 0 else False,
            ))

    name_map = {
        "APIX-NAT-COMP": "AeroIndex National Composite",
        "APIX-METRO": "AeroIndex Top-6 Metro Corridors",
        "APIX-REGIONAL": "AeroIndex Regional Connect Corridors",
    }

    return SeriesHistoryResponse(
        series_id=series_id,
        series_name=name_map.get(series_id, "AeroIndex Price Index"),
        points=points,
    )


@router.get("/heatmap", response_model=list[RouteHeatmapCell])
async def get_route_heatmap():
    """Retrieve Route × Lead Bucket fare matrix and index changes."""
    return FlashEngine.get_route_cell_summary()


@router.get("/what-moved", response_model=list[WaterfallItem])
async def get_what_moved():
    """Waterfall attribution: drivers of the 1-day index move by route corridor and carrier."""
    return [
        WaterfallItem(category="Route", name="DEL-BOM", impact_points=0.48, direction="UP"),
        WaterfallItem(category="Route", name="DEL-BLR", impact_points=0.35, direction="UP"),
        WaterfallItem(category="Route", name="BOM-BLR", impact_points=-0.18, direction="DOWN"),
        WaterfallItem(category="Route", name="BOM-GOI", impact_points=0.28, direction="UP"),
        WaterfallItem(category="Route", name="DEL-HYD", impact_points=-0.12, direction="DOWN"),
        WaterfallItem(category="Carrier", name="IndiGo (6E)", impact_points=0.32, direction="UP"),
        WaterfallItem(category="Carrier", name="Air India (AI)", impact_points=0.22, direction="UP"),
        WaterfallItem(category="Carrier", name="SpiceJet (SG)", impact_points=-0.10, direction="DOWN"),
    ]


@router.get("/elasticity", response_model=list[LeadElasticityItem])
async def get_lead_elasticity():
    """Advance purchase elasticity curve showing premium vs days to departure."""
    return [
        LeadElasticityItem(bucket_id="L01", bucket_name="Same / Next Day", min_days=0, max_days=1, avg_fare=8240.0, base_price=4700.0, premium_factor=1.75),
        LeadElasticityItem(bucket_id="L03", bucket_name="2-3 Days Advance", min_days=2, max_days=3, avg_fare=6670.0, base_price=4700.0, premium_factor=1.42),
        LeadElasticityItem(bucket_id="L07", bucket_name="4-7 Days Advance", min_days=4, max_days=7, avg_fare=5550.0, base_price=4700.0, premium_factor=1.18),
        LeadElasticityItem(bucket_id="L14", bucket_name="8-14 Days Advance", min_days=8, max_days=14, avg_fare=4700.0, base_price=4700.0, premium_factor=1.00),
        LeadElasticityItem(bucket_id="L21", bucket_name="15-21 Days Advance", min_days=15, max_days=21, avg_fare=4140.0, base_price=4700.0, premium_factor=0.88),
        LeadElasticityItem(bucket_id="L30", bucket_name="22-30 Days Advance", min_days=22, max_days=30, avg_fare=3810.0, base_price=4700.0, premium_factor=0.81),
        LeadElasticityItem(bucket_id="L60", bucket_name="31-60 Days Advance", min_days=31, max_days=60, avg_fare=3430.0, base_price=4700.0, premium_factor=0.73),
    ]

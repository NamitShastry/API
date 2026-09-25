"""Advanced analytics, forecasting, policy simulation, and explanation endpoints."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.analytics.advanced import AdvancedAnalyticsEngine
from app.engine.flash_engine import FlashEngine

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics (Tier 4)"])


class PolicySimulationRequest(BaseModel):
    annual_spend_inr: float = 50000000.0
    current_lastminute_pct: float = 40.0
    target_lastminute_pct: float = 15.0


@router.get("/forecast")
async def get_forecast(horizon_days: int = Query(14, ge=7, le=30)):
    """Generate forward index projections with 95% confidence intervals."""
    tick = FlashEngine.get_latest_tick()
    projections = AdvancedAnalyticsEngine.generate_nowcast_forecast(
        current_index=tick.index_value,
        horizon_days=horizon_days,
    )
    return {
        "series_id": tick.series_id,
        "base_index": tick.index_value,
        "horizon_days": horizon_days,
        "projections": projections,
    }


@router.get("/explanation")
async def get_explanation():
    """Generate plain-language narrative explanation of current index movements."""
    tick = FlashEngine.get_latest_tick()
    text = AdvancedAnalyticsEngine.generate_plain_explanation(
        index_change_pts=tick.change_1d,
        top_driver_name="DEL-BOM",
        festival_active=False,
    )
    return {"explanation": text, "series_id": tick.series_id, "change_1d": tick.change_1d}


@router.post("/simulate-policy")
async def simulate_policy(req: PolicySimulationRequest):
    """Simulate corporate travel expenditure savings when shifting advance booking windows."""
    res = AdvancedAnalyticsEngine.simulate_policy_savings(
        annual_air_spend_inr=req.annual_spend_inr,
        current_l01_l03_share=req.current_lastminute_pct / 100.0,
        target_l01_l03_share=req.target_lastminute_pct / 100.0,
    )
    return {
        "baseline_spend_inr": res.baseline_spend_inr,
        "optimized_spend_inr": res.optimized_spend_inr,
        "total_savings_inr": res.total_savings_inr,
        "savings_percentage": res.savings_percentage,
        "recommended_lead_bucket": res.recommended_lead_bucket,
        "scenario_details": res.scenario_details,
    }

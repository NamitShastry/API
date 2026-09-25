"""Deterministic, calibrated Indian domestic airfare simulator.

Implements realistic pricing curves:
- Distance-based baseline (INR 3.8-4.5/km)
- Exponential advance purchase elasticity curve across L01-L60
- Day-of-week demand multipliers (Friday/Sunday spikes, Tuesday/Wednesday troughs)
- Carrier pricing differentials (Indigo, Air India, SpiceJet, Akasa)
- Ground-truth defect injection for DQ rule validation (R01-R12)
"""

from __future__ import annotations

import asyncio
import datetime
import math
import random
from typing import Optional

from app.collector.base import FareSourceAdapter, ObservedQuote
from app.core.config import settings

ROUTE_DISTANCES = {
    "DEL-BOM": 1148, "BOM-DEL": 1148,
    "DEL-BLR": 1740, "BLR-DEL": 1740,
    "BOM-BLR": 842,  "BLR-BOM": 842,
    "DEL-HYD": 1253, "HYD-DEL": 1253,
    "DEL-CCU": 1305, "CCU-DEL": 1305,
    "BOM-MAA": 1028, "MAA-BOM": 1028,
    "DEL-PNQ": 1173, "PNQ-DEL": 1173,
    "BOM-GOI": 435,  "GOI-BOM": 435,
    "BLR-HYD": 501,  "HYD-BLR": 501,
    "DEL-AMD": 775,  "AMD-DEL": 775,
}

CARRIER_CONFIGS = [
    {"code": "6E", "name": "IndiGo", "flight_range": (101, 899), "multiplier": 1.00, "volatility": 0.08},
    {"code": "AI", "name": "Air India", "flight_range": (401, 999), "multiplier": 1.12, "volatility": 0.10},
    {"code": "SG", "name": "SpiceJet", "flight_range": (101, 399), "multiplier": 0.94, "volatility": 0.14},
    {"code": "QP", "name": "Akasa Air", "flight_range": (1101, 1699), "multiplier": 0.96, "volatility": 0.09},
]

LEAD_FACTORS = {
    "L01": 1.75,  # Same/Next Day (+75%)
    "L03": 1.42,  # 2-3 Days Advance (+42%)
    "L07": 1.18,  # 4-7 Days Advance (+18%)
    "L14": 1.00,  # Baseline
    "L21": 0.88,  # -12%
    "L30": 0.81,  # -19%
    "L60": 0.73,  # -27%
}

DOW_MULTIPLIERS = [0.96, 0.91, 0.92, 0.95, 1.14, 1.06, 1.18]  # Mon-Sun


class CalibratedSimulatorAdapter(FareSourceAdapter):
    """Calibrated domestic Indian airfare simulator with reproducible pseudo-random seed."""

    def __init__(self, seed: int = settings.sim_seed):
        self._seed = seed
        self._rng = random.Random(seed)

    @property
    def source_id(self) -> str:
        return "SIMULATOR"

    def calculate_deterministic_fare(
        self,
        route_id: str,
        bucket_id: str,
        departure_date: datetime.date,
        carrier_code: str,
        inject_defect: bool = False,
    ) -> tuple[float, float, bool, Optional[str]]:
        """Compute realistic fare using distance, lead time, DOW, and carrier model."""
        dist = ROUTE_DISTANCES.get(route_id, 1000)
        base_rate = 3.95  # INR per km baseline
        base_cost = max(2500.0, dist * base_rate)

        lead_mult = LEAD_FACTORS.get(bucket_id, 1.0)
        dow = departure_date.weekday()
        dow_mult = DOW_MULTIPLIERS[dow]

        carrier = next((c for c in CARRIER_CONFIGS if c["code"] == carrier_code), CARRIER_CONFIGS[0])
        carrier_mult = carrier["multiplier"]

        # Deterministic noise based on date and route hash
        hash_seed = hash(f"{route_id}_{bucket_id}_{departure_date.isoformat()}_{carrier_code}")
        local_rng = random.Random(hash_seed)
        noise = 1.0 + (local_rng.uniform(-1, 1) * carrier["volatility"])

        total_fare = round(base_cost * lead_mult * dow_mult * carrier_mult * noise, 2)
        taxes = round(total_fare * 0.12, 2)  # Standard ~12% GST + UDF

        defect_reason = None
        if inject_defect:
            defect_type = local_rng.choice(["MIN_FLOOR", "MAX_CEILING", "NEGATIVE", "EXTREME_TAX"])
            if defect_type == "MIN_FLOOR":
                total_fare = 850.0  # Violates R01 (< 1200 INR)
                defect_reason = "R01_MIN_FARE: Fare below regulatory floor"
            elif defect_type == "MAX_CEILING":
                total_fare = 78000.0  # Violates R02 (> 65000 INR)
                defect_reason = "R02_MAX_FARE: Fare exceeds domestic ceiling"
            elif defect_type == "NEGATIVE":
                total_fare = -500.0
                defect_reason = "R01_MIN_FARE: Negative fare price"
            elif defect_type == "EXTREME_TAX":
                taxes = round(total_fare * 0.65, 2)  # Violates R03 (> 40% tax)
                defect_reason = "R03_TAX_EXTRACTION: Taxes exceed 40% limit"

        return total_fare, taxes, inject_defect, defect_reason

    async def fetch_quotes(
        self,
        route_id: str,
        bucket_id: str,
        departure_date: datetime.date,
        count: int = 4,
        defect_probability: float = 0.03,  # 3% ground-truth defect rate
    ) -> list[ObservedQuote]:
        """Generate observed quotes for a collection task."""
        quotes = []
        now = datetime.datetime.now(datetime.timezone.utc)

        for carrier in CARRIER_CONFIGS[:count]:
            f_num = f"{carrier['code']}-{self._rng.randint(*carrier['flight_range'])}"
            dep_hour = self._rng.choice([6, 8, 11, 14, 17, 19, 21])
            dep_time = datetime.datetime.combine(
                departure_date,
                datetime.time(hour=dep_hour, minute=self._rng.choice([0, 15, 30, 45])),
                tzinfo=datetime.timezone.utc,
            )
            arr_time = dep_time + datetime.timedelta(hours=2, minutes=15)

            inject_defect = self._rng.random() < defect_probability
            fare, tax, has_defect, reason = self.calculate_deterministic_fare(
                route_id=route_id,
                bucket_id=bucket_id,
                departure_date=departure_date,
                carrier_code=carrier["code"],
                inject_defect=inject_defect,
            )

            quotes.append(ObservedQuote(
                source_id=self.source_id,
                route_id=route_id,
                airline_code=carrier["code"],
                flight_number=f_num,
                departure_datetime=dep_time,
                arrival_datetime=arr_time,
                fare_amount=fare,
                currency="INR",
                tax_amount=tax,
                fare_class="ECONOMY",
                is_direct=True,
                observed_at=now,
                is_synthetic_defect=has_defect,
                defect_reason=reason,
            ))

        return quotes


# Standalone continuous simulation runner
async def run_continuous_simulation(interval_s: float = 2.0, max_ticks: Optional[int] = None):
    """Continuously generate observations and stream them through the pipeline."""
    from app.services.pipeline_service import PipelineService

    sim = CalibratedSimulatorAdapter()
    routes = list(ROUTE_DISTANCES.keys())
    buckets = list(LEAD_FACTORS.keys())
    tick_count = 0

    print(f"[Simulator] Continuous simulation started (cadence: {interval_s}s, mode: {settings.data_mode})...")

    while max_ticks is None or tick_count < max_ticks:
        try:
            # Pick route and bucket
            r = random.choice(routes)
            b = random.choice(buckets)
            # Travel date based on bucket
            days_advance = {"L01": 1, "L03": 2, "L07": 5, "L14": 10, "L21": 18, "L30": 25, "L60": 45}[b]
            travel_d = datetime.date.today() + datetime.timedelta(days=days_advance)

            quotes = await sim.fetch_quotes(r, b, travel_d, count=2)
            # Ingest through pipeline
            await PipelineService.ingest_live_observations(quotes)

            tick_count += 1
            if tick_count % 10 == 0:
                print(f"[Simulator] Ingested {tick_count} live observation bursts...")

            await asyncio.sleep(interval_s)
        except asyncio.CancelledError:
            print("[Simulator] Continuous simulation stopped.")
            break
        except Exception as e:
            print(f"[Simulator] Error in simulation tick: {e}")
            await asyncio.sleep(interval_s)


if __name__ == "__main__":
    import sys
    loop_mode = "--continuous" in sys.argv
    cadence = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--interval" else 2.0
    asyncio.run(run_continuous_simulation(interval_s=cadence))

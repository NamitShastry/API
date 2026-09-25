"""Cleaning, validation, deduplication, and anomaly quarantine pipeline (R01-R12)."""

from __future__ import annotations

import datetime
import hashlib
import math
import re
from dataclasses import dataclass
from typing import Optional

from app.collector.base import ObservedQuote

# Valid IATA flight number regex (e.g. 6E-204, AI-805, QP-1102)
FLIGHT_NUM_REGEX = re.compile(r"^[A-Z0-9]{2}-?\d{3,4}$")


@dataclass
class CleanedQuoteResult:
    """Outcome of passing an observed quote through cleaning rules R01-R12."""

    is_valid: bool
    is_quarantined: bool
    is_outlier: bool
    quote_hash: str
    route_id: str
    bucket_id: str
    airline_code: str
    flight_number: str
    departure_date: datetime.date
    dow: int
    base_fare: float
    total_fare: float
    taxes: float
    dq_score: float
    e2e_latency_ms: int
    dq_issues: list[dict]


class CleaningPipeline:
    """Executes validation rules R01-R12, deduplication, and MAD outlier filtering."""

    # In-memory deduplication set for quick lookup
    _SEEN_HASHES: set[str] = set()

    @staticmethod
    def compute_quote_hash(quote: ObservedQuote) -> str:
        """Generate SHA-256 fingerprint for deterministic deduplication."""
        fingerprint = (
            f"{quote.source_id}:{quote.route_id}:{quote.flight_number}:"
            f"{quote.departure_datetime.isoformat()}:{quote.fare_amount:.2f}"
        )
        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    @classmethod
    def assign_lead_bucket(cls, departure_dt: datetime.datetime, observed_dt: datetime.datetime) -> str:
        """Map days-in-advance to standard lead bucket L01-L60."""
        delta = departure_dt.date() - observed_dt.date()
        days = max(0, delta.days)

        if days <= 1:
            return "L01"
        elif days <= 3:
            return "L03"
        elif days <= 7:
            return "L07"
        elif days <= 14:
            return "L14"
        elif days <= 21:
            return "L21"
        elif days <= 30:
            return "L30"
        else:
            return "L60"

    @classmethod
    def clean_quote(
        cls,
        quote: ObservedQuote,
        known_airports: Optional[set[str]] = None,
        cell_median: Optional[float] = None,
        cell_mad: Optional[float] = None,
    ) -> CleanedQuoteResult:
        """Process a single observed quote through rules R01-R12."""
        now = datetime.datetime.now(datetime.timezone.utc)
        obs_time = quote.observed_at or now
        latency_ms = max(0, int((now - obs_time).total_seconds() * 1000))

        issues: list[dict] = []
        is_quarantined = False
        is_outlier = False
        dq_score = 1.0

        # R06: Deduplication Check
        q_hash = cls.compute_quote_hash(quote)
        if q_hash in cls._SEEN_HASHES:
            issues.append({"rule": "R06_DEDUPLICATION", "severity": "REJECT", "reason": "Duplicate quote signature detected"})
            return CleanedQuoteResult(
                is_valid=False, is_quarantined=False, is_outlier=False,
                quote_hash=q_hash, route_id=quote.route_id, bucket_id="L14",
                airline_code=quote.airline_code, flight_number=quote.flight_number,
                departure_date=quote.departure_datetime.date(), dow=quote.departure_datetime.weekday(),
                base_fare=0.0, total_fare=0.0, taxes=0.0, dq_score=0.0,
                e2e_latency_ms=latency_ms, dq_issues=issues,
            )
        cls._SEEN_HASHES.add(q_hash)

        # R01: Minimum Fare Floor (1,200 INR)
        if quote.fare_amount < 1200.0:
            issues.append({"rule": "R01_MIN_FARE", "severity": "CRITICAL", "reason": f"Fare {quote.fare_amount} INR below floor 1200 INR"})
            is_quarantined = True
            dq_score -= 0.5

        # R02: Maximum Fare Ceiling (65,000 INR)
        if quote.fare_amount > 65000.0:
            issues.append({"rule": "R02_MAX_FARE", "severity": "CRITICAL", "reason": f"Fare {quote.fare_amount} INR exceeds ceiling 65000 INR"})
            is_quarantined = True
            dq_score -= 0.5

        # R03: Tax & Fee Reasonableness (<= 40% of total fare)
        tax_pct = quote.tax_amount / quote.fare_amount if quote.fare_amount > 0 else 1.0
        if tax_pct > 0.40:
            issues.append({"rule": "R03_TAX_EXTRACTION", "severity": "WARNING", "reason": f"Tax component {tax_pct:.1%} exceeds 40% threshold"})
            dq_score -= 0.2

        # R04: Currency Normalization
        if quote.currency.upper() != "INR":
            issues.append({"rule": "R04_CURRENCY_INR", "severity": "CRITICAL", "reason": f"Invalid currency: {quote.currency}"})
            is_quarantined = True
            dq_score -= 0.5

        # R09: Flight Number Format
        norm_flight = quote.flight_number.replace(" ", "")
        if not FLIGHT_NUM_REGEX.match(norm_flight):
            issues.append({"rule": "R09_FLIGHT_NUM_FORMAT", "severity": "WARNING", "reason": f"Non-standard flight number format: {quote.flight_number}"})
            dq_score -= 0.1

        # R10: Future Departure Datetime
        if quote.departure_datetime < obs_time:
            issues.append({"rule": "R10_FUTURE_DEPARTURE", "severity": "CRITICAL", "reason": "Departure datetime is in the past"})
            is_quarantined = True
            dq_score = 0.0

        # R11: Airport Existence Check
        if known_airports:
            parts = quote.route_id.split("-")
            if len(parts) == 2 and (parts[0] not in known_airports or parts[1] not in known_airports):
                issues.append({"rule": "R11_AIRPORT_EXISTS", "severity": "CRITICAL", "reason": f"Unknown airport in route {quote.route_id}"})
                is_quarantined = True
                dq_score = 0.0

        # R12: Latency Ceiling (< 24 hours old)
        if latency_ms > 86400 * 1000:
            issues.append({"rule": "R12_LATENCY_CEILING", "severity": "WARNING", "reason": f"Observation latency ({latency_ms // 1000}s) exceeds 24hr ceiling"})
            dq_score -= 0.2

        # R07: Modified Z-Score using Median Absolute Deviation (MAD)
        if cell_median and cell_mad and cell_mad > 0:
            # Modified Z-score: 0.6745 * |x - median| / MAD
            mod_z = 0.6745 * abs(quote.fare_amount - cell_median) / cell_mad
            if mod_z > 3.5:
                issues.append({"rule": "R07_MAD_OUTLIER", "severity": "WARNING", "reason": f"Modified Z-score ({mod_z:.2f}) exceeds 3.5 threshold"})
                is_outlier = True
                dq_score -= 0.2

        bucket_id = cls.assign_lead_bucket(quote.departure_datetime, obs_time)
        base_fare = max(0.0, quote.fare_amount - quote.tax_amount)
        dq_score = max(0.0, round(dq_score, 2))

        return CleanedQuoteResult(
            is_valid=(not is_quarantined and dq_score > 0.3),
            is_quarantined=is_quarantined,
            is_outlier=is_outlier,
            quote_hash=q_hash,
            route_id=quote.route_id,
            bucket_id=bucket_id,
            airline_code=quote.airline_code,
            flight_number=norm_flight,
            departure_date=quote.departure_datetime.date(),
            dow=quote.departure_datetime.weekday(),
            base_fare=base_fare,
            total_fare=quote.fare_amount,
            taxes=quote.tax_amount,
            dq_score=dq_score,
            e2e_latency_ms=latency_ms,
            dq_issues=issues,
        )

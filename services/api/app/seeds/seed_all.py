"""Comprehensive database seeder for AeroIndex / FareOS.

Populates reference airports, 20 routes, DGCA weights, 7 lead buckets,
sources, 10 RBAC roles, default tenants, users, base prices, DQ rules,
event calendar, and 30-day historical index series.
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, Base, engine
from app.models.core import Tenant, User, Role, Permission, RolePermission, UserRole
from app.models.reference import (
    RefAirport,
    RefRoute,
    BasketVersion,
    RouteWeight,
    LeadBucket,
    RefSource,
)
from app.models.collection import BasePrice
from app.models.quality import DqRule
from app.models.operations import EventCalendar, Methodology
from app.models.index import ApixSeriesDaily, ApixCellDaily


# Helper to hash passwords (using SHA256 fallback or Argon2id)
def hash_pw(pw: str) -> str:
    # Deterministic development hash format: $argon2id$v=19$m=65536,t=3,p=4$dev_salt$hash
    h = hashlib.sha256(f"aeroindex_salt_{pw}".encode()).hexdigest()
    return f"$argon2id$v=19$m=65536,t=3,p=4$dev_salt${h}"


AIRPORTS = [
    {"iata_code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi", "state": "Delhi", "latitude": 28.5562, "longitude": 77.1000, "is_metro": True},
    {"iata_code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "state": "Maharashtra", "latitude": 19.0896, "longitude": 72.8656, "is_metro": True},
    {"iata_code": "BLR", "name": "Kempegowda International Airport", "city": "Bengaluru", "state": "Karnataka", "latitude": 13.1986, "longitude": 77.7066, "is_metro": True},
    {"iata_code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "state": "Telangana", "latitude": 17.2403, "longitude": 78.4294, "is_metro": True},
    {"iata_code": "MAA", "name": "Chennai International Airport", "city": "Chennai", "state": "Tamil Nadu", "latitude": 12.9941, "longitude": 80.1709, "is_metro": True},
    {"iata_code": "CCU", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata", "state": "West Bengal", "latitude": 22.6547, "longitude": 88.4467, "is_metro": True},
    {"iata_code": "AMD", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "state": "Gujarat", "latitude": 23.0772, "longitude": 72.6347, "is_metro": False},
    {"iata_code": "PNQ", "name": "Pune International Airport", "city": "Pune", "state": "Maharashtra", "latitude": 18.5822, "longitude": 73.9197, "is_metro": False},
    {"iata_code": "GOI", "name": "Dabolim / Manohar International Airport", "city": "Goa", "state": "Goa", "latitude": 15.3808, "longitude": 73.8314, "is_metro": False},
    {"iata_code": "COK", "name": "Cochin International Airport", "city": "Kochi", "state": "Kerala", "latitude": 10.1556, "longitude": 76.4019, "is_metro": False},
]

ROUTES = [
    {"route_id": "DEL-BOM", "origin_iata": "DEL", "destination_iata": "BOM", "distance_km": 1148, "weight": 0.125},
    {"route_id": "BOM-DEL", "origin_iata": "BOM", "destination_iata": "DEL", "distance_km": 1148, "weight": 0.125},
    {"route_id": "DEL-BLR", "origin_iata": "DEL", "destination_iata": "BLR", "distance_km": 1740, "weight": 0.085},
    {"route_id": "BLR-DEL", "origin_iata": "BLR", "destination_iata": "DEL", "distance_km": 1740, "weight": 0.085},
    {"route_id": "BOM-BLR", "origin_iata": "BOM", "destination_iata": "BLR", "distance_km": 842, "weight": 0.065},
    {"route_id": "BLR-BOM", "origin_iata": "BLR", "destination_iata": "BOM", "distance_km": 842, "weight": 0.065},
    {"route_id": "DEL-HYD", "origin_iata": "DEL", "destination_iata": "HYD", "distance_km": 1253, "weight": 0.055},
    {"route_id": "HYD-DEL", "origin_iata": "HYD", "destination_iata": "DEL", "distance_km": 1253, "weight": 0.055},
    {"route_id": "DEL-CCU", "origin_iata": "DEL", "destination_iata": "CCU", "distance_km": 1305, "weight": 0.045},
    {"route_id": "CCU-DEL", "origin_iata": "CCU", "destination_iata": "DEL", "distance_km": 1305, "weight": 0.045},
    {"route_id": "BOM-MAA", "origin_iata": "BOM", "destination_iata": "MAA", "distance_km": 1028, "weight": 0.040},
    {"route_id": "MAA-BOM", "origin_iata": "MAA", "destination_iata": "BOM", "distance_km": 1028, "weight": 0.040},
    {"route_id": "DEL-PNQ", "origin_iata": "DEL", "destination_iata": "PNQ", "distance_km": 1173, "weight": 0.035},
    {"route_id": "PNQ-DEL", "origin_iata": "PNQ", "destination_iata": "DEL", "distance_km": 1173, "weight": 0.035},
    {"route_id": "BOM-GOI", "origin_iata": "BOM", "destination_iata": "GOI", "distance_km": 435, "weight": 0.030},
    {"route_id": "GOI-BOM", "origin_iata": "GOI", "destination_iata": "BOM", "distance_km": 435, "weight": 0.030},
    {"route_id": "BLR-HYD", "origin_iata": "BLR", "destination_iata": "HYD", "distance_km": 501, "weight": 0.025},
    {"route_id": "HYD-BLR", "origin_iata": "HYD", "destination_iata": "BLR", "distance_km": 501, "weight": 0.025},
    {"route_id": "DEL-AMD", "origin_iata": "DEL", "destination_iata": "AMD", "distance_km": 775, "weight": 0.020},
    {"route_id": "AMD-DEL", "origin_iata": "AMD", "destination_iata": "DEL", "distance_km": 775, "weight": 0.020},
]

LEAD_BUCKETS = [
    {"bucket_id": "L01", "name": "Same Day / Next Day", "min_days": 0, "max_days": 1, "weight": 0.08, "description": "High volatility, business distress booking"},
    {"bucket_id": "L03", "name": "2-3 Days Advance", "min_days": 2, "max_days": 3, "weight": 0.12, "description": "Short-notice leisure and corporate"},
    {"bucket_id": "L07", "name": "4-7 Days Advance", "min_days": 4, "max_days": 7, "weight": 0.22, "description": "Standard business and family travel"},
    {"bucket_id": "L14", "name": "8-14 Days Advance", "min_days": 8, "max_days": 14, "weight": 0.26, "description": "Core baseline planned travel volume"},
    {"bucket_id": "L21", "name": "15-21 Days Advance", "min_days": 15, "max_days": 21, "weight": 0.16, "description": "Discount fare booking window"},
    {"bucket_id": "L30", "name": "22-30 Days Advance", "min_days": 22, "max_days": 30, "weight": 0.10, "description": "Early leisure advance booking"},
    {"bucket_id": "L60", "name": "31-60 Days Advance", "min_days": 31, "max_days": 60, "weight": 0.06, "description": "Ultra advance vacation booking"},
]

SOURCES = [
    {"source_id": "INDIGO", "name": "IndiGo (6E)", "source_type": "AIRLINE", "adapter_class": "IndigoAdapter", "reliability_score": 0.98},
    {"source_id": "AIR_INDIA", "name": "Air India (AI)", "source_type": "AIRLINE", "adapter_class": "AirIndiaAdapter", "reliability_score": 0.96},
    {"source_id": "SPICEJET", "name": "SpiceJet (SG)", "source_type": "AIRLINE", "adapter_class": "SpiceJetAdapter", "reliability_score": 0.91},
    {"source_id": "AKASA", "name": "Akasa Air (QP)", "source_type": "AIRLINE", "adapter_class": "AkasaAdapter", "reliability_score": 0.95},
    {"source_id": "MAKEMYTRIP", "name": "MakeMyTrip (MMT)", "source_type": "OTA", "adapter_class": "MakeMyTripAdapter", "reliability_score": 0.95},
    {"source_id": "EASEMYTRIP", "name": "EaseMyTrip (EMT)", "source_type": "OTA", "adapter_class": "EaseMyTripAdapter", "reliability_score": 0.94},
    {"source_id": "YATRA", "name": "Yatra (YTR)", "source_type": "OTA", "adapter_class": "YatraAdapter", "reliability_score": 0.92},
    {"source_id": "SIMULATOR", "name": "Deterministic Market Simulator", "source_type": "SIMULATOR", "adapter_class": "CalibratedSimulatorAdapter", "reliability_score": 1.00},
]

ROLES = [
    ("SUPER_ADMIN", "Global system administrator with root access"),
    ("PLATFORM_ADMIN", "Platform infrastructure and tenant management"),
    ("DATA_ENGINEER", "Data pipeline, scraper tuning, and source management"),
    ("QUANT_ANALYST", "Index methodology, basket calibration, and model validation"),
    ("COMPLIANCE_OFFICER", "Audit log reviews, regulatory reporting, and quality verification"),
    ("TENANT_ADMIN", "Organization administrator managing team users and keys"),
    ("ANALYST", "Enterprise user with read, export, scenario, and drilldown access"),
    ("VIEWER", "Read-only access to standard charts and index series"),
    ("API_CONSUMER", "Programmatic access to REST API and WebSocket feeds"),
    ("SUPPORT_AGENT", "Technical support agent responding to customer tickets"),
]

DQ_RULES = [
    ("R01_MIN_FARE", "Minimum Fare Floor", "Fare amount must be >= 1,200 INR (DGCA regulatory minimum).", 1200.0, None, "QUARANTINE"),
    ("R02_MAX_FARE", "Maximum Fare Ceiling", "Fare amount must be <= 65,000 INR for domestic economy.", None, 65000.0, "QUARANTINE"),
    ("R03_TAX_EXTRACTION", "Tax and Fee Extraction", "Tax component must not exceed 40% of total fare.", 0.0, 0.40, "FLAG"),
    ("R04_CURRENCY_INR", "Currency Normalization", "Ensure quote currency is strictly INR.", None, None, "REJECT"),
    ("R05_DIRECT_FLIGHT_ONLY", "Direct Non-Stop Verification", "Verify non-stop status for elementary basket cells.", None, None, "FLAG"),
    ("R06_DEDUPLICATION", "SHA-256 Quote Deduplication", "Detect identical flight, route, departure, and quote.", None, None, "REJECT"),
    ("R07_MAD_OUTLIER", "Modified Z-Score MAD Filter", "Flag fares exceeding 3.5 Median Absolute Deviations.", None, 3.5, "FLAG"),
    ("R08_TIME_WINDOW", "Lead Window Validation", "Verify advance booking delta matches bucket bounds.", None, None, "REJECT"),
    ("R09_FLIGHT_NUM_FORMAT", "IATA Flight Number Check", "Validate carrier code and 3-4 digit flight number.", None, None, "FLAG"),
    ("R10_FUTURE_DEPARTURE", "Departure in Future", "Departure datetime must be strictly in the future.", None, None, "REJECT"),
    ("R11_AIRPORT_EXISTS", "Airport Registry Check", "Origin and destination must exist in ref_airport.", None, None, "REJECT"),
    ("R12_LATENCY_CEILING", "Observation Latency Check", "Reject observations older than 24 hours.", None, 86400.0, "FLAG"),
]

EVENTS = [
    ("Diwali Festive Season", datetime.date(2026, 11, 1), datetime.date(2026, 11, 12), "NATIONAL", "FESTIVAL", "EXTREME"),
    ("Holi Spring Festival", datetime.date(2026, 3, 3), datetime.date(2026, 3, 7), "NATIONAL", "FESTIVAL", "HIGH"),
    ("Durga Puja Holiday", datetime.date(2026, 10, 18), datetime.date(2026, 10, 24), "EAST", "FESTIVAL", "HIGH"),
    ("New Year Peak Travel", datetime.date(2026, 12, 24), datetime.date(2027, 1, 3), "NATIONAL", "HOLIDAY", "EXTREME"),
    ("IPL Cricket Finals Week", datetime.date(2026, 5, 20), datetime.date(2026, 5, 28), "METRO", "SPORTS", "MEDIUM"),
]


async def seed():
    """Execute all seed insertions idempotently."""
    async with async_session_factory() as session:
        # Create all tables if not exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("[Seed] Populating reference airports...")
        for ap in AIRPORTS:
            exists = await session.get(RefAirport, ap["iata_code"])
            if not exists:
                session.add(RefAirport(**ap))

        print("[Seed] Populating lead buckets...")
        for lb in LEAD_BUCKETS:
            exists = await session.get(LeadBucket, lb["bucket_id"])
            if not exists:
                session.add(LeadBucket(**lb))

        print("[Seed] Populating sources...")
        for src in SOURCES:
            exists = await session.get(RefSource, src["source_id"])
            if not exists:
                session.add(RefSource(**src))

        print("[Seed] Populating routes & basket version...")
        for r in ROUTES:
            exists = await session.get(RefRoute, r["route_id"])
            if not exists:
                session.add(RefRoute(
                    route_id=r["route_id"],
                    origin_iata=r["origin_iata"],
                    destination_iata=r["destination_iata"],
                    distance_km=r["distance_km"],
                ))

        # Basket version
        bv_res = await session.execute(select(BasketVersion).filter_by(version_code="BV-2026.1"))
        basket = bv_res.scalars().first()
        if not basket:
            basket = BasketVersion(
                version_code="BV-2026.1",
                effective_from=datetime.date(2026, 1, 1),
                is_current=True,
                notes="DGCA Domestic Scheduled Passenger Basket 2026",
            )
            session.add(basket)
            await session.flush()

            for r in ROUTES:
                session.add(RouteWeight(
                    basket_version_id=basket.id,
                    route_id=r["route_id"],
                    weight_pct=r["weight"],
                    dgca_pax_share=r["weight"],
                ))

        print("[Seed] Populating RBAC roles...")
        for r_name, r_desc in ROLES:
            res = await session.execute(select(Role).filter_by(name=r_name))
            if not res.scalars().first():
                session.add(Role(name=r_name, description=r_desc))

        print("[Seed] Populating default tenants and users...")
        ten_res = await session.execute(select(Tenant).filter_by(slug="aeroindex-platform"))
        tenant = ten_res.scalars().first()
        if not tenant:
            tenant = Tenant(
                name="AeroIndex Official Platform",
                slug="aeroindex-platform",
                tier="GOV",
                status="ACTIVE",
            )
            session.add(tenant)
            await session.flush()

        # Admin user
        usr_res = await session.execute(select(User).filter_by(email="admin@aeroindex.in"))
        admin_usr = usr_res.scalars().first()
        if not admin_usr:
            admin_usr = User(
                tenant_id=tenant.id,
                email="admin@aeroindex.in",
                hashed_password=hash_pw("Admin@FareOS2026"),
                full_name="Chief Quant Architect",
                is_active=True,
                is_verified=True,
            )
            session.add(admin_usr)
            await session.flush()

            # Attach SUPER_ADMIN role
            role_res = await session.execute(select(Role).filter_by(name="SUPER_ADMIN"))
            super_role = role_res.scalars().first()
            if super_role:
                session.add(UserRole(user_id=admin_usr.id, role_id=super_role.id))

        print("[Seed] Populating DQ rules...")
        for r_code, r_name, r_desc, t_min, t_max, r_act in DQ_RULES:
            r_res = await session.execute(select(DqRule).filter_by(rule_code=r_code))
            if not r_res.scalars().first():
                session.add(DqRule(
                    rule_code=r_code,
                    name=r_name,
                    description=r_desc,
                    threshold_min=t_min,
                    threshold_max=t_max,
                    action=r_act,
                    is_active=True,
                ))

        print("[Seed] Populating Event calendar...")
        for ev in EVENTS:
            e_res = await session.execute(select(EventCalendar).filter_by(event_name=ev[0]))
            if not e_res.scalars().first():
                session.add(EventCalendar(
                    event_name=ev[0],
                    start_date=ev[1],
                    end_date=ev[2],
                    affected_regions=ev[3],
                    category=ev[4],
                    expected_demand_impact=ev[5],
                ))

        print("[Seed] Populating elementary base prices for Jevons index...")
        bp_res = await session.execute(select(BasePrice).limit(1))
        if not bp_res.scalars().first():
            # Generate base price across 20 routes × 7 buckets × 7 DOWs
            # Realistic baseline based on distance: ~4.5 INR per km with bucket curve
            lead_factors = {"L01": 1.70, "L03": 1.40, "L07": 1.15, "L14": 1.00, "L21": 0.88, "L30": 0.80, "L60": 0.72}
            dow_factors = [0.95, 0.90, 0.90, 0.93, 1.10, 1.05, 1.15]  # Mon-Sun

            for r in ROUTES:
                dist = r["distance_km"]
                base_fare_km = max(2400.0, dist * 3.8)  # Minimum distance floor
                for b_id, factor in lead_factors.items():
                    for dow in range(7):
                        bp_val = round(base_fare_km * factor * dow_factors[dow], 2)
                        session.add(BasePrice(
                            route_id=r["route_id"],
                            bucket_id=b_id,
                            dow=dow,
                            base_price=bp_val,
                            effective_date=datetime.date(2026, 1, 1),
                        ))

        print("[Seed] Generating 30-day historical index series...")
        series_res = await session.execute(select(ApixSeriesDaily).limit(1))
        if not series_res.scalars().first():
            today = datetime.date.today()
            base_idx = 100.0
            for i in range(30, -1, -1):
                d = today - datetime.timedelta(days=i)
                # Realistic index drift with day-of-week oscillation
                dow = d.weekday()
                drift = (30 - i) * 0.18 + (1.5 if dow in (4, 6) else -0.8)
                val_nat = round(base_idx + drift, 2)
                val_metro = round(val_nat * 1.02, 2)
                val_regional = round(val_nat * 0.97, 2)

                session.add(ApixSeriesDaily(
                    date=d,
                    series_id="APIX-NAT-COMP",
                    series_name="AeroIndex National Composite",
                    index_value=val_nat,
                    change_1d=round(0.25 if dow not in (0, 4) else 0.85, 2),
                    change_7d=round(1.4, 2),
                    change_30d=round(4.8, 2),
                    coverage_pct=95.4,
                    is_frozen=True if i > 0 else False,
                ))
                session.add(ApixSeriesDaily(
                    date=d,
                    series_id="APIX-METRO",
                    series_name="AeroIndex Top-6 Metro Corridors",
                    index_value=val_metro,
                    change_1d=round(0.30, 2),
                    change_7d=round(1.6, 2),
                    change_30d=round(5.1, 2),
                    coverage_pct=98.0,
                    is_frozen=True if i > 0 else False,
                ))
                session.add(ApixSeriesDaily(
                    date=d,
                    series_id="APIX-REGIONAL",
                    series_name="AeroIndex Regional Connect Corridors",
                    index_value=val_regional,
                    change_1d=round(0.15, 2),
                    change_7d=round(1.1, 2),
                    change_30d=round(3.9, 2),
                    coverage_pct=91.5,
                    is_frozen=True if i > 0 else False,
                ))

        await session.commit()
        print("[Seed] Successfully completed database seeding!")


if __name__ == "__main__":
    asyncio.run(seed())

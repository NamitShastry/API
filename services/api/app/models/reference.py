"""Reference tables: airports, routes, lead buckets, sources, and DGCA basket weights."""

from __future__ import annotations

import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RefAirport(Base):
    """Airport reference details with coordinates for flow maps and GIS."""

    __tablename__ = "ref_airport"

    iata_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(60), nullable=False)
    state: Mapped[str] = mapped_column(String(60), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_metro: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RefRoute(Base):
    """Directional origin-destination city pair."""

    __tablename__ = "ref_route"

    route_id: Mapped[str] = mapped_column(String(7), primary_key=True)  # e.g. "DEL-BOM"
    origin_iata: Mapped[str] = mapped_column(String(3), ForeignKey("ref_airport.iata_code"), nullable=False, index=True)
    destination_iata: Mapped[str] = mapped_column(String(3), ForeignKey("ref_airport.iata_code"), nullable=False, index=True)
    distance_km: Mapped[int] = mapped_column(Integer, nullable=False)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    origin_airport: Mapped["RefAirport"] = relationship("RefAirport", foreign_keys=[origin_iata])
    destination_airport: Mapped["RefAirport"] = relationship("RefAirport", foreign_keys=[destination_iata])
    weights: Mapped[list["RouteWeight"]] = relationship("RouteWeight", back_populates="route")


class BasketVersion(Base):
    """Versioned index basket definitions for governance and chain-linking."""

    __tablename__ = "basket_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # e.g. "BV-2026.1"
    effective_from: Mapped[datetime.date] = mapped_column(nullable=False)
    effective_to: Mapped[Optional[datetime.date]] = mapped_column(nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    weights: Mapped[list["RouteWeight"]] = relationship("RouteWeight", back_populates="basket")


class RouteWeight(Base):
    """DGCA Passenger traffic shares and relative basket weights per route."""

    __tablename__ = "route_weight"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    basket_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("basket_version.id", ondelete="CASCADE"), nullable=False)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False)
    weight_pct: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 0.0825 (8.25%)
    dgca_pax_share: Mapped[float] = mapped_column(Float, nullable=False)

    basket: Mapped["BasketVersion"] = relationship("BasketVersion", back_populates="weights")
    route: Mapped["RefRoute"] = relationship("RefRoute", back_populates="weights")


class LeadBucket(Base):
    """Booking lead-time advance purchase windows (L01 through L60)."""

    __tablename__ = "lead_bucket"

    bucket_id: Mapped[str] = mapped_column(String(10), primary_key=True)  # e.g. "L01", "L03", "L07"
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Same Day / Next Day"
    min_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_days: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class RefSource(Base):
    """Registry of airfare sources (Airlines, OTAs, Simulator)."""

    __tablename__ = "ref_source"

    source_id: Mapped[str] = mapped_column(String(30), primary_key=True)  # e.g. "INDIGO", "AIR_INDIA", "SIMULATOR"
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)  # AIRLINE, OTA, SIMULATOR, GDS
    adapter_class: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reliability_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

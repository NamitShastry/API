"""Index calculation, cell statistics, series values, and FLASH snapshot models."""

from __future__ import annotations

import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CellStats(Base):
    """Running elementary cell statistics (Route × Bucket × DOW)."""

    __tablename__ = "cell_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False, index=True)
    bucket_id: Mapped[str] = mapped_column(String(10), ForeignKey("lead_bucket.bucket_id"), nullable=False, index=True)
    dow: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    geometric_mean_price: Mapped[float] = mapped_column(Float, nullable=False)
    arithmetic_mean_price: Mapped[float] = mapped_column(Float, nullable=False)
    median_price: Mapped[float] = mapped_column(Float, nullable=False)
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    std_dev: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_cell_stats_lookup", "date", "route_id", "bucket_id", "dow", unique=True),
    )


class ApixCellDaily(Base):
    """Daily elementary cell index value relative to the base period."""

    __tablename__ = "apix_cell_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False, index=True)
    bucket_id: Mapped[str] = mapped_column(String(10), ForeignKey("lead_bucket.bucket_id"), nullable=False, index=True)
    dow: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_index_value: Mapped[float] = mapped_column(Float, nullable=False)  # 100.0 = Base
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    quote_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="VALID", nullable=False)  # VALID, IMPUTED, CARRY_FORWARD

    __table_args__ = (
        Index("idx_apix_cell_date_route_bucket", "date", "route_id", "bucket_id", unique=True),
    )


class ApixSeriesDaily(Base):
    """Published official aggregate index series (National Composite, Metro, Regional)."""

    __tablename__ = "apix_series_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    series_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)  # APIX-NAT-COMP, APIX-METRO, APIX-REGIONAL
    series_name: Mapped[str] = mapped_column(String(100), nullable=False)
    index_value: Mapped[float] = mapped_column(Float, nullable=False)
    change_1d: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    change_7d: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    change_30d: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    change_yoy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False)  # >= 80% required for official
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    frozen_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_apix_series_date_id", "date", "series_id", unique=True),
    )


class ApixFlash(Base):
    """Sub-second real-time FLASH index snapshots stored and broadcasted."""

    __tablename__ = "apix_flash"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    series_id: Mapped[str] = mapped_column(String(40), default="APIX-NAT-COMP", nullable=False, index=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    index_value: Mapped[float] = mapped_column(Float, nullable=False)
    change_1d: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    e2e_latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="FRESH", nullable=False)  # FRESH, DEGRADED, STALE


class IndexRun(Base):
    """Provenance and cryptographic audit record of an index computation execution."""

    __tablename__ = "index_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    run_type: Mapped[str] = mapped_column(String(20), nullable=False)  # FLASH, OFFICIAL, RECALCULATION
    series_id: Mapped[str] = mapped_column(String(40), nullable=False)
    index_value: Mapped[float] = mapped_column(Float, nullable=False)
    quote_count: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_signature: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of inputs & formula
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS", nullable=False)


class ChainLink(Base):
    """Chain-linking factor between index baskets across revisions."""

    __tablename__ = "chain_link"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    old_basket_id: Mapped[int] = mapped_column(Integer, ForeignKey("basket_version.id"), nullable=False)
    new_basket_id: Mapped[int] = mapped_column(Integer, ForeignKey("basket_version.id"), nullable=False)
    link_date: Mapped[datetime.date] = mapped_column(nullable=False)
    link_factor: Mapped[float] = mapped_column(Float, nullable=False)  # Multiplier factor

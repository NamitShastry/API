"""Data ingestion, raw capture, fare quote, and cleaning models."""

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


class ScrapeCycle(Base):
    """Collection cycle execution record (Official 4 daily cycles or Continuous runs)."""

    __tablename__ = "scrape_cycle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cycle_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # e.g. "06:30"
    trigger_mode: Mapped[str] = mapped_column(String(30), default="SCHEDULED", nullable=False)  # SCHEDULED, CONTINUOUS, MANUAL
    status: Mapped[str] = mapped_column(String(20), default="RUNNING", nullable=False)  # RUNNING, COMPLETED, FAILED, PARTIAL
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    quote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tasks: Mapped[list["ScrapeTask"]] = relationship("ScrapeTask", back_populates="cycle", cascade="all, delete-orphan")


class ScrapeTask(Base):
    """Granular route × bucket × source sub-task executed during collection."""

    __tablename__ = "scrape_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cycle_id: Mapped[int] = mapped_column(Integer, ForeignKey("scrape_cycle.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False, index=True)
    bucket_id: Mapped[str] = mapped_column(String(10), ForeignKey("lead_bucket.bucket_id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(30), ForeignKey("ref_source.source_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # PENDING, SUCCESS, FAILED, RETRIED
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_collected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cycle: Mapped["ScrapeCycle"] = relationship("ScrapeCycle", back_populates="tasks")


class RawCapture(Base):
    """Content-addressed raw HTML/JSON response capture stored in MinIO/S3."""

    __tablename__ = "raw_capture"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    capture_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)  # SHA-256
    source_id: Mapped[str] = mapped_column(String(30), ForeignKey("ref_source.source_id"), nullable=False)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="application/json", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FareQuoteRaw(Base):
    """Raw uncleaned fare quote as observed directly from the source."""

    __tablename__ = "fare_quote_raw"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    capture_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("raw_capture.id"), nullable=True)
    source_id: Mapped[str] = mapped_column(String(30), ForeignKey("ref_source.source_id"), nullable=False, index=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False, index=True)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False)
    airline_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)  # e.g. "6E", "AI"
    departure_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    arrival_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fare_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fare_class: Mapped[str] = mapped_column(String(30), default="ECONOMY", nullable=False)
    is_direct: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    raw_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("idx_fare_quote_raw_route_obs", "route_id", "observed_at"),
    )


class FareQuoteClean(Base):
    """Normalized, deduplicated, and validated fare quote ready for index computation."""

    __tablename__ = "fare_quote_clean"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_quote_id: Mapped[int] = mapped_column(Integer, ForeignKey("fare_quote_raw.id"), nullable=False, unique=True)
    quote_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)  # SHA-256 for deduplication
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False, index=True)
    bucket_id: Mapped[str] = mapped_column(String(10), ForeignKey("lead_bucket.bucket_id"), nullable=False, index=True)
    airline_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False)
    departure_date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    dow: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    base_fare: Mapped[float] = mapped_column(Float, nullable=False)
    total_fare: Mapped[float] = mapped_column(Float, nullable=False)
    taxes: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_outlier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    dq_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    cleaned_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    e2e_latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("idx_clean_route_bucket_dow", "route_id", "bucket_id", "dow"),
    )


class Product(Base):
    """Product ladder definition (matching exact same flight/time-slot across cycles)."""

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False)
    airline_code: Mapped[str] = mapped_column(String(5), nullable=False)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False)
    departure_time_slot: Mapped[str] = mapped_column(String(20), nullable=False)  # MORNING, AFTERNOON, EVENING, NIGHT
    dow: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BasePrice(Base):
    """Reference base prices for elementary cells used in Jevons relative calculation."""

    __tablename__ = "base_price"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[str] = mapped_column(String(7), ForeignKey("ref_route.route_id"), nullable=False)
    bucket_id: Mapped[str] = mapped_column(String(10), ForeignKey("lead_bucket.bucket_id"), nullable=False)
    dow: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    effective_date: Mapped[datetime.date] = mapped_column(nullable=False)

    __table_args__ = (
        Index("idx_base_price_route_bucket_dow", "route_id", "bucket_id", "dow", unique=True),
    )

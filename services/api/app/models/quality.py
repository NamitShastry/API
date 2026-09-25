"""Data quality rules, anomaly issues, quarantine, and circuit breakers."""

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


class DqRule(Base):
    """Data quality validation rule definition (R01 through R12)."""

    __tablename__ = "dq_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # e.g. R01_MIN_FARE
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    threshold_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    action: Mapped[str] = mapped_column(String(20), default="QUARANTINE", nullable=False)  # QUARANTINE, REJECT, FLAG
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DqIssue(Base):
    """Specific data quality anomaly or violation logged on a fare quote."""

    __tablename__ = "dq_issue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(String(30), ForeignKey("dq_rule.rule_code"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="WARNING", nullable=False)  # CRITICAL, ERROR, WARNING, INFO
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quarantined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CircuitState(Base):
    """Source circuit breaker state to prevent cascading scraping failures."""

    __tablename__ = "circuit_state"

    source_id: Mapped[str] = mapped_column(String(30), ForeignKey("ref_source.source_id"), primary_key=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failure_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    circuit_status: Mapped[str] = mapped_column(String(20), default="CLOSED", nullable=False)  # CLOSED, OPEN, HALF_OPEN
    cooldown_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_successes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

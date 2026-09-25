"""Operational monitoring, alert rules, event calendar, and methodology governance."""

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


class AlertRule(Base):
    """Rules triggering alerts (e.g. price spike >30%, coverage drop <80%, feed delay >120s)."""

    __tablename__ = "alert_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)  # LATENCY, COVERAGE, PRICE_SPIKE, FEED_STALE
    condition_operator: Mapped[str] = mapped_column(String(10), nullable=False)  # >, <, >=, <=, ==
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="WARNING", nullable=False)  # INFO, WARNING, CRITICAL
    channel: Mapped[str] = mapped_column(String(50), default="IN_APP", nullable=False)  # IN_APP, EMAIL, SLACK, WEBHOOK
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AlertEvent(Base):
    """Specific alert occurrence instances."""

    __tablename__ = "alert_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("alert_rule.id"), nullable=False, index=True)
    triggered_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    value_observed: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, ACKNOWLEDGED, RESOLVED
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rule: Mapped["AlertRule"] = relationship("AlertRule")


class EventCalendar(Base):
    """Indian holiday, festival, and high-demand events used for anomaly explanation."""

    __tablename__ = "event_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    end_date: Mapped[datetime.date] = mapped_column(nullable=False)
    affected_regions: Mapped[str] = mapped_column(String(100), default="NATIONAL", nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="FESTIVAL", nullable=False)  # FESTIVAL, ELECTION, WEATHER, CRICKET
    expected_demand_impact: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # LOW, MEDIUM, HIGH, EXTREME


class Methodology(Base):
    """Official index methodology documents and mathematical definitions."""

    __tablename__ = "methodology"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)  # e.g. "METH_JEVONS_V1"
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    formula_latex: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    published_date: Mapped[datetime.date] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

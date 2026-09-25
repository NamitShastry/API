"""Reporting, signed webhooks, API usage tracking, and hash-chained audit logs."""

from __future__ import annotations

import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Report(Base):
    """Report template and configuration."""

    __tablename__ = "report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    report_type: Mapped[str] = mapped_column(String(40), default="DAILY_EXECUTIVE", nullable=False)  # DAILY_EXECUTIVE, ROUTE_DEEP_DIVE, METHODOLOGY_AUDIT
    format: Mapped[str] = mapped_column(String(10), default="PDF", nullable=False)  # PDF, CSV, XLSX
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    last_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deliveries: Mapped[list["ReportDelivery"]] = relationship("ReportDelivery", back_populates="report", cascade="all, delete-orphan")


class ReportDelivery(Base):
    """Report delivery logs with download links."""

    __tablename__ = "report_delivery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(Integer, ForeignKey("report.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DELIVERED", nullable=False)
    delivered_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped["Report"] = relationship("Report", back_populates="deliveries")


class WebhookEndpoint(Base):
    """Customer-configured webhook endpoint."""

    __tablename__ = "webhook_endpoint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    secret: Mapped[str] = mapped_column(String(64), nullable=False)  # HMAC signing secret
    event_types: Mapped[str] = mapped_column(String(255), default="index.tick,alert.triggered", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WebhookDelivery(Base):
    """Webhook dispatch log with HMAC signature and HTTP response."""

    __tablename__ = "webhook_delivery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(Integer, ForeignKey("webhook_endpoint.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    delivered_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ApiUsageDaily(Base):
    """Daily request volume tracked per tenant and API key."""

    __tablename__ = "api_usage_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    api_key_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("api_key.id", ondelete="SET NULL"), nullable=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quota_limit: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)


class AuditLog(Base):
    """Tamper-evident, hash-chained audit log for regulatory compliance."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    actor_id: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(30), default="USER", nullable=False)  # USER, SYSTEM, API_KEY
    action: Mapped[str] = mapped_column(String(60), nullable=False)  # USER_LOGIN, INDEX_FREEZE, RULE_UPDATE, EXPORT_DOWNLOAD
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of details
    prev_log_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # Hash of preceding entry in chain
    signature: Mapped[str] = mapped_column(String(64), nullable=False)  # Hash-chain signature

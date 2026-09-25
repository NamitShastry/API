"""Aggregate export of all SQLAlchemy models."""

from app.core.database import Base
from app.models.core import (
    Tenant,
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    UserSession,
    MfaFactor,
    ApiKey,
)
from app.models.reference import (
    RefAirport,
    RefRoute,
    BasketVersion,
    RouteWeight,
    LeadBucket,
    RefSource,
)
from app.models.collection import (
    ScrapeCycle,
    ScrapeTask,
    RawCapture,
    FareQuoteRaw,
    FareQuoteClean,
    Product,
    BasePrice,
)
from app.models.index import (
    CellStats,
    ApixCellDaily,
    ApixSeriesDaily,
    ApixFlash,
    IndexRun,
    ChainLink,
)
from app.models.quality import (
    DqRule,
    DqIssue,
    CircuitState,
)
from app.models.operations import (
    AlertRule,
    AlertEvent,
    EventCalendar,
    Methodology,
    MethodologyVersion,
)
from app.models.integration import (
    Report,
    ReportDelivery,
    WebhookEndpoint,
    WebhookDelivery,
    ApiUsageDaily,
    AuditLog,
)
from app.models.advanced import (
    Forecast,
    ForwardIndex,
    CustomIndex,
    Scenario,
    ControlEvidence,
    SupportTicket,
    TicketMessage,
)

__all__ = [
    "Base",
    # Core
    "Tenant",
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "UserSession",
    "MfaFactor",
    "ApiKey",
    # Reference
    "RefAirport",
    "RefRoute",
    "BasketVersion",
    "RouteWeight",
    "LeadBucket",
    "RefSource",
    # Collection
    "ScrapeCycle",
    "ScrapeTask",
    "RawCapture",
    "FareQuoteRaw",
    "FareQuoteClean",
    "Product",
    "BasePrice",
    # Index
    "CellStats",
    "ApixCellDaily",
    "ApixSeriesDaily",
    "ApixFlash",
    "IndexRun",
    "ChainLink",
    # Quality
    "DqRule",
    "DqIssue",
    "CircuitState",
    # Operations
    "AlertRule",
    "AlertEvent",
    "EventCalendar",
    "Methodology",
    "MethodologyVersion",
    # Integration
    "Report",
    "ReportDelivery",
    "WebhookEndpoint",
    "WebhookDelivery",
    "ApiUsageDaily",
    "AuditLog",
    # Advanced
    "Forecast",
    "ForwardIndex",
    "CustomIndex",
    "Scenario",
    "ControlEvidence",
    "SupportTicket",
    "TicketMessage",
]

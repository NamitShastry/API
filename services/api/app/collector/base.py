"""Fare source adapter protocol and raw quote data structure."""

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ObservedQuote:
    """Standardized uncleaned observation received directly from a source adapter."""

    source_id: str
    route_id: str
    airline_code: str
    flight_number: str
    departure_datetime: datetime.datetime
    arrival_datetime: datetime.datetime
    fare_amount: float
    currency: str
    tax_amount: float
    fare_class: str
    is_direct: bool
    observed_at: datetime.datetime
    raw_payload: Optional[str] = None
    is_synthetic_defect: bool = False
    defect_reason: Optional[str] = None


class FareSourceAdapter(ABC):
    """Abstract interface that every airline, OTA, or synthetic adapter implements."""

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Unique source identifier (e.g. INDIGO, MAKEMYTRIP, SIMULATOR)."""
        pass

    @abstractmethod
    async def fetch_quotes(
        self,
        route_id: str,
        bucket_id: str,
        departure_date: datetime.date,
    ) -> list[ObservedQuote]:
        """Fetch quotes for a given route and departure date."""
        pass

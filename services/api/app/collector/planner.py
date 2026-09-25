"""Collection task planner for scheduled daily cycles and continuous coverage."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class CollectionTask:
    """Represents a scheduled scraping unit of work."""

    cycle_id: Optional[int]
    route_id: str
    bucket_id: str
    source_id: str
    target_departure_date: datetime.date
    scheduled_at: datetime.datetime


class TaskPlanner:
    """Generates the execution matrix of collection tasks across routes, buckets, and sources."""

    LEAD_BUCKET_MIDPOINTS = {
        "L01": 1,
        "L03": 2,
        "L07": 5,
        "L14": 11,
        "L21": 18,
        "L30": 26,
        "L60": 45,
    }

    @classmethod
    def plan_cycle(
        cls,
        cycle_id: int,
        routes: list[str],
        buckets: list[str],
        sources: list[str],
        base_date: Optional[datetime.date] = None,
    ) -> list[CollectionTask]:
        """Create task grid for full cycle collection."""
        if base_date is None:
            base_date = datetime.date.today()

        now = datetime.datetime.now(datetime.timezone.utc)
        tasks: list[CollectionTask] = []

        for route in routes:
            for bucket in buckets:
                days_ahead = cls.LEAD_BUCKET_MIDPOINTS.get(bucket, 7)
                dep_date = base_date + datetime.timedelta(days=days_ahead)

                for src in sources:
                    tasks.append(CollectionTask(
                        cycle_id=cycle_id,
                        route_id=route,
                        bucket_id=bucket,
                        source_id=src,
                        target_departure_date=dep_date,
                        scheduled_at=now,
                    ))

        return tasks

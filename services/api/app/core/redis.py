"""Redis connection pool for FLASH state, pub/sub, sessions, and heartbeats."""

from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import settings

# Shared async Redis pool
redis_pool = aioredis.ConnectionPool.from_url(
    settings.redis_url,
    max_connections=50,
    decode_responses=True,
)

redis_client = aioredis.Redis(connection_pool=redis_pool)


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency — returns the shared Redis client."""
    return redis_client

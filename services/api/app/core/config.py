"""AeroIndex core configuration — loaded from environment variables."""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional

try:
    from pydantic import field_validator
    from pydantic_settings import BaseSettings
    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False
    class BaseSettings:
        pass


class DataMode(str, Enum):
    """System-wide data source mode. The UI must never label SIMULATED as LIVE."""

    LIVE = "LIVE"
    SIMULATED_LIVE = "SIMULATED_LIVE"
    REPLAY = "REPLAY"
    BACKTEST = "BACKTEST"
    HYBRID = "HYBRID"


if _HAS_PYDANTIC:
    class Settings(BaseSettings):
        app_name: str = "AeroIndex"
        debug: bool = False
        tz: str = "Asia/Kolkata"

        data_mode: DataMode = DataMode.SIMULATED_LIVE
        sim_seed: int = 20260922
        simulation_interval_seconds: float = 2.0

        database_url: str = "postgresql+asyncpg://aeroindex:changeme_pg_dev_only@localhost:5432/aeroindex"
        database_url_sync: str = "postgresql://aeroindex:changeme_pg_dev_only@localhost:5432/aeroindex"

        redis_url: str = "redis://localhost:6379/0"
        celery_broker_url: str = "redis://localhost:6379/1"
        celery_result_backend: str = "redis://localhost:6379/2"

        minio_endpoint: str = "localhost:9000"
        minio_root_user: str = "minioadmin"
        minio_root_password: str = "changeme_minio_dev_only"
        minio_bucket: str = "aeroindex-raw"
        minio_secure: bool = False

        jwt_secret_key: str = "aeroindex_super_secret_jwt_key_2026"
        jwt_algorithm: str = "HS256"
        jwt_access_token_expire_minutes: int = 15
        jwt_refresh_token_expire_days: int = 7
        password_min_length: int = 12

        api_host: str = "0.0.0.0"
        api_port: int = 8000
        api_cors_origins: str = "http://localhost:3000"

        rate_limit_per_minute: int = 120
        rate_limit_burst: int = 40
        rate_limit_daily: int = 50000

        collection_cycles_ist: str = "00:30,06:30,12:30,18:30"
        collector_concurrency: int = 4
        collector_max_per_host_per_day: int = 500
        collector_delay_min_s: float = 2.0
        collector_delay_max_s: float = 5.0

        flash_persist_interval_s: int = 30
        flash_tick_max_per_second: int = 4

        official_freeze_time_ist: str = "23:30"
        coverage_min_weight: float = 0.80

        heartbeat_interval_seconds: int = 10
        heartbeat_stale_threshold_seconds: int = 60
        heartbeat_offline_threshold_seconds: int = 300

        freshness_fresh_seconds: int = 30
        freshness_degraded_seconds: int = 120
        freshness_stale_seconds: int = 300

        @property
        def cors_origins_list(self) -> list[str]:
            return [s.strip() for s in self.api_cors_origins.split(",")]

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
        }

    settings = Settings()
else:
    class StandaloneSettings:
        def __init__(self):
            self.app_name = os.getenv("APP_NAME", "AeroIndex")
            self.debug = os.getenv("DEBUG", "false").lower() == "true"
            self.tz = os.getenv("TZ", "Asia/Kolkata")

            mode_str = os.getenv("DATA_MODE", "SIMULATED_LIVE")
            self.data_mode = DataMode(mode_str) if mode_str in DataMode.__members__ else DataMode.SIMULATED_LIVE
            self.sim_seed = int(os.getenv("SIM_SEED", "20260922"))
            self.simulation_interval_seconds = float(os.getenv("SIMULATION_INTERVAL_SECONDS", "2.0"))

            self.database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://aeroindex:changeme_pg_dev_only@localhost:5432/aeroindex")
            self.database_url_sync = os.getenv("DATABASE_URL_SYNC", "postgresql://aeroindex:changeme_pg_dev_only@localhost:5432/aeroindex")

            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "aeroindex_super_secret_jwt_key_2026")
            self.jwt_algorithm = "HS256"
            self.jwt_access_token_expire_minutes = 15
            self.jwt_refresh_token_expire_days = 7
            self.password_min_length = 12

            self.api_host = "0.0.0.0"
            self.api_port = 8000
            self.api_cors_origins = "http://localhost:3000"

            self.freshness_fresh_seconds = 30
            self.freshness_degraded_seconds = 120
            self.freshness_stale_seconds = 300

            self.heartbeat_stale_threshold_seconds = 60
            self.heartbeat_offline_threshold_seconds = 300

        @property
        def cors_origins_list(self) -> list[str]:
            return [s.strip() for s in self.api_cors_origins.split(",")]

    settings = StandaloneSettings()

"""Observability: structured JSON logging, Prometheus metrics, and latency instrumentation."""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

from app.engine.flash_engine import FlashEngine


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for Datadog / CloudWatch / ELK."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_observability_logging():
    """Configure root logger to use structured JSON output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)


class PrometheusMetricsExporter:
    """Exports Prometheus text exposition format metrics without external libraries."""

    @classmethod
    def generate_metrics_text(cls) -> str:
        tick = FlashEngine.get_latest_tick()

        lines = [
            "# HELP aeroindex_flash_index_value Real-time FLASH index value",
            "# TYPE aeroindex_flash_index_value gauge",
            f'aeroindex_flash_index_value{{series_id="{tick.series_id}"}} {tick.index_value}',
            "",
            "# HELP aeroindex_e2e_latency_ms End-to-end observation to publication latency in milliseconds",
            "# TYPE aeroindex_e2e_latency_ms gauge",
            f'aeroindex_e2e_latency_ms{{series_id="{tick.series_id}"}} {tick.e2e_latency_ms}',
            "",
            "# HELP aeroindex_coverage_pct Route basket coverage percentage",
            "# TYPE aeroindex_coverage_pct gauge",
            f'aeroindex_coverage_pct{{series_id="{tick.series_id}"}} {tick.coverage_pct}',
            "",
            "# HELP aeroindex_quotes_total Cumulative count of airfare observations processed",
            "# TYPE aeroindex_quotes_total counter",
            f'aeroindex_quotes_total{{series_id="{tick.series_id}"}} {tick.quote_count}',
            "",
        ]
        return "\n".join(lines)

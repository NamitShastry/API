# Real-Time Architecture Specification: AeroIndex / FareOS

## 1. Dual Real-Time Concepts
The platform strictly decouples and implements two independent real-time dimensions:

### Dimension A: Continuous Live Observation Layer
- Continuous incoming stream of fare quotes (from airlines, OTAs, or local deterministic simulator).
- Operates independently of the four scheduled daily snapshot cycles (00:30, 06:30, 12:30, 18:30 IST).
- Every observation records:
  - `observed_at`: Exact timestamp when the quote was extracted at source.
  - `ingested_at`: Exact timestamp when the quote was accepted by the pipeline.
  - `e2e_latency_ms`: Elapsed time between observation and availability in the platform.

### Dimension B: FLASH Real-Time Index Engine
- High-frequency index computation engine maintaining running geometric cell statistics in Redis.
- As new quotes pass data quality validation (R01-R12), Redis updates cell states atomically.
- Emits `IndexTick` envelopes over Redis pub/sub and WebSocket connections.
- Sub-second distribution to the frontend mission control dashboard.

---

## 2. Staleness & Freshness Thresholds
| Status | Time Since Last Tick | UI Presentation | Alert Action |
|---|---|---|---|
| **FRESH** | < 30 seconds | Green pulsing indicator | None |
| **DEGRADED** | 30s - 120 seconds | Amber warning banner | Warning log |
| **STALE** | > 120 seconds | Red alert indicator | On-call / Pager notification |
| **OFFLINE** | > 300 seconds | Grey disconnected state | Reconnection loop initiated |

---

## 3. WebSocket Event Envelopes
Every message emitted to connected clients adheres to the unified envelope:
```json
{
  "event_type": "INDEX_TICK",
  "timestamp": "2026-09-22T16:15:00.123Z",
  "data_mode": "SIMULATED_LIVE",
  "series_id": "APIX-NAT-COMP",
  "index_value": 114.82,
  "change_1d": 1.45,
  "e2e_latency_ms": 320,
  "coverage_pct": 94.2,
  "quote_count": 18450
}
```

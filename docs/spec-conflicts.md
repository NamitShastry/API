# Specification Conflict Resolution & Architectural Decisions (ADR)

## Conflict 1: Real-Time vs Daily Scheduled Collections
- **Issue**: Source documents describe four daily collection cycles (00:30, 06:30, 12:30, 18:30 IST) for the Official Index, but also mandate a sub-second "FLASH" index and real-time dashboard.
- **Resolution**: Implemented the dual-layer architecture. Scheduled cycles populate the Official Daily Index with an 80% route coverage freeze at 23:30 IST. The Continuous Observation Layer / Simulator continuously streams quotes into the Redis FLASH engine for live tick distribution.

## Conflict 2: Live Scraping vs Sandbox Demonstrability
- **Issue**: Full production scraping of 8 airlines and OTAs requires live proxy pools, anti-bot bypass tokens, and rate budget management, which can fail or be unavailable in offline or local demo environments.
- **Resolution**: Designed the system around a strict `DataMode` enum (`LIVE`, `SIMULATED_LIVE`, `REPLAY`). The `SIMULATED_LIVE` adapter generates mathematically calibrated, realistic domestic Indian market data with authentic airline behavior (Indigo, Air India, SpiceJet, Akasa), realistic demand elasticity curves across lead windows (L01-L60), and simulated anomalies for test verification.

## Conflict 3: Index Mathematical Formula
- **Issue**: Jevons elementary index vs weighted Laspeyres aggregations.
- **Resolution**: Jevons geometric mean ($(\prod p_i)^{1/n}$) is used at the elementary cell level (Route $\times$ Lead Bucket $\times$ Day-of-Week) to avoid arithmetic upward substitution bias. Higher-level aggregations apply DGCA route weights and passenger-basket weights.

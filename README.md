# AeroIndex / FareOS

> **Real-Time Airfare Price Intelligence & Daily Index Platform for India**
> An enterprise-grade, high-frequency airfare intelligence system replacing manual, slow airfare reporting with an automated, robust Jevons elementary price index and continuous streaming price signals.

---

## 1. System Overview

AeroIndex operates across two distinct real-time dimensions:
1. **Continuous Live Observation Layer**: Ingests freshly observed flight quotes from airlines, OTAs, and the calibrated continuous simulator into the pipeline with sub-second timestamps and latency tracking.
2. **Real-Time FLASH Index**: Continuous index recalculation using an atomic Redis pipeline with sub-second publication over WebSockets to dashboards and enterprise consumers.
3. **Official Daily Settlement**: Methodology-grounded daily index freeze at 23:30 IST based on the four scheduled collection cycles (00:30, 06:30, 12:30, 18:30 IST) with an 80% coverage guard.

---

## 2. Architecture & Data Flow

```text
[Airlines / OTAs / Calibrated Simulator]
                  │
                  ▼
         Unified Collector (Live & Scheduled)
                  │
                  ▼
         Cleaning & Deduplication Engine (R01-R12)
                  │
                  ▼
   ┌──────────────┴────────────────────────┐
   ▼                                       ▼
PostgreSQL (Raw/Clean Quotes)       Redis FLASH Engine (Sub-second)
                                           │
                                           ▼
                                   IndexTick Publication
                                           │
                                           ▼
                                 WebSocket Channel
                                           │
                                           ▼
                             Next.js 14 Mission Control UI
```

---

## 3. Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15+ and Redis 7+ (or Docker)

### Setup
```bash
# Copy environment configuration
cp .env.example .env

# Install dependencies and prepare DB
make setup

# Run migrations and seed data
make migrate
make seed

# Run backend API and Next.js frontend
make dev
```

---

## 4. Operational Modes
- `LIVE`: Live web scraping adapter enabled (requires proxy pool and headless browsers).
- `SIMULATED_LIVE`: Deterministic synthetic simulator generating realistic Indian domestic flight price quotes at configurable tick frequencies with realistic seasonality, lead-time elasticity, and carrier behaviors.
- `REPLAY`: Historical replay for backtesting and algorithm validation.

---

## 5. Security & Governance
- **Authentication**: Argon2id password hashing, JWT token rotation, TOTP MFA.
- **RBAC**: 10 hierarchical and functional roles.
- **Data Governance**: Tamper-evident hash-chained audit log, automated provenance tracking ("Reproduce this number").

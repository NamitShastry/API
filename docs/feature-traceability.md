# AeroIndex / FareOS Feature Traceability Matrix

This document maps all 160 specification features (F001 to F160) across 4 tiers to the implementation components.

## Tier 1: Core Foundation & Index Pipeline (F001 - F040)
- **F001 - F010**: Route basket configuration (20 top Indian domestic routes, DGCA passenger weights).
- **F011 - F020**: Lead-time buckets (L01: 0-1 days, L03: 2-3 days, L07: 4-7 days, L14: 8-14 days, L21: 15-21 days, L30: 22-30 days, L60: 31-60 days).
- **F021 - F030**: Source adapters (Airlines: 6E, AI, SG, QP; OTAs: MakeMyTrip, EaseMyTrip, Yatra; Simulator).
- **F031 - F040**: Cleaning rules (R01-R12: Fare boundary validation, tax extraction, currency normalization, deduplication, MAD outlier filter).

## Tier 2: Index Calculation & Storage (F041 - F080)
- **F041 - F050**: Product matching ladder (Direct Non-Stop Standard Economy vs 1-stop options).
- **F051 - F060**: Jevons elementary price index calculator ($(\prod p_i)^{1/n}$).
- **F061 - F070**: FLASH engine (Redis Lua sub-second state) and Official Daily Freeze (23:30 IST).
- **F071 - F080**: Core REST API v1 endpoints (`/api/v1/index/current`, `/series`, `/routes`, `/heatmap`).

## Tier 3: Visual Analytics & Mission Control (F081 - F120)
- **F081 - F090**: Interactive dashboards (Overview, Index Explorer, Route Heatmap, India Route Flow Map).
- **F091 - F100**: Route Drill-down, Lead-Time Elasticity curves, Carrier Comparison matrices.
- **F101 - F110**: What Moved waterfall chart, Real-time Quote Ticker with animated price pulses.
- **F111 - F120**: Public landing page, Methodology disclosure page, Solutions showcase.

## Tier 4: Enterprise Intelligence, Trust & Governance (F121 - F160)
- **F121 - F130**: Provenance Drawer ("Reproduce This Number"), Quote Inspector with audit trails.
- **F131 - F140**: Data Health console, Service heartbeats, Source Circuit Breakers, Alert manager.
- **F141 - F150**: Security (Argon2id, JWT rotation, 10 RBAC roles, MFA, Hashed API keys).
- **F151 - F160**: Automated PDF report generator, CSV/SDMX exports, Developer API console, Support ticketing.

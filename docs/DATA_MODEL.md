# Data Model

## Overview

This document describes intended data entities and storage layout. No database or persistence layer is implemented in the foundation phase.

## File-Based Data (`data/`)

| Path | Contents | Version Control |
|------|----------|-----------------|
| `data/raw/` | Source downloads, broker exports, unmodified feeds | Structure only (`.gitkeep`); files gitignored |
| `data/processed/` | Cleaned OHLCV, derived features, analysis outputs | Structure only; files gitignored |

See [data/README.md](../data/README.md) for usage conventions.

## Conceptual Entities

These entities support the domain model and will inform future schema design. Fields are illustrative — not finalized.

### Candle / OHLCV Bar

| Field | Type | Notes |
|-------|------|-------|
| `timestamp` | datetime | Bar open or close time (TBD) |
| `open`, `high`, `low`, `close` | decimal | Price |
| `volume` | decimal | Optional |
| `timeframe` | string | e.g. `15m`, `1h`, `4h` |
| `instrument` | string | e.g. `EUR_USD` |

### Impulse (Candidate)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | |
| `instrument` | string | |
| `timeframe` | string | |
| `start_time`, `end_time` | datetime | Move boundaries (TBD) |
| `direction` | enum | `bullish` / `bearish` |
| `displacement` | decimal | Raw price move |
| `displacement_atr_ratio` | decimal | Normalized (future) |
| `duration_bars` | int | |
| `directional_efficiency` | decimal | Future metric |
| `qualified` | bool | Set by qualification logic |

### Zone

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | |
| `impulse_id` | UUID | FK to validated impulse |
| `instrument` | string | |
| `timeframe` | string | |
| `zone_high`, `zone_low` | decimal | From preceding candle |
| `preceding_candle_time` | datetime | |
| `direction` | enum | `bullish` / `bearish` |
| `created_at` | datetime | Detection time |
| `initial_strength` | decimal | Future; nullable at foundation |
| `lifecycle_state` | enum | TBD |

### Zone Lifecycle Event

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | |
| `zone_id` | UUID | |
| `event_type` | string | e.g. retest, break, confluence_update |
| `timestamp` | datetime | |
| `payload` | JSON | Event-specific data |

### Historical Outcome

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | |
| `zone_id` | UUID | |
| `outcome_type` | string | TBD |
| `observed_at` | datetime | |
| `metrics` | JSON | Reaction depth, time to target, etc. |

## Persistence Strategy (Future)

| Layer | Technology | Purpose |
|-------|------------|---------|
| Analytical / bulk | Parquet in `data/processed/` | Research, backtests |
| Operational | PostgreSQL (planned) | Zones, events, API state |
| Cache / queue | Redis, Celery (planned) | Async jobs, not foundation |

## API Schemas (Future)

Pydantic schemas in `backend/app/schemas/` will mirror API contracts. The health endpoint is the only implemented schema today.

## Related Documents

- [DOMAIN_MODEL.md](DOMAIN_MODEL.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)

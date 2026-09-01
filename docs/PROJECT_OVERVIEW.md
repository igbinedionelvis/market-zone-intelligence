# Project Overview

## Purpose

Market Zone Intelligence is a research and engineering platform for detecting, scoring, and validating price zones derived from impulse moves in financial markets. The system separates zone definition from impulse qualification, strength scoring, lifecycle management, and downstream trading or research use cases.

## Core Methodology

Zones are defined by a validated impulse move:

1. A validated impulse move is detected.
2. The last candle immediately preceding that impulse becomes the zone.
3. This is **not** a generic multi-candle supply/demand definition.

Initial zone strength will eventually be derived from characteristics of the impulse. Candidate impulse factors include normalized displacement relative to ATR, duration, and directional efficiency. Exact formulas, thresholds, and weights are intentionally **not** decided yet.

A zone is a living object whose strength can be reevaluated as time passes and additional confluences or events occur. Future confluence may include 4H, 1H, and 15M alignment, structure, liquidity, freshness, retests, reaction behavior, and other strategy-specific factors.

See [ADR-001](decisions/ADR-001-impulse-based-zone-definition.md) for the authoritative decision record.

## Scope (Current Foundation)

- Monorepo layout: backend API, frontend UI, research workspace, data directories
- Minimal FastAPI backend with health endpoint
- Vite + React + TypeScript frontend (scaffold only)
- Documentation and architecture decision records

## Non-Goals (Foundation Phase)

The following are explicitly **out of scope** for the current foundation:

- Impulse detection implementation
- Zone detection and scoring logic
- Trading, execution, or backtesting
- OANDA or other broker integrations
- PostgreSQL, Redis, Celery, or other infrastructure
- Machine learning pipelines
- Dashboard or visualization features beyond frontend scaffold

## Key Distinctions

| Concern | Description |
|---------|-------------|
| Zone detection | Identifying the candle/price range that becomes the zone after impulse validation |
| Impulse qualification | Determining whether a price move qualifies as a validated impulse |
| Initial zone strength | Scoring derived from impulse characteristics at zone creation |
| Zone lifecycle | Ongoing reevaluation of zone strength over time |
| Multi-timeframe confluence | Alignment and context across timeframes (e.g. 4H, 1H, 15M) |
| Historical outcomes | Recording what happened after zone formation for analysis |
| Statistical validation | Rigorous testing of hypotheses and scoring models |
| Future ML research | Exploratory modeling using labeled outcomes and features |

## Success Criteria

The foundation phase is complete when:

- Repository structure, documentation, and ADRs are in place
- Backend serves a health endpoint and passes basic tests
- Frontend scaffold remains intact and runnable
- Clear boundaries exist between future implementation phases

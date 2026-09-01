# Roadmap

Phases are ordered by dependency. Dates and priorities are not fixed.

## Phase 0: Foundation (Current)

- [x] Repository structure and documentation
- [x] ADR-001: impulse-based zone definition
- [x] Minimal FastAPI backend with health endpoint
- [x] Preserve Vite + React frontend scaffold
- [x] Data and research directory layout

## Phase 1: Data Ingestion

- Define OHLCV data sources and formats
- Implement data loading utilities in `backend/app/data/`
- Establish sample datasets in `data/raw/` and `data/processed/`
- Document data provenance

**Not in scope:** OANDA integration until explicitly planned.

## Phase 2: Impulse Qualification

- Specify qualification rules (ADR or spec document)
- Implement candidate impulse detection
- Unit tests with fixture candles
- Research notebooks validating rule behavior

**Deferred:** Exact formulas, thresholds, weights.

## Phase 3: Zone Detection

- Implement zone derivation from validated impulses
- API endpoints for zone listing (read-only)
- Frontend visualization (basic)

## Phase 4: Initial Zone Strength

- Define strength model from impulse characteristics
- Implement scoring service
- Document in ADR when rules are chosen

## Phase 5: Zone Lifecycle

- Event model for retests, breaks, reactions
- Lifecycle state machine
- Persistence layer (PostgreSQL)

## Phase 6: Multi-Timeframe Confluence

- Cross-timeframe alignment logic
- Confluence scoring (separate from initial strength)
- API and UI for confluence context

## Phase 7: Historical Outcomes and Statistical Validation

- Outcome labeling pipeline
- Backtest harness (analysis only, not live trading)
- Statistical reports and dashboards

## Phase 8: ML Research (Optional)

- Feature engineering from zones and outcomes
- Experimental models in `research/`
- Adoption only after statistical validation

## Explicitly Out of Scope (Until Revisited)

- Live trading and order execution
- Broker integrations
- Redis / Celery job infrastructure
- Production deployment hardening

## Related Documents

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- [decisions/](decisions/)

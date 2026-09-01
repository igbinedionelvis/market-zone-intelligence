# Testing Strategy

## Principles

- Test behavior, not implementation details.
- Keep the foundation test suite small and fast.
- Expand coverage as each domain concern is implemented.
- Separate unit, integration, and research validation tests.

## Backend

### Current (Foundation)

| Layer | Tool | Scope |
|-------|------|-------|
| API | pytest + httpx (`TestClient`) | Health endpoint returns expected status and body |

```bash
cd backend
pytest
```

### Planned by Domain Concern

| Concern | Test Type | Notes |
|---------|-----------|-------|
| Impulse qualification | Unit | Pure functions on OHLCV fixtures; no I/O |
| Zone detection | Unit | Given validated impulse + candles → zone bounds |
| Initial zone strength | Unit | Given impulse metrics → score; golden fixtures |
| Zone lifecycle | Unit + integration | State transitions with synthetic price paths |
| Multi-timeframe confluence | Unit | Alignment rules on multi-TF fixtures |
| API routes | Integration | Full request/response with test client |
| Database | Integration | When PostgreSQL is added; use test DB or containers |

### Fixtures

- Store small OHLCV samples under `backend/tests/fixtures/` (future).
- Avoid committing large datasets; generate minimal candles in tests.

## Frontend

Foundation phase: no automated tests configured. When UI features are added:

- **Unit:** Vitest or React Testing Library for components
- **E2E:** Playwright or Cypress for critical flows (optional, later)

## Research and Statistical Validation

| Activity | Location | Validation |
|----------|----------|------------|
| Exploratory notebooks | `research/notebooks/` | Manual review; not CI |
| Reproducible experiments | `research/experiments/` | Scripted runs; document seeds and inputs |
| Statistical validation | Research + future CI job | Hypothesis tests on `data/processed/` outcomes |

Research outputs are not gate-kept by default CI until promoted to `backend/` services.

## CI (Future)

- Run `pytest` on backend changes
- Run `npm run build` and `npm run lint` on frontend changes
- No trading or live market connectivity in CI

## Related Documents

- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)

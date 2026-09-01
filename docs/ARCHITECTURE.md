# Architecture

## System Context

```
┌─────────────┐     HTTP      ┌─────────────┐
│   Frontend  │ ────────────► │   Backend   │
│  (Vite/React)│ ◄──────────── │  (FastAPI)  │
└─────────────┘               └──────┬──────┘
                                     │
                              (future: data,
                               research APIs)
┌─────────────┐               ┌──────▼──────┐
│  Research   │               │    Data     │
│ (notebooks) │──────────────►│ raw/processed│
└─────────────┘               └─────────────┘
```

## Component Boundaries

### Backend (`backend/`)

FastAPI application organized by layer:

| Package | Responsibility |
|---------|----------------|
| `api/` | HTTP routes and request/response handling |
| `core/` | Configuration, shared utilities |
| `models/` | Domain and persistence models (future) |
| `schemas/` | Pydantic request/response schemas |
| `services/` | Business logic orchestration |
| `database/` | Database access (future) |
| `data/` | Data loading and transformation helpers |

**Current state:** `main.py` exposes a `/health` endpoint only. Other packages are placeholders.

### Frontend (`frontend/`)

Vite + React + TypeScript SPA. Not modified during foundation setup. Will consume backend APIs in future phases.

### Research (`research/`)

Jupyter notebooks and standalone experiments. Outputs are gitignored; structure is versioned.

### Data (`data/`)

| Directory | Purpose |
|-----------|---------|
| `raw/` | Unmodified source data (downloads, exports) |
| `processed/` | Cleaned, normalized datasets for analysis |

Contents are gitignored; `.gitkeep` preserves directory structure.

## Domain Pipeline (Planned)

These stages are **documented but not implemented**:

```
Market Data
    │
    ▼
Impulse Qualification ──► Zone Detection
    │                          │
    ▼                          ▼
Initial Zone Strength    Zone Lifecycle
    │                          │
    └──────────┬───────────────┘
               ▼
    Multi-Timeframe Confluence
               │
               ▼
    Historical Outcomes / Statistical Validation / ML Research
```

Each stage is a separate module with clear inputs and outputs. No stage embeds trading logic.

## Cross-Cutting Concerns

- **Configuration:** Environment variables via `.env` (see `.env.example`)
- **Testing:** pytest for backend; frontend test strategy TBD (see [TESTING_STRATEGY.md](TESTING_STRATEGY.md))
- **Documentation:** Markdown in `docs/`; decisions in `docs/decisions/`

## Infrastructure (Future)

Not part of the foundation:

- PostgreSQL for persistent storage
- Redis / Celery for async jobs
- OANDA or other market data providers
- Container orchestration beyond local `docker-compose`

## Related Documents

- [DOMAIN_MODEL.md](DOMAIN_MODEL.md) — terminology and entity relationships
- [DATA_MODEL.md](DATA_MODEL.md) — data entities and storage intent
- [ADR-001](decisions/ADR-001-impulse-based-zone-definition.md) — zone definition methodology

# Market Zone Intelligence

Research and tooling platform for impulse-based zone detection, scoring, and validation in financial markets.

## Overview

This project defines supply/demand zones using a validated impulse move: the last candle immediately preceding the impulse becomes the zone. Zone strength, lifecycle, and multi-timeframe confluence are modeled as separate concerns and documented in the architecture.

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for goals and scope.

## Repository Structure

```
market-zone-intelligence/
├── backend/          # FastAPI application
├── frontend/         # Vite + React + TypeScript UI
├── research/         # Notebooks and experiments
├── data/             # Raw and processed datasets (gitignored contents)
└── docs/             # Architecture, domain model, ADRs
```

## Prerequisites

- Python 3.11+
- Node.js 20+ (for frontend)
- Docker (optional, for containerized backend)

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment

Copy `.env.example` to `.env` and adjust values as needed.

## Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_OVERVIEW](docs/PROJECT_OVERVIEW.md) | Goals, scope, and non-goals |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | System design and component boundaries |
| [DOMAIN_MODEL](docs/DOMAIN_MODEL.md) | Core concepts and terminology |
| [DATA_MODEL](docs/DATA_MODEL.md) | Data entities and storage intent |
| [DEVELOPMENT_WORKFLOW](docs/DEVELOPMENT_WORKFLOW.md) | Local dev and contribution flow |
| [TESTING_STRATEGY](docs/TESTING_STRATEGY.md) | Testing approach by layer |
| [ROADMAP](docs/ROADMAP.md) | Planned phases |
| [ADRs](docs/decisions/) | Architecture decision records |

## License

[MIT](LICENSE)

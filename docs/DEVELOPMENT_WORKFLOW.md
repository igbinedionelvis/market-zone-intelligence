# Development Workflow

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- (Optional) Docker and Docker Compose

## Initial Setup

1. Clone the repository.
2. Copy `.env.example` to `.env` and adjust values.
3. Set up the backend (see below).
4. Set up the frontend (see below).

## Backend Development

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs (auto-generated): [http://localhost:8000/docs](http://localhost:8000/docs)

### Running Tests

```bash
cd backend
pytest
```

### Code Organization

- Add routes under `app/api/`
- Add Pydantic schemas under `app/schemas/`
- Add business logic under `app/services/`
- Keep `main.py` thin — wire routers and middleware only

## Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend scaffold is independent of the backend during foundation phase. Configure `VITE_API_BASE_URL` in `.env` when API integration begins.

## Research Workflow

1. Place exploratory notebooks in `research/notebooks/`.
2. Place reproducible scripts or small experiments in `research/experiments/`.
3. Store inputs in `data/raw/` and outputs in `data/processed/`.
4. Document significant findings; promote stable logic to `backend/` when appropriate.

## Docker (Optional)

```bash
docker compose up --build
```

Requires a `.env` file at the repository root.

## Branching and Commits

- Use descriptive branch names (e.g. `feature/impulse-detection`, `docs/adr-002`).
- Keep commits focused; reference ADRs or issues when relevant.
- Do not commit secrets, large data files, or `node_modules/`.

## Architecture Decisions

Significant design choices are recorded as ADRs in `docs/decisions/`. Propose new ADRs before implementing cross-cutting changes to zone methodology, data storage, or API contracts.

## Related Documents

- [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)

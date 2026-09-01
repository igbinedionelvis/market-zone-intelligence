# Research

Exploratory analysis, notebooks, and experiments for impulse qualification, zone detection, and validation.

## Layout

| Directory | Purpose |
|-----------|---------|
| `notebooks/` | Jupyter notebooks for exploratory work |
| `experiments/` | Reproducible scripts and small standalone studies |

## Guidelines

- Notebooks are for exploration; promote stable logic to `backend/` when ready
- Store inputs in `data/raw/` and outputs in `data/processed/`
- Document assumptions; do not invent production thresholds without ADR backing
- Checkpoint directories (`.ipynb_checkpoints/`) are gitignored

## Related

- [docs/DOMAIN_MODEL.md](../docs/DOMAIN_MODEL.md)
- [docs/decisions/ADR-001-impulse-based-zone-definition.md](../docs/decisions/ADR-001-impulse-based-zone-definition.md)

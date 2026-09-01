# Data Directory

Local storage for market data and analysis outputs. File contents are gitignored; only directory structure is versioned.

## Layout

| Directory | Purpose |
|-----------|---------|
| `raw/` | Unmodified source data (downloads, exports, API dumps) |
| `processed/` | Cleaned, normalized, or feature-enriched datasets |

## Conventions

- Use descriptive filenames: `{instrument}_{timeframe}_{date_range}.{ext}`
- Prefer Parquet or CSV for tabular OHLCV data
- Document provenance in commit messages or companion `.md` files in `research/`
- Do not commit secrets, API keys, or large binary blobs

## Related

- [docs/DATA_MODEL.md](../docs/DATA_MODEL.md)
- [research/README.md](../research/README.md)

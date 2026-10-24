# Data Directory

Local storage for market data and analysis outputs. File contents are gitignored; only directory structure is versioned.

## Layout

| Directory | Purpose |
|-----------|---------|
| `raw/` | Unmodified source files. Do not rewrite, resample, or add columns. |
| `processed/` | Outputs of loading, UTC normalization, and later feature work. Empty until a processing step writes files here. |

Raw files are the source of truth for provenance. Processed files, when present, are derived and may be regenerated from raw inputs.

## Current sample (raw)

| Field | Value |
|-------|-------|
| Path | `data/raw/eurusd-m15-bid-2025-01-06-2025-01-07.csv` |
| Source | Dukascopy |
| Instrument | EUR/USD |
| Timeframe | 15-minute candles |
| Price type | Bid (this sample has no ask or mid series) |
| Timestamp unit | Unix epoch milliseconds |
| Columns | `timestamp,open,high,low,close` |
| Volume | Not present. Do not invent a volume column. |

This file is a short historical extract (2025-01-06 through 2025-01-07). It is suitable for exercising CSV ingestion and validation. It is not a substitute for a longer history, and bid prices from this source should not be assumed to match any particular TradingView feed.

Ingestion lives in `backend/app/data/`: read the caller-supplied path, require the exact columns above, convert timestamps to timezone-aware UTC, and validate OHLC invariants. The loader does not sort, deduplicate, or inject symbol, timeframe, or volume onto candle records. Optional timeframe alignment is applied only when the caller passes an explicit timeframe.

## Conventions

- Use descriptive filenames (instrument, timeframe, price type, and date range)
- Prefer Parquet or CSV for tabular OHLC data
- Document provenance here or in companion notes under `research/`
- Do not commit secrets, API keys, or large binary blobs

## Related

- [docs/DATA_MODEL.md](../docs/DATA_MODEL.md)
- [research/README.md](../research/README.md)

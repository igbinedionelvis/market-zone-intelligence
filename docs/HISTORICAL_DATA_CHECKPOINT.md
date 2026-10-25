# Historical Forex Data Checkpoint

## Status

The historical OHLC CSV ingestion and dataset-level validation foundations are implemented. The current sample dataset has passed combined validation.

## Dataset Details

- **Instrument:** EUR/USD
- **Timeframe:** 15 minutes (M15)
- **Data source:** Dukascopy
- **Price type:** Bid prices
- **Coverage:** January 6, 2025 – March 12, 2025
- **First candle:** 2025-01-06 00:00:00 UTC
- **Last candle:** 2025-03-12 23:45:00 UTC
- **Expanded CSV files:** 10
- **Total candles:** 5,400

## Combined Validation Results

- **Total candles:** 5,400
- **Unique timestamps:** 5,400
- **Safe to count as unique:** Yes
- **Duplicate timestamps:** 0
- **Overlapping file ranges:** 0
- **Out-of-order candles:** 0
- **Reported gaps:** 9

All nine reported gaps occur between Friday evening and Sunday and have a duration of 1 day, 2 hours, and 15 minutes. This pattern is consistent with weekend market closures, but the validator does not automatically classify gaps as valid or invalid.

## Data Handling Rules

- Raw CSV files remain local and Git-ignored.
- Source files are not rewritten, sorted, deduplicated, or filled with synthetic candles.
- Timestamps are timezone-aware UTC.
- The dataset validator reports duplicates, overlapping ranges, ordering issues, load errors, and gaps.
- Bid prices must not be assumed equivalent to midpoint or another broker's price feed.

## Next Steps

1. Automate historical dataset inventory and combined validation.
2. Add tests for the automation and its reporting behavior.
3. Run the full backend test suite.
4. Push the feature branch and review CI results.
5. Merge through a pull request only after appropriate review and tests.
6. Continue collecting historical data until approximately three months of coverage is available, then reassess the data workflow.

**Important:** Passing structural validation confirms data consistency against the implemented checks; it does not prove that the feed is complete or suitable for trading research.

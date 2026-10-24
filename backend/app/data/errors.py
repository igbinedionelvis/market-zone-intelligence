"""Errors raised while loading or validating market CSV data."""


class MarketDataError(Exception):
    """Base error for CSV ingestion and candle validation."""


class CsvLoadError(MarketDataError):
    """Raised when a CSV cannot be read, parsed, or matched to the OHLC schema."""


class CandleValidationError(MarketDataError):
    """Raised when parsed candles violate timestamp or OHLC rules."""

"""OHLC candle records and validation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite

from app.data.errors import CandleValidationError

_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class Candle:
    """A single OHLC bar. Volume, symbol, and timeframe are not part of this record."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float


def epoch_ms_to_utc(milliseconds: int) -> datetime:
    """Convert a Unix epoch timestamp in milliseconds to timezone-aware UTC."""
    seconds, remainder_ms = divmod(milliseconds, 1000)
    return _UNIX_EPOCH + timedelta(seconds=seconds, milliseconds=remainder_ms)


def utc_to_epoch_ms(value: datetime) -> int:
    """Convert a timezone-aware UTC datetime to Unix epoch milliseconds.

    Naive and non-UTC timestamps are rejected; offsets are not converted.
    """
    _require_utc(value)
    delta = value - _UNIX_EPOCH
    return int(delta / timedelta(milliseconds=1))


def validate_candles(
    candles: Sequence[Candle],
    *,
    timeframe: timedelta | None = None,
    row_numbers: Sequence[int] | None = None,
) -> None:
    """Validate candle prices, uniqueness, chronological order, and optional alignment.

    Row order is preserved. Duplicates are not dropped and out-of-order rows are not
    sorted; either condition raises ``CandleValidationError``.

    ``timeframe`` is optional. When provided, each timestamp must fall on a boundary
    of that duration counted from the Unix epoch. Alignment is not assumed.

    Each timestamp must already be timezone-aware UTC (zero UTC offset). Naive values
    and other offsets are rejected rather than converted. The CSV loader always emits
    ``datetime.timezone.utc``, so this rule matches loaded candles without changing them.
    """
    if row_numbers is not None and len(row_numbers) != len(candles):
        raise ValueError("row_numbers must be the same length as candles")

    if timeframe is not None:
        timeframe_ms = _timeframe_to_milliseconds(timeframe)

    seen: dict[datetime, int] = {}
    previous: Candle | None = None

    for index, candle in enumerate(candles):
        row = row_numbers[index] if row_numbers is not None else index + 1
        _validate_single_candle(candle, row=row)

        if timeframe is not None:
            epoch_ms = utc_to_epoch_ms(candle.timestamp)
            if epoch_ms % timeframe_ms != 0:
                raise CandleValidationError(
                    f"Row {row} timestamp {candle.timestamp.isoformat()}: "
                    f"not aligned to timeframe {timeframe}"
                )

        duplicate_row = seen.get(candle.timestamp)
        if duplicate_row is not None:
            raise CandleValidationError(
                f"Row {row} timestamp {candle.timestamp.isoformat()}: "
                f"duplicate of row {duplicate_row}"
            )

        if previous is not None and candle.timestamp < previous.timestamp:
            raise CandleValidationError(
                f"Row {row} timestamp {candle.timestamp.isoformat()}: "
                f"out of order (previous timestamp {previous.timestamp.isoformat()})"
            )

        seen[candle.timestamp] = row
        previous = candle


def _timeframe_to_milliseconds(timeframe: timedelta) -> int:
    if timeframe <= timedelta(0):
        raise CandleValidationError("timeframe must be a positive duration")
    milliseconds = timeframe / timedelta(milliseconds=1)
    if milliseconds != int(milliseconds):
        raise CandleValidationError("timeframe must be a whole number of milliseconds")
    return int(milliseconds)


def _require_utc(value: datetime, *, row: int | None = None) -> None:
    """Reject naive or non-UTC timestamps instead of converting them."""
    prefix = f"Row {row}: " if row is not None else ""
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        detail = value.isoformat() if value.tzinfo is not None else "naive datetime"
        raise CandleValidationError(
            f"{prefix}timestamp {detail} must be timezone-aware UTC"
        )


def _validate_single_candle(candle: Candle, *, row: int) -> None:
    _require_utc(candle.timestamp, row=row)

    for field in ("open", "high", "low", "close"):
        value = getattr(candle, field)
        if not isfinite(value):
            raise CandleValidationError(
                f"Row {row} timestamp {candle.timestamp.isoformat()}: "
                f"non-finite {field} value {value!r}"
            )

    if candle.high < candle.open:
        raise CandleValidationError(
            _ohlc_message(candle, row, "high", candle.high, "below open", candle.open)
        )
    if candle.high < candle.close:
        raise CandleValidationError(
            _ohlc_message(candle, row, "high", candle.high, "below close", candle.close)
        )
    if candle.high < candle.low:
        raise CandleValidationError(
            _ohlc_message(candle, row, "high", candle.high, "below low", candle.low)
        )
    if candle.low > candle.open:
        raise CandleValidationError(
            _ohlc_message(candle, row, "low", candle.low, "above open", candle.open)
        )
    if candle.low > candle.close:
        raise CandleValidationError(
            _ohlc_message(candle, row, "low", candle.low, "above close", candle.close)
        )


def _ohlc_message(
    candle: Candle,
    row: int,
    field: str,
    field_value: float,
    relation: str,
    other_value: float,
) -> str:
    return (
        f"Row {row} timestamp {candle.timestamp.isoformat()}: "
        f"{field} {field_value} is {relation} {other_value}"
    )

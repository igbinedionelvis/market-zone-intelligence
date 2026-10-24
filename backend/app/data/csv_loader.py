"""Load OHLC candles from a caller-supplied CSV path."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from math import isfinite
from pathlib import Path

from app.data.candles import Candle, epoch_ms_to_utc, validate_candles
from app.data.errors import CsvLoadError

EXPECTED_COLUMNS: tuple[str, ...] = ("timestamp", "open", "high", "low", "close")


def load_ohlc_csv(
    path: str | Path,
    *,
    timeframe: timedelta | None = None,
) -> list[Candle]:
    """Read, normalize, and validate OHLC rows from ``path``.

    Expected columns are exactly ``timestamp,open,high,low,close``. ``timestamp``
    values are Unix epoch milliseconds and are converted to timezone-aware UTC.
    Row order from the file is preserved.

    Pass ``timeframe`` to require timestamps to align to that interval. The loader
    does not assume a 15-minute series.
    """
    csv_path = Path(path)
    if not csv_path.is_file():
        raise CsvLoadError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        first_byte = handle.read(1)
        if not first_byte:
            raise CsvLoadError(f"CSV file is empty: {csv_path}")
        handle.seek(0)

        reader = csv.DictReader(handle)
        _require_exact_columns(reader.fieldnames)

        candles: list[Candle] = []
        row_numbers: list[int] = []
        for row_number, raw_row in enumerate(reader, start=2):
            candles.append(_parse_row(raw_row, row_number=row_number))
            row_numbers.append(row_number)

    if not candles:
        raise CsvLoadError(f"CSV contains no data rows: {csv_path}")

    validate_candles(candles, timeframe=timeframe, row_numbers=row_numbers)
    return candles


def _require_exact_columns(fieldnames: Iterable[str] | None) -> None:
    if not fieldnames:
        raise CsvLoadError("CSV is missing a header row")

    columns = [name.strip() for name in fieldnames]
    if any(column == "" for column in columns):
        raise CsvLoadError("CSV header contains an empty column name")
    if len(columns) != len(set(columns)):
        raise CsvLoadError(f"CSV header contains duplicate column names: {columns}")

    expected = set(EXPECTED_COLUMNS)
    actual = set(columns)
    missing = [column for column in EXPECTED_COLUMNS if column not in actual]
    unexpected = [column for column in columns if column not in expected]
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing columns: {missing}")
        if unexpected:
            details.append(f"unexpected columns: {unexpected}")
        raise CsvLoadError(
            "CSV header must contain exactly "
            f"{list(EXPECTED_COLUMNS)}; " + "; ".join(details)
        )


def _parse_row(raw_row: dict[str, str | None], *, row_number: int) -> Candle:
    timestamp_ms = _parse_timestamp_ms(
        _require_field(raw_row, "timestamp", row_number=row_number),
        row_number=row_number,
    )
    try:
        timestamp = epoch_ms_to_utc(timestamp_ms)
    except OverflowError as exc:
        raise CsvLoadError(
            f"Row {row_number}: timestamp {timestamp_ms} is out of range"
        ) from exc
    return Candle(
        timestamp=timestamp,
        open=_parse_price(raw_row, "open", row_number=row_number),
        high=_parse_price(raw_row, "high", row_number=row_number),
        low=_parse_price(raw_row, "low", row_number=row_number),
        close=_parse_price(raw_row, "close", row_number=row_number),
    )


def _require_field(raw_row: dict[str, str | None], field: str, *, row_number: int) -> str:
    value = raw_row.get(field)
    if value is None:
        raise CsvLoadError(f"Row {row_number}: missing {field}")
    stripped = value.strip()
    if stripped == "":
        raise CsvLoadError(f"Row {row_number}: missing {field}")
    return stripped


def _parse_timestamp_ms(raw_value: str, *, row_number: int) -> int:
    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise CsvLoadError(
            f"Row {row_number}: malformed timestamp {raw_value!r}"
        ) from exc
    if not value.is_finite():
        raise CsvLoadError(f"Row {row_number}: non-finite timestamp {raw_value!r}")
    if value != value.to_integral_value():
        raise CsvLoadError(
            f"Row {row_number}: timestamp must be an integer millisecond "
            f"Unix epoch, got {raw_value!r}"
        )
    return int(value)


def _parse_price(raw_row: dict[str, str | None], field: str, *, row_number: int) -> float:
    raw_value = _require_field(raw_row, field, row_number=row_number)
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise CsvLoadError(
            f"Row {row_number}: non-numeric {field} value {raw_value!r}"
        ) from exc
    if not isfinite(value):
        raise CsvLoadError(f"Row {row_number}: non-finite {field} value {raw_value!r}")
    return value

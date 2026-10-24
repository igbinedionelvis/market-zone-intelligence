"""CSV OHLC ingestion and validation tests using synthetic fixtures."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.data import Candle, CandleValidationError, CsvLoadError, load_ohlc_csv, validate_candles

HEADER = "timestamp,open,high,low,close"
FIRST_MS = 1736121600000  # 2025-01-06 00:00:00 UTC
SECOND_MS = 1736122500000  # 2025-01-06 00:15:00 UTC
FIRST_ROW = f"{FIRST_MS},1.03051,1.03053,1.02957,1.02965"
SECOND_ROW = f"{SECOND_MS},1.02965,1.03001,1.02962,1.02972"


def _write_csv(tmp_path: Path, *lines: str, name: str = "candles.csv") -> Path:
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_load_valid_csv_preserves_order_and_values(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, FIRST_ROW, SECOND_ROW)

    candles = load_ohlc_csv(path)

    assert len(candles) == 2
    assert candles[0].open == 1.03051
    assert candles[0].high == 1.03053
    assert candles[0].low == 1.02957
    assert candles[0].close == 1.02965
    assert candles[1].open == 1.02965
    assert candles[0].timestamp < candles[1].timestamp


def test_load_converts_millisecond_epoch_to_utc(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, FIRST_ROW)

    candle = load_ohlc_csv(path)[0]

    assert candle.timestamp == datetime(2025, 1, 6, 0, 0, tzinfo=timezone.utc)
    assert candle.timestamp.tzinfo is timezone.utc
    assert candle.timestamp.utcoffset() == timedelta(0)


def test_load_rejects_missing_columns(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "timestamp,open,high,close", FIRST_ROW)

    with pytest.raises(CsvLoadError, match="missing columns: \\['low'\\]"):
        load_ohlc_csv(path)


def test_load_rejects_unexpected_columns(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "timestamp,open,high,low,close,volume",
        f"{FIRST_ROW},100",
    )

    with pytest.raises(CsvLoadError, match="unexpected columns: \\['volume'\\]"):
        load_ohlc_csv(path)


def test_load_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(CsvLoadError, match="empty"):
        load_ohlc_csv(path)


def test_load_rejects_header_only_csv(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER)

    with pytest.raises(CsvLoadError, match="no data rows"):
        load_ohlc_csv(path)


def test_load_rejects_malformed_price(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, f"{FIRST_MS},1.03051,not-a-number,1.02957,1.02965")

    with pytest.raises(CsvLoadError, match="Row 2: non-numeric high value"):
        load_ohlc_csv(path)


def test_load_rejects_malformed_timestamp(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, "yesterday,1.03051,1.03053,1.02957,1.02965")

    with pytest.raises(CsvLoadError, match="Row 2: malformed timestamp"):
        load_ohlc_csv(path)


def test_load_rejects_non_finite_price(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, f"{FIRST_MS},1.03051,inf,1.02957,1.02965")

    with pytest.raises(CsvLoadError, match="Row 2: non-finite high value"):
        load_ohlc_csv(path)


def test_load_rejects_invalid_ohlc_high_below_open(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, f"{FIRST_MS},1.03,1.02,1.01,1.025")

    with pytest.raises(CandleValidationError, match="Row 2 .* high 1.02 is below open 1.03"):
        load_ohlc_csv(path)


def test_load_rejects_invalid_ohlc_low_above_close(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, f"{FIRST_MS},1.03,1.04,1.025,1.02")

    with pytest.raises(CandleValidationError, match="Row 2 .* low 1.025 is above close 1.02"):
        load_ohlc_csv(path)


def test_load_rejects_duplicate_timestamps(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, FIRST_ROW, FIRST_ROW)

    with pytest.raises(CandleValidationError, match="Row 3 .* duplicate of row 2"):
        load_ohlc_csv(path)


def test_load_rejects_out_of_order_timestamps_without_reordering(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, SECOND_ROW, FIRST_ROW)

    with pytest.raises(CandleValidationError, match="Row 3 .* out of order"):
        load_ohlc_csv(path)


def test_load_does_not_require_timeframe_alignment_by_default(tmp_path: Path) -> None:
    unaligned_ms = FIRST_MS + 60_000
    path = _write_csv(tmp_path, HEADER, f"{unaligned_ms},1.03051,1.03053,1.02957,1.02965")

    candles = load_ohlc_csv(path)

    assert len(candles) == 1
    assert candles[0].timestamp == datetime(2025, 1, 6, 0, 1, tzinfo=timezone.utc)


def test_load_validates_alignment_when_timeframe_is_provided(tmp_path: Path) -> None:
    unaligned_ms = FIRST_MS + 60_000
    path = _write_csv(tmp_path, HEADER, f"{unaligned_ms},1.03051,1.03053,1.02957,1.02965")

    with pytest.raises(CandleValidationError, match="not aligned to timeframe"):
        load_ohlc_csv(path, timeframe=timedelta(minutes=15))


def test_load_accepts_aligned_timestamps_when_timeframe_is_provided(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, HEADER, FIRST_ROW, SECOND_ROW)

    candles = load_ohlc_csv(path, timeframe=timedelta(minutes=15))

    assert [candle.timestamp.minute for candle in candles] == [0, 15]


def test_load_rejects_out_of_range_timestamp(tmp_path: Path) -> None:
    # 10000-01-01 00:00:00 UTC, beyond datetime.max
    path = _write_csv(tmp_path, HEADER, "253402300800000,1.03051,1.03053,1.02957,1.02965")

    with pytest.raises(
        CsvLoadError,
        match="Row 2: timestamp 253402300800000 is out of range",
    ):
        load_ohlc_csv(path)


def test_validate_candles_rejects_non_utc_timestamp() -> None:
    candle = Candle(
        timestamp=datetime(2025, 1, 6, tzinfo=timezone(timedelta(hours=-5))),
        open=1.03,
        high=1.03,
        low=1.03,
        close=1.03,
    )

    with pytest.raises(
        CandleValidationError,
        match="timestamp 2025-01-06T00:00:00-05:00 must be timezone-aware UTC",
    ):
        validate_candles([candle])


def test_validate_candles_accepts_equal_ohlc_bounds() -> None:
    candle = Candle(
        timestamp=datetime(2025, 1, 6, tzinfo=timezone.utc),
        open=1.03,
        high=1.03,
        low=1.03,
        close=1.03,
    )

    validate_candles([candle])

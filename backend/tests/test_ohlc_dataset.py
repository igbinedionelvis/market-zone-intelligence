"""Dataset-level OHLC validation tests using synthetic CSV fixtures."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.data import DatasetValidationError, validate_ohlc_dataset

HEADER = "timestamp,open,high,low,close"
TIMEFRAME = timedelta(minutes=15)
M15_MS = 15 * 60 * 1000
BASE_MS = 1736121600000  # 2025-01-06 00:00:00 UTC
OHLC = "1.03051,1.03053,1.02957,1.02965"


def _row(offset_bars: int) -> str:
    return f"{BASE_MS + offset_bars * M15_MS},{OHLC}"


def _write_csv(tmp_path: Path, name: str, *offsets: int) -> Path:
    path = tmp_path / name
    lines = [HEADER, *(_row(offset) for offset in offsets)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _ts(offset_bars: int) -> datetime:
    return datetime(2025, 1, 6, tzinfo=timezone.utc) + TIMEFRAME * offset_bars


def test_clean_consecutive_files(tmp_path: Path) -> None:
    first = _write_csv(tmp_path, "week1.csv", 0, 1)
    second = _write_csv(tmp_path, "week2.csv", 2, 3)

    report = validate_ohlc_dataset([first, second], timeframe=TIMEFRAME)

    assert [(item.name, item.candle_count) for item in report.files] == [
        ("week1.csv", 2),
        ("week2.csv", 2),
    ]
    assert report.first_timestamp == _ts(0)
    assert report.last_timestamp == _ts(3)
    assert report.total_candles == 4
    assert report.unique_timestamps == 4
    assert report.safe_to_count_as_unique is True
    assert report.unique_count_warning is None
    assert report.duplicates == ()
    assert report.overlapping_ranges == ()
    assert report.out_of_order == ()
    assert report.gaps == ()


def test_overlapping_files_are_not_safe_to_count_as_unique(tmp_path: Path) -> None:
    first = _write_csv(tmp_path, "jan6-8.csv", 0, 1, 2)
    second = _write_csv(tmp_path, "jan6.csv", 0, 1)

    report = validate_ohlc_dataset([first, second], timeframe=TIMEFRAME)

    assert report.total_candles == 5
    assert report.unique_timestamps == 3
    assert report.safe_to_count_as_unique is False
    assert report.unique_count_warning == (
        "Overlapping files are not safe to count together as unique candles."
    )
    assert len(report.overlapping_ranges) == 1
    overlap = report.overlapping_ranges[0]
    assert overlap.first_path == str(first)
    assert overlap.second_path == str(second)
    assert overlap.overlap_start == _ts(0)
    assert overlap.overlap_end == _ts(1)
    assert report.out_of_order
    assert report.out_of_order[0].timestamp == _ts(0)
    assert report.out_of_order[0].previous_timestamp == _ts(2)


def test_duplicate_timestamps_across_files(tmp_path: Path) -> None:
    first = _write_csv(tmp_path, "a.csv", 0, 1)
    second = _write_csv(tmp_path, "b.csv", 1, 2)

    report = validate_ohlc_dataset([first, second], timeframe=TIMEFRAME)

    assert report.safe_to_count_as_unique is False
    assert len(report.duplicates) == 1
    duplicate = report.duplicates[0]
    assert duplicate.timestamp == _ts(1)
    assert duplicate.occurrences == 2
    assert duplicate.files == (str(first), str(second))


def test_gaps_are_reported_not_filled(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "gapped.csv", 0, 2)

    report = validate_ohlc_dataset([path], timeframe=TIMEFRAME)

    assert report.total_candles == 2
    assert report.safe_to_count_as_unique is True
    assert len(report.gaps) == 1
    gap = report.gaps[0]
    assert gap.previous_timestamp == _ts(0)
    assert gap.timestamp == _ts(2)
    assert gap.duration == timedelta(minutes=30)
    assert gap.path == str(path)


def test_invalid_empty_path_list_raises() -> None:
    with pytest.raises(DatasetValidationError, match="at least one CSV path is required"):
        validate_ohlc_dataset([], timeframe=TIMEFRAME)


def test_invalid_timeframe_raises(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "ok.csv", 0)

    with pytest.raises(DatasetValidationError, match="timeframe must be a positive duration"):
        validate_ohlc_dataset([path], timeframe=timedelta(0))


def test_missing_file_is_recorded_without_raising(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"

    report = validate_ohlc_dataset([missing], timeframe=TIMEFRAME)

    assert report.files[0].load_error is not None
    assert "CSV file not found" in report.files[0].load_error
    assert report.total_candles == 0
    assert report.first_timestamp is None
    assert report.last_timestamp is None
    assert report.safe_to_count_as_unique is False

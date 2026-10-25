"""CLI inventory tests for expanded EUR/USD M15 bid CSVs."""

from io import StringIO
from pathlib import Path

from scripts.validate_historical_ohlc import (
    EXCLUDED_ONE_DAY_SAMPLE,
    discover_expanded_ohlc_csvs,
    main,
    run_inventory,
)

HEADER = "timestamp,open,high,low,close"
M15_MS = 15 * 60 * 1000
BASE_MS = 1736121600000  # 2025-01-06 00:00:00 UTC
OHLC = "1.03051,1.03053,1.02957,1.02965"


def _row(offset_bars: int) -> str:
    return f"{BASE_MS + offset_bars * M15_MS},{OHLC}"


def _write_csv(directory: Path, name: str, *offsets: int) -> Path:
    path = directory / name
    path.write_text("\n".join([HEADER, *(_row(offset) for offset in offsets)]) + "\n")
    return path


def test_discover_matches_pattern_and_excludes_one_day_sample(tmp_path: Path) -> None:
    included = _write_csv(tmp_path, "eurusd-m15-bid-2025-01-06-2025-01-08.csv", 0, 1)
    _write_csv(tmp_path, EXCLUDED_ONE_DAY_SAMPLE, 0)
    _write_csv(tmp_path, "eurusd-h1-bid-2025-01-06-2025-01-08.csv", 0)
    _write_csv(tmp_path, "notes.txt", 0)
    later = _write_csv(tmp_path, "eurusd-m15-bid-2025-01-09-2025-01-15.csv", 2, 3)

    discovered = discover_expanded_ohlc_csvs(tmp_path)

    assert [path.name for path in discovered] == [
        included.name,
        later.name,
    ]


def test_discover_does_not_exclude_other_matching_dates(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "eurusd-m15-bid-2025-01-06-2025-01-08.csv", 0, 1)

    assert discover_expanded_ohlc_csvs(tmp_path) == [path]


def test_run_inventory_exits_nonzero_when_no_matching_files(tmp_path: Path) -> None:
    _write_csv(tmp_path, EXCLUDED_ONE_DAY_SAMPLE, 0)
    output = StringIO()

    exit_code = run_inventory(tmp_path, output=output)

    assert exit_code == 1
    assert "No matching expanded EUR/USD M15 bid CSV files found" in output.getvalue()


def test_run_inventory_succeeds_when_only_gaps_are_present(tmp_path: Path) -> None:
    _write_csv(tmp_path, "eurusd-m15-bid-2025-01-06-2025-01-08.csv", 0, 2)
    output = StringIO()

    exit_code = run_inventory(tmp_path, output=output)
    text = output.getvalue()

    assert exit_code == 0
    assert "Discovered files: 1" in text
    assert "eurusd-m15-bid-2025-01-06-2025-01-08.csv: 2 candles" in text
    assert "Safe to count as unique: yes" in text
    assert "Gaps: 1" in text
    assert "duration 0:30:00" in text
    assert "First UTC timestamp: 2025-01-06T00:00:00+00:00" in text
    assert "Last UTC timestamp: 2025-01-06T00:30:00+00:00" in text


def test_run_inventory_fails_on_overlap_and_prints_details(tmp_path: Path) -> None:
    _write_csv(tmp_path, "eurusd-m15-bid-2025-01-06-2025-01-08.csv", 0, 1, 2)
    _write_csv(tmp_path, "eurusd-m15-bid-2025-01-06-2025-01-15.csv", 1, 2, 3)
    output = StringIO()

    exit_code = run_inventory(tmp_path, output=output)
    text = output.getvalue()

    assert exit_code == 1
    assert "Safe to count as unique: no" in text
    assert "Overlapping ranges: 1" in text
    assert "Duplicate timestamps: 2" in text
    assert "Out-of-order candles:" in text
    assert "overlap: 2025-01-06T00:15:00+00:00 .. 2025-01-06T00:30:00+00:00" in text


def test_run_inventory_fails_on_load_error(tmp_path: Path) -> None:
    path = tmp_path / "eurusd-m15-bid-2025-01-16-2025-01-22.csv"
    path.write_text("timestamp,open,high,low,close\n", encoding="utf-8")
    output = StringIO()

    exit_code = run_inventory(tmp_path, output=output)
    text = output.getvalue()

    assert exit_code == 1
    assert "Load errors: 1" in text
    assert "load error" in text
    assert "CSV contains no data rows" in text


def test_main_uses_raw_dir_argument(tmp_path: Path) -> None:
    _write_csv(tmp_path, "eurusd-m15-bid-2025-01-09-2025-01-15.csv", 0, 1)
    output = StringIO()

    exit_code = main(["--raw-dir", str(tmp_path)], output=output)

    assert exit_code == 0
    assert "Discovered files: 1" in output.getvalue()
    assert "Total candles: 2" in output.getvalue()


def test_missing_raw_dir_is_treated_as_no_matches(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    output = StringIO()

    exit_code = run_inventory(missing, output=output)

    assert exit_code == 1
    assert "No matching expanded EUR/USD M15 bid CSV files found" in output.getvalue()

"""Inventory and validate expanded EUR/USD M15 Dukascopy bid CSV files.

Run from the repository root:

    backend/.venv/bin/python backend/scripts/validate_historical_ohlc.py

Windows:

    backend\\.venv\\Scripts\\python.exe backend\\scripts\\validate_historical_ohlc.py
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import TextIO

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.data.dataset import DatasetReport, validate_ohlc_dataset

M15_TIMEFRAME = timedelta(minutes=15)
EXCLUDED_ONE_DAY_SAMPLE = "eurusd-m15-bid-2025-01-06-2025-01-07.csv"
EURUSD_M15_BID_CSV = re.compile(
    r"^eurusd-m15-bid-\d{4}-\d{2}-\d{2}-\d{4}-\d{2}-\d{2}\.csv$"
)


def default_raw_dir() -> Path:
    """Return ``<repo>/data/raw`` relative to this script."""
    return Path(__file__).resolve().parents[2] / "data" / "raw"


def discover_expanded_ohlc_csvs(raw_dir: Path) -> list[Path]:
    """Return matching expanded CSV paths under ``raw_dir``, sorted by name.

    Includes files named ``eurusd-m15-bid-YYYY-MM-DD-YYYY-MM-DD.csv``. Excludes
    only the original overlapping one-day sample by exact filename. Source files
    are not modified.
    """
    if not raw_dir.is_dir():
        return []

    discovered: list[Path] = []
    for path in raw_dir.iterdir():
        if not path.is_file():
            continue
        if not EURUSD_M15_BID_CSV.fullmatch(path.name):
            continue
        if path.name == EXCLUDED_ONE_DAY_SAMPLE:
            continue
        discovered.append(path)
    return sorted(discovered, key=lambda item: item.name)


def has_validation_failures(report: DatasetReport) -> bool:
    """Return True when the inventory should fail (gaps alone do not fail)."""
    if any(item.load_error for item in report.files):
        return True
    return bool(report.duplicates or report.overlapping_ranges or report.out_of_order)


def format_report(report: DatasetReport) -> str:
    """Build a readable inventory report from a ``DatasetReport``."""
    lines: list[str] = [
        "EUR/USD M15 Dukascopy bid dataset validation",
        f"Timeframe: {report.timeframe}",
        (
            "Excluded overlapping one-day sample: "
            f"{EXCLUDED_ONE_DAY_SAMPLE}"
        ),
        "",
        f"Discovered files: {len(report.files)}",
    ]
    for item in report.files:
        if item.load_error:
            lines.append(f"  - {item.name}: load error")
        else:
            lines.append(f"  - {item.name}: {item.candle_count} candles")

    lines.extend(
        [
            "",
            f"Total candles: {report.total_candles}",
            f"Unique timestamps: {report.unique_timestamps}",
            f"Safe to count as unique: {_yes_no(report.safe_to_count_as_unique)}",
        ]
    )
    if report.unique_count_warning:
        lines.append(f"  {report.unique_count_warning}")

    first = report.first_timestamp.isoformat() if report.first_timestamp else "n/a"
    last = report.last_timestamp.isoformat() if report.last_timestamp else "n/a"
    lines.extend(
        [
            f"First UTC timestamp: {first}",
            f"Last UTC timestamp: {last}",
            "",
            f"Load errors: {sum(1 for item in report.files if item.load_error)}",
            f"Duplicate timestamps: {len(report.duplicates)}",
            f"Overlapping ranges: {len(report.overlapping_ranges)}",
            f"Out-of-order candles: {len(report.out_of_order)}",
            (
                f"Gaps: {len(report.gaps)} "
                "(informational; not a validation failure)"
            ),
        ]
    )

    load_errors = [item for item in report.files if item.load_error]
    if load_errors:
        lines.append("")
        lines.append("Load error details:")
        for item in load_errors:
            lines.append(f"  - {item.name}: {item.load_error}")

    if report.duplicates:
        lines.append("")
        lines.append("Duplicate timestamps:")
        for duplicate in report.duplicates:
            files = ", ".join(Path(path).name for path in duplicate.files)
            lines.append(
                f"  - {duplicate.timestamp.isoformat()} "
                f"({duplicate.occurrences} occurrences): {files}"
            )

    if report.overlapping_ranges:
        lines.append("")
        lines.append("Overlapping ranges:")
        for overlap in report.overlapping_ranges:
            lines.append(
                "  - "
                f"{Path(overlap.first_path).name} "
                f"[{overlap.first_range[0].isoformat()} .. "
                f"{overlap.first_range[1].isoformat()}] overlaps "
                f"{Path(overlap.second_path).name} "
                f"[{overlap.second_range[0].isoformat()} .. "
                f"{overlap.second_range[1].isoformat()}]"
            )
            lines.append(
                f"    overlap: {overlap.overlap_start.isoformat()} .. "
                f"{overlap.overlap_end.isoformat()}"
            )

    if report.out_of_order:
        lines.append("")
        lines.append("Out-of-order candles:")
        for item in report.out_of_order:
            lines.append(
                f"  - {Path(item.path).name} {item.timestamp.isoformat()} "
                f"precedes {Path(item.previous_path).name} "
                f"{item.previous_timestamp.isoformat()}"
            )

    if report.gaps:
        lines.append("")
        lines.append("Gaps:")
        for gap in report.gaps:
            lines.append(
                f"  - {gap.previous_timestamp.isoformat()} -> "
                f"{gap.timestamp.isoformat()} (duration {gap.duration})"
            )
            lines.append(
                f"    files: {Path(gap.previous_path).name} -> "
                f"{Path(gap.path).name}"
            )

    return "\n".join(lines) + "\n"


def run_inventory(raw_dir: Path, *, output: TextIO) -> int:
    """Discover expanded CSVs under ``raw_dir``, validate, and print a report."""
    paths = discover_expanded_ohlc_csvs(raw_dir)
    if not paths:
        output.write(
            "No matching expanded EUR/USD M15 bid CSV files found in "
            f"{raw_dir}\n"
        )
        return 1

    report = validate_ohlc_dataset(paths, timeframe=M15_TIMEFRAME)
    output.write(format_report(report))
    return 1 if has_validation_failures(report) else 0


def main(argv: Sequence[str] | None = None, *, output: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory and validate expanded EUR/USD M15 Dukascopy bid CSVs "
            "under data/raw. The original overlapping one-day sample is excluded."
        )
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory to scan (default: <repo>/data/raw)",
    )
    args = parser.parse_args(argv)
    raw_dir = args.raw_dir if args.raw_dir is not None else default_raw_dir()
    return run_inventory(raw_dir, output=output or sys.stdout)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())

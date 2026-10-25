"""Dataset-level validation for a collection of OHLC CSV files.

This module does not rewrite, combine, sort, or fill source files. It loads each
path through ``load_ohlc_csv`` and reports coverage, duplicates, overlaps, order
issues, and gaps. Gaps are listed with timestamps and duration; they are not
classified as valid or invalid (forex weekends and other closures are expected).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from app.data.candles import Candle
from app.data.csv_loader import load_ohlc_csv
from app.data.errors import CandleValidationError, CsvLoadError, DatasetValidationError

OVERLAP_UNIQUE_COUNT_WARNING = (
    "Overlapping files are not safe to count together as unique candles."
)


@dataclass(frozen=True, slots=True)
class FileSummary:
    """Coverage for one input path."""

    path: str
    name: str
    candle_count: int
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    load_error: str | None = None


@dataclass(frozen=True, slots=True)
class TimestampDuplicate:
    """A timestamp that occurs more than once in the loaded collection."""

    timestamp: datetime
    files: tuple[str, ...]
    occurrences: int


@dataclass(frozen=True, slots=True)
class RangeOverlap:
    """Inclusive timestamp-range overlap between two successfully loaded files."""

    first_path: str
    second_path: str
    first_range: tuple[datetime, datetime]
    second_range: tuple[datetime, datetime]
    overlap_start: datetime
    overlap_end: datetime


@dataclass(frozen=True, slots=True)
class OutOfOrder:
    """A timestamp that precedes the previous candle in caller-supplied file order."""

    previous_path: str
    previous_timestamp: datetime
    path: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class Gap:
    """A gap larger than ``timeframe`` between consecutive loaded candles.

    Duration is the elapsed time between the two timestamps. This is not treated
    as a hard error and is not classified as a market closure.
    """

    previous_path: str
    previous_timestamp: datetime
    path: str
    timestamp: datetime
    duration: timedelta


@dataclass(frozen=True, slots=True)
class DatasetReport:
    """Read-only validation report for an explicit list of OHLC CSV paths."""

    files: tuple[FileSummary, ...]
    timeframe: timedelta
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    total_candles: int
    unique_timestamps: int
    safe_to_count_as_unique: bool
    unique_count_warning: str | None
    duplicates: tuple[TimestampDuplicate, ...]
    overlapping_ranges: tuple[RangeOverlap, ...]
    out_of_order: tuple[OutOfOrder, ...]
    gaps: tuple[Gap, ...]


def validate_ohlc_dataset(
    paths: Iterable[str | Path],
    *,
    timeframe: timedelta,
) -> DatasetReport:
    """Load ``paths`` in the given order and report dataset-level issues.

    ``timeframe`` is required for gap detection and is passed through to
    ``load_ohlc_csv``. Source files are not modified. Row order is preserved;
    candles are not sorted, deduplicated, or synthesized.
    """
    path_list = [Path(path) for path in paths]
    if not path_list:
        raise DatasetValidationError("at least one CSV path is required")
    _require_positive_timeframe(timeframe)

    summaries: list[FileSummary] = []
    loaded: list[tuple[FileSummary, list[Candle]]] = []
    for path in path_list:
        summary, candles = _load_file(path, timeframe=timeframe)
        summaries.append(summary)
        if candles is not None:
            loaded.append((summary, candles))

    duplicates = _find_duplicates(loaded)
    overlapping_ranges = _find_overlapping_ranges(loaded)
    out_of_order, gaps = _walk_consecutive(loaded, timeframe=timeframe)

    all_timestamps = [
        candle.timestamp for _, candles in loaded for candle in candles
    ]
    total_candles = sum(summary.candle_count for summary in summaries)
    unique_timestamps = len(set(all_timestamps))
    has_overlap_or_duplicate = bool(overlapping_ranges) or bool(duplicates)
    safe_to_count_as_unique = (
        bool(loaded)
        and not has_overlap_or_duplicate
        and total_candles == unique_timestamps
    )
    warning = OVERLAP_UNIQUE_COUNT_WARNING if has_overlap_or_duplicate else None

    return DatasetReport(
        files=tuple(summaries),
        timeframe=timeframe,
        first_timestamp=min(all_timestamps) if all_timestamps else None,
        last_timestamp=max(all_timestamps) if all_timestamps else None,
        total_candles=total_candles,
        unique_timestamps=unique_timestamps,
        safe_to_count_as_unique=safe_to_count_as_unique,
        unique_count_warning=warning,
        duplicates=duplicates,
        overlapping_ranges=overlapping_ranges,
        out_of_order=out_of_order,
        gaps=gaps,
    )


def _require_positive_timeframe(timeframe: timedelta) -> None:
    if timeframe <= timedelta(0):
        raise DatasetValidationError("timeframe must be a positive duration")
    milliseconds = timeframe / timedelta(milliseconds=1)
    if milliseconds != int(milliseconds):
        raise DatasetValidationError("timeframe must be a whole number of milliseconds")


def _load_file(
    path: Path,
    *,
    timeframe: timedelta,
) -> tuple[FileSummary, list[Candle] | None]:
    try:
        candles = load_ohlc_csv(path, timeframe=timeframe)
    except (CsvLoadError, CandleValidationError) as exc:
        return (
            FileSummary(
                path=str(path),
                name=path.name,
                candle_count=0,
                first_timestamp=None,
                last_timestamp=None,
                load_error=str(exc),
            ),
            None,
        )

    return (
        FileSummary(
            path=str(path),
            name=path.name,
            candle_count=len(candles),
            first_timestamp=candles[0].timestamp,
            last_timestamp=candles[-1].timestamp,
        ),
        candles,
    )


def _find_duplicates(
    loaded: Sequence[tuple[FileSummary, list[Candle]]],
) -> tuple[TimestampDuplicate, ...]:
    occurrences: dict[datetime, list[str]] = defaultdict(list)
    for summary, candles in loaded:
        for candle in candles:
            occurrences[candle.timestamp].append(summary.path)

    duplicates: list[TimestampDuplicate] = []
    for timestamp, files in occurrences.items():
        if len(files) > 1:
            duplicates.append(
                TimestampDuplicate(
                    timestamp=timestamp,
                    files=tuple(files),
                    occurrences=len(files),
                )
            )
    return tuple(duplicates)


def _find_overlapping_ranges(
    loaded: Sequence[tuple[FileSummary, list[Candle]]],
) -> tuple[RangeOverlap, ...]:
    overlaps: list[RangeOverlap] = []
    for index, (left_summary, _) in enumerate(loaded):
        left_first = left_summary.first_timestamp
        left_last = left_summary.last_timestamp
        if left_first is None or left_last is None:
            continue
        for right_summary, _ in loaded[index + 1 :]:
            right_first = right_summary.first_timestamp
            right_last = right_summary.last_timestamp
            if right_first is None or right_last is None:
                continue
            overlap_start = max(left_first, right_first)
            overlap_end = min(left_last, right_last)
            if overlap_start <= overlap_end:
                overlaps.append(
                    RangeOverlap(
                        first_path=left_summary.path,
                        second_path=right_summary.path,
                        first_range=(left_first, left_last),
                        second_range=(right_first, right_last),
                        overlap_start=overlap_start,
                        overlap_end=overlap_end,
                    )
                )
    return tuple(overlaps)


def _walk_consecutive(
    loaded: Sequence[tuple[FileSummary, list[Candle]]],
    *,
    timeframe: timedelta,
) -> tuple[tuple[OutOfOrder, ...], tuple[Gap, ...]]:
    out_of_order: list[OutOfOrder] = []
    gaps: list[Gap] = []
    previous_path: str | None = None
    previous_timestamp: datetime | None = None

    for summary, candles in loaded:
        for candle in candles:
            if previous_path is not None and previous_timestamp is not None:
                if candle.timestamp < previous_timestamp:
                    out_of_order.append(
                        OutOfOrder(
                            previous_path=previous_path,
                            previous_timestamp=previous_timestamp,
                            path=summary.path,
                            timestamp=candle.timestamp,
                        )
                    )
                elif candle.timestamp - previous_timestamp > timeframe:
                    gaps.append(
                        Gap(
                            previous_path=previous_path,
                            previous_timestamp=previous_timestamp,
                            path=summary.path,
                            timestamp=candle.timestamp,
                            duration=candle.timestamp - previous_timestamp,
                        )
                    )
            previous_path = summary.path
            previous_timestamp = candle.timestamp

    return tuple(out_of_order), tuple(gaps)

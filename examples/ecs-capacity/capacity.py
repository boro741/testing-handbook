"""Estimate how many ECS tasks a service needs.

Formula (from chapter 67):

    tasks = ceil(peak_rps / per_task_rps * headroom)

per_task_rps is the most requests per second ONE task can handle while still
meeting the SLO. Measure it with autoscaling OFF (one task, rising load).

Run the CLI on a CSV file:

    python capacity.py sample-capacity.csv
    python capacity.py sample-capacity.csv --headroom 1.5

CSV columns: service, peak_rps, per_task_rps, headroom (optional).
Pure Python, no AWS calls.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys

DEFAULT_HEADROOM = 1.3


def tasks_needed(peak_rps: float, per_task_rps: float, headroom: float = DEFAULT_HEADROOM) -> int:
    """Return the number of tasks needed for ``peak_rps``.

    Raises ValueError for a per-task RPS that is zero, negative or NaN, for a
    negative peak, and for a headroom below 1.0 (that would plan for less
    capacity than the peak).
    """
    if not per_task_rps > 0:  # also catches NaN
        raise ValueError(f"per_task_rps must be greater than 0, got {per_task_rps!r}")
    if not peak_rps >= 0:
        raise ValueError(f"peak_rps must be 0 or more, got {peak_rps!r}")
    if not headroom >= 1.0:
        raise ValueError(f"headroom must be 1.0 or more, got {headroom!r}")

    value = peak_rps / per_task_rps * headroom
    # Round away float noise first. Without this, 1.1 / 0.1 is 11.000000000000002
    # and ceil() would give 12 instead of 11.
    return math.ceil(round(value, 9))


def _read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Estimate ECS task counts from a CSV file.")
    parser.add_argument("csv_path", help="CSV with service, peak_rps, per_task_rps[, headroom]")
    parser.add_argument(
        "--headroom",
        type=float,
        default=DEFAULT_HEADROOM,
        help="Default headroom factor when a row has no headroom column (default: 1.3)",
    )
    args = parser.parse_args(argv)

    rows = _read_rows(args.csv_path)
    if not rows:
        print("No rows found in CSV.", file=sys.stderr)
        return 2

    print("service,peak_rps,per_task_rps,headroom,tasks_needed")
    status = 0
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        try:
            peak = float(row["peak_rps"])
            per_task = float(row["per_task_rps"])
            raw_headroom = (row.get("headroom") or "").strip()
            headroom = float(raw_headroom) if raw_headroom else args.headroom
            tasks = tasks_needed(peak, per_task, headroom)
        except (KeyError, ValueError) as exc:
            print(f"line {line_no}: {exc}", file=sys.stderr)
            status = 1
            continue
        print(f"{row.get('service', '')},{peak:g},{per_task:g},{headroom:g},{tasks}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())

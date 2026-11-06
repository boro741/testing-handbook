"""Data tests for the orders pipeline. Run from this folder with: pytest -q"""
import csv
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from pipeline import ALLOWED_STATUS, COLUMNS, is_fresh, run_pipeline  # noqa: E402

SOURCE = HERE / "orders.csv"


def count_source_rows():
    # Count the raw CSV separately from the pipeline, so the check is independent.
    with open(SOURCE, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


@pytest.fixture(scope="module")
def warehouse(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("warehouse") / "warehouse.db"
    stats = run_pipeline(SOURCE, db_path)
    con = sqlite3.connect(db_path)
    yield stats, con
    con.close()


def test_row_counts_reconcile(warehouse):
    stats, con = warehouse
    (rows_in_db,) = con.execute("SELECT COUNT(*) FROM orders").fetchone()
    assert rows_in_db == stats["loaded"]
    # Every source row is either loaded or rejected for a counted reason.
    assert count_source_rows() == stats["loaded"] + sum(stats["rejected"].values())


def test_rejections_are_counted_by_reason(warehouse):
    stats, _ = warehouse
    assert stats["rejected"] == {
        "blank_order_id": 1,
        "negative_amount": 1,
        "bad_amount": 1,
        "duplicate_order_id": 1,
        "bad_date": 1,
        "bad_status": 1,
    }


def test_no_null_or_blank_order_id(warehouse):
    _, con = warehouse
    (bad,) = con.execute(
        "SELECT COUNT(*) FROM orders WHERE order_id IS NULL OR TRIM(order_id) = ''"
    ).fetchone()
    assert bad == 0


def test_no_duplicate_order_id(warehouse):
    _, con = warehouse
    duplicates = con.execute(
        "SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1"
    ).fetchall()
    assert duplicates == []


def test_amounts_are_non_negative(warehouse):
    _, con = warehouse
    negatives = con.execute("SELECT order_id, amount FROM orders WHERE amount < 0").fetchall()
    assert negatives == []


def test_amount_total_matches_pipeline_control_total(warehouse):
    stats, con = warehouse
    (total,) = con.execute("SELECT SUM(amount) FROM orders").fetchone()
    assert total == pytest.approx(stats["loaded_amount_total"])


def test_schema_has_expected_columns(warehouse):
    _, con = warehouse
    columns = [row[1] for row in con.execute("PRAGMA table_info(orders)")]
    assert columns == COLUMNS


def test_status_values_are_allowed(warehouse):
    _, con = warehouse
    statuses = {status for (status,) in con.execute("SELECT DISTINCT status FROM orders")}
    assert statuses <= ALLOWED_STATUS


def test_order_dates_are_real_dates(warehouse):
    _, con = warehouse
    for (order_date,) in con.execute("SELECT order_date FROM orders"):
        datetime.strptime(order_date, "%Y-%m-%d")  # raises ValueError if not a real date


def test_load_is_fresh(warehouse):
    _, con = warehouse
    (loaded_at,) = con.execute("SELECT loaded_at FROM load_log").fetchone()
    assert is_fresh(loaded_at)


def test_a_stale_load_is_detected(warehouse):
    # The check must be able to fail. Pretend the load ran 48 hours ago.
    _, con = warehouse
    (loaded_at,) = con.execute("SELECT loaded_at FROM load_log").fetchone()
    two_days_later = datetime.fromisoformat(loaded_at) + timedelta(hours=48)
    assert not is_fresh(loaded_at, now=two_days_later)


def test_a_load_just_inside_the_limit_is_fresh():
    loaded_at = "2026-11-06T00:00:00+00:00"
    now = datetime(2026, 11, 6, 23, 59, tzinfo=timezone.utc)
    assert is_fresh(loaded_at, now=now)

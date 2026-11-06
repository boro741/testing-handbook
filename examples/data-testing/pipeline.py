"""A small nightly ETL pipeline for orders.

Extract: read rows from a CSV file.
Transform: trim text, parse types, reject bad rows and count the reason.
Load: write the clean rows into a SQLite table and log the load time.

Run from the command line:
    python3 pipeline.py --source orders.csv --db /tmp/warehouse.db
"""
import argparse
import csv
import sqlite3
import tempfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE / "orders.csv"
DEFAULT_DB = Path(tempfile.gettempdir()) / "data-testing-demo" / "warehouse.db"
ALLOWED_STATUS = {"NEW", "PAID", "SHIPPED", "CANCELLED"}
COLUMNS = ["order_id", "customer_id", "order_date", "status", "amount"]


def extract(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def transform(rows):
    """Return (clean_rows, rejected), where rejected maps each reason to a count."""
    clean, seen = [], set()
    rejected = Counter()
    for row in rows:
        order_id = (row.get("order_id") or "").strip()
        if not order_id:
            rejected["blank_order_id"] += 1
            continue
        if order_id in seen:
            rejected["duplicate_order_id"] += 1
            continue
        try:
            amount = float((row.get("amount") or "").strip())
        except ValueError:
            rejected["bad_amount"] += 1
            continue
        if amount < 0:
            rejected["negative_amount"] += 1
            continue
        try:
            order_date = date.fromisoformat((row.get("order_date") or "").strip())
        except ValueError:
            rejected["bad_date"] += 1
            continue
        status = (row.get("status") or "").strip().upper()
        if status not in ALLOWED_STATUS:
            rejected["bad_status"] += 1
            continue
        seen.add(order_id)
        clean.append({
            "order_id": order_id,
            "customer_id": (row.get("customer_id") or "").strip(),
            "order_date": order_date.isoformat(),
            "status": status,
            "amount": round(amount, 2),
        })
    return clean, dict(rejected)


def load(clean, db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        with con:  # one transaction: all tables are written, or none are
            con.execute("DROP TABLE IF EXISTS orders")
            # No PRIMARY KEY or NOT NULL here on purpose: the tests do the checking.
            con.execute("CREATE TABLE orders (order_id TEXT, customer_id TEXT, "
                        "order_date TEXT, status TEXT, amount REAL)")
            con.executemany("INSERT INTO orders VALUES "
                            "(:order_id, :customer_id, :order_date, :status, :amount)", clean)
            con.execute("DROP TABLE IF EXISTS load_log")
            con.execute("CREATE TABLE load_log (loaded_at TEXT)")
            con.execute("INSERT INTO load_log VALUES (?)",
                        (datetime.now(timezone.utc).isoformat(),))
    finally:
        con.close()


def is_fresh(loaded_at, max_age=timedelta(hours=24), now=None):
    """True when the load time (an ISO 8601 string) is no older than max_age.

    `now` is a parameter so a test can check a stale load without waiting a day.
    """
    now = now or datetime.now(timezone.utc)
    return now - datetime.fromisoformat(loaded_at) <= max_age


def run_pipeline(source, db_path):
    rows = extract(source)
    clean, rejected = transform(rows)
    load(clean, db_path)
    return {
        "read": len(rows),
        "loaded": len(clean),
        "rejected": rejected,
        "loaded_amount_total": round(sum(r["amount"] for r in clean), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Load orders.csv into SQLite.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    print(run_pipeline(args.source, args.db))


if __name__ == "__main__":
    main()

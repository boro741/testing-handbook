"""SLO gate for TaskFlow. Locust generates the load; pytest only checks the result.

Run against a server that is already up (for example `uvicorn app.main:app --port 8000`):
  pytest -q loadtest/test_slo_gate.py

Settings (environment variables, all optional):
  TASKFLOW_URL      default http://localhost:8000
  SLO_P95_MS        default 500     (95th percentile response time, milliseconds)
  SLO_ERROR_RATE    default 0.01    (failed requests / all requests, 1%)
  GATE_USERS        default 10
  GATE_SPAWN_RATE   default 2       (users started per second)
  GATE_RUN_TIME     default 30s

If no server answers at TASKFLOW_URL, every test in this file is skipped.
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

HERE = Path(__file__).resolve().parent
LOCUSTFILE = HERE / "locustfile.py"

TASKFLOW_URL = os.getenv("TASKFLOW_URL", "http://localhost:8000")
SLO_P95_MS = float(os.getenv("SLO_P95_MS", "500"))
SLO_ERROR_RATE = float(os.getenv("SLO_ERROR_RATE", "0.01"))
GATE_USERS = os.getenv("GATE_USERS", "10")
GATE_SPAWN_RATE = os.getenv("GATE_SPAWN_RATE", "2")
GATE_RUN_TIME = os.getenv("GATE_RUN_TIME", "30s")


def server_is_up(url: str) -> bool:
    try:
        return httpx.get(f"{url}/health", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="module")
def aggregated_stats(tmp_path_factory):
    """Run Locust headless once and return the 'Aggregated' row of its stats CSV."""
    if not server_is_up(TASKFLOW_URL):
        pytest.skip(f"No TaskFlow server at {TASKFLOW_URL}. Start it first (see docstring).")

    out_dir = tmp_path_factory.mktemp("locust")
    prefix = out_dir / "gate"
    cmd = [
        sys.executable, "-m", "locust",
        "-f", str(LOCUSTFILE),
        "--host", TASKFLOW_URL,
        "--headless",
        "-u", GATE_USERS, "-r", GATE_SPAWN_RATE, "-t", GATE_RUN_TIME,
        "--csv", str(prefix),
        "--only-summary",
    ]
    # Locust exit codes are not used here. The SLO thresholds decide pass or fail.
    subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=600)

    stats_file = Path(f"{prefix}_stats.csv")
    assert stats_file.exists(), f"Locust did not write {stats_file}"
    with stats_file.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row["Name"] == "Aggregated":
                return row
    pytest.fail("No 'Aggregated' row in the Locust stats CSV")


def test_p95_within_slo(aggregated_stats):
    p95_ms = float(aggregated_stats["95%"])
    assert p95_ms <= SLO_P95_MS, f"p95 {p95_ms:.0f} ms is above the {SLO_P95_MS:.0f} ms SLO"


def test_error_rate_within_slo(aggregated_stats):
    requests = int(aggregated_stats["Request Count"])
    failures = int(aggregated_stats["Failure Count"])
    assert requests > 0, "Locust sent no requests"
    error_rate = failures / requests
    assert error_rate <= SLO_ERROR_RATE, (
        f"error rate {error_rate:.2%} is above the {SLO_ERROR_RATE:.2%} SLO "
        f"({failures} of {requests} requests failed)"
    )

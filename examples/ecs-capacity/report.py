"""Render a load-test results JSON file into report.html (chapter 71).

    python report.py sample-results.json
    python report.py sample-results.json -o report.html

Reads a JSON file, works out the SLO verdict and comparison deltas, then renders
templates/report.html.j2 with Jinja2. Runs locally, no AWS calls.

The JSON must contain "data_label". The report shows it in a banner, so sample
data is never mistaken for a real measurement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

HERE = Path(__file__).resolve().parent
TEMPLATE_DIR = HERE / "templates"
TEMPLATE_NAME = "report.html.j2"
REQUIRED_KEYS = ("data_label", "report_title", "slo", "results", "scenarios")


def load_results(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"results file is missing keys: {', '.join(missing)}")
    if not str(data["data_label"]).strip():
        raise ValueError("data_label must not be empty")
    return data


def build_verdict(data: dict) -> dict:
    """Pass only if every scenario meets both the p95 and error-rate SLO."""
    slo = data["slo"]
    rows = []
    for result in data["results"]:
        p95_ok = result["p95_ms"] <= slo["p95_ms"]
        err_ok = result["error_rate_pct"] <= slo["max_error_rate_pct"]
        rows.append({**result, "p95_ok": p95_ok, "err_ok": err_ok, "pass": p95_ok and err_ok})
    failing = [row["scenario"] for row in rows if not row["pass"]]
    return {
        "passed": not failing,
        "label": "PASS" if not failing else "FAIL",
        "failing_scenarios": failing,
        "rows": rows,
    }


def build_comparison(data: dict) -> list[dict]:
    """Compare the peak scenario with the previous run. Returns [] if none given."""
    previous = data.get("previous_run")
    if not previous:
        return []
    peak = next((r for r in data["results"] if r["scenario"] == "peak"), None)
    infra = data.get("infrastructure", {})
    pairs = [
        ("Peak p95 latency (ms)", previous.get("peak_p95_ms"), peak and peak["p95_ms"]),
        ("Peak error rate (%)", previous.get("peak_error_rate_pct"), peak and peak["error_rate_pct"]),
        ("Task count", previous.get("task_count"), data["system_under_test"]["services"][0]["task_count"]),
        (
            "Task CPU, average at peak (%)",
            previous.get("task_cpu_avg_pct_peak"),
            infra.get("task_cpu_avg_pct_peak"),
        ),
        (
            "DB connections in use, peak",
            previous.get("db_connections_in_use_peak"),
            infra.get("db_connections_in_use_peak"),
        ),
    ]
    out = []
    for name, before, after in pairs:
        if before is None or after is None:
            continue
        out.append({"metric": name, "previous": before, "current": after, "delta": round(after - before, 2)})
    return out


def render(data: dict, output: Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,  # escape all values, the template is HTML
        undefined=StrictUndefined,  # fail on a missing key instead of printing blanks
    )
    template = env.get_template(TEMPLATE_NAME)
    html = template.render(
        data=data,
        verdict=build_verdict(data),
        comparison=build_comparison(data),
        max_p95=max(r["p95_ms"] for r in data["results"]),
    )
    output.write_text(html, encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a load-test results JSON to HTML.")
    parser.add_argument("results_json", type=Path, help="Path to the results JSON file")
    parser.add_argument("-o", "--output", type=Path, default=Path("report.html"), help="Output HTML file")
    args = parser.parse_args(argv)

    try:
        data = load_results(args.results_json)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    try:
        out = render(data, args.output)
    except OSError as exc:
        print(f"error: cannot write output: {exc}")
        return 2
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

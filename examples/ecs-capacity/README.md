# ECS capacity examples (Part 12)

Local helpers for chapters 64 to 71. Nothing here calls AWS, except `cloudwatch_pull.py`,
which is compile-checked only.

| File | What it does |
|---|---|
| `capacity.py` | `tasks_needed()` and a CSV CLI: `ceil(peak_rps / per_task_rps * headroom)` |
| `tests/test_capacity.py` | pytest tests for the formula and edge cases |
| `sample-capacity.csv` | Illustrative data for the CLI |
| `report.py` | Renders a load-test results JSON to `report.html` with Jinja2 |
| `templates/report.html.j2` | The 10-section report template from chapter 71 |
| `sample-results.json` | Illustrative data for the report |
| `cloudwatch_pull.py` | boto3 script that reads ALB and ECS metrics for a time window (read-only, needs AWS credentials; not run here) |

## Set up

Requires Python 3.11 or newer. Install into a local venv, using the PyPI index explicitly:

```bash
cd examples/ecs-capacity
python3 -m venv .venv
.venv/bin/pip install --index-url https://pypi.org/simple jinja2==3.1.6 boto3==1.43.125 pytest==9.2.0
```

## Run the tests

```bash
.venv/bin/python -m pytest -q tests
```

## Run the capacity CLI

```bash
.venv/bin/python capacity.py sample-capacity.csv
.venv/bin/python capacity.py sample-capacity.csv --headroom 1.5
```

The CSV needs `service`, `peak_rps` and `per_task_rps`. `headroom` is optional. A row with
`per_task_rps` of 0 or less is reported as an error and the exit code is 1.

## Generate the report

```bash
.venv/bin/python report.py sample-results.json -o report.html
open report.html
```

The script stops with a clear error if the JSON has no `data_label`. The report shows that label
as a banner, so sample data cannot pass as a real measurement. The verdict is PASS only when every
scenario meets both the p95 and error-rate SLO in the JSON.

## Check the CloudWatch script (no run)

```bash
.venv/bin/python -m py_compile cloudwatch_pull.py
```

To run it for real, you need AWS credentials with read-only access (`cloudwatch:GetMetricData`).
Only do this against an account you own, with approval.

## Notes

- Versions were checked against PyPI on 2026-11-06. Jinja2 and boto3 syntax was checked with Context7
  (`/pallets/jinja`, `/boto/boto3`).
- All numbers in `sample-capacity.csv` and `sample-results.json` are invented. Treat them as Illustrative data.

# TaskFlow (local)

The fictional app used by every example in the Software Testing Handbook.

| Run | Command |
|---|---|
| Install (core: offline tests and load tests) | `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt` |
| Install extras (browser tests, mutation testing, static analysis; large) | `pip install -r requirements-extra.txt && python -m playwright install chromium` |
| Start API + UI | `uvicorn app.main:app --reload` → open http://localhost:8000 (UI), http://localhost:8000/docs (OpenAPI) |
| Start with Postgres | `docker compose up --build` |
| Offline tests (API, security, property, unit, BDD, doubles, Pact consumer): 94 tests, no server needed | `pytest -q` |
| UI tests (needs the extras above and a running server) | `pytest ui-tests --base-url http://localhost:8000` |
| Visual tests (needs the extras above; first run creates baselines, second run compares) | `BASE_URL=http://localhost:8000 pytest visual` |
| Load gate (needs a running server; about 30 s) | `pytest loadtest` |
| Postman CLI collection (no login needed to run) | `postman collection run postman/collections/taskflow-api -e postman/environments/local.environment.yaml --env-var baseUrl=http://localhost:8000` |
| Load smoke test | `locust -f loadtest/locustfile.py --host http://localhost:8000 --headless -u 10 -r 2 -t 1m --csv results/smoke` |
| Export OpenAPI | `python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json` |

Demo users: `alice / alice-pass`, `bob / bob-pass`. Project id `1` is "Demo project" (both are members).

Not included locally (they exist only in the production reference architecture): SQS/SNS, Redis, ECS, ALB.
Passwords are plain text and tokens are in memory. This is a demo, not a template for real auth.

"""Pact consumer test: the TaskFlow web UI (consumer) and task-service (provider).

Covers POST /api/auth/login and GET /api/tasks/{id}. The tiny client below does
what static/index.html does with fetch(). Run:  pytest contract
The pact file is written to a temporary folder, not to the repo.
"""
import httpx
import pytest
from pact import Pact, match


class WebClient:
    """Minimal stand-in for the calls the web UI makes."""

    def __init__(self, base_url: str) -> None:
        self.http = httpx.Client(base_url=base_url, timeout=5.0)

    def login(self, username: str, password: str) -> httpx.Response:
        return self.http.post("/api/auth/login", json={"username": username, "password": password})

    def get_task(self, task_id: int, token: str) -> httpx.Response:
        return self.http.get(f"/api/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def pact(tmp_path):
    p = Pact("taskflow-web", "task-service").with_specification("V4")
    yield p
    p.write_file(tmp_path / "pacts", overwrite=True)


def test_login(pact: Pact):
    (pact.upon_receiving("a login with valid credentials")
         .given("user alice exists")
         .with_request("POST", "/api/auth/login")
         .with_body({"username": "alice", "password": "alice-pass"}, content_type="application/json")
         .will_respond_with(200)
         .with_body({"token": match.str("abc123"), "user_id": match.int(1)},
                    content_type="application/json"))
    with pact.serve() as srv:
        res = WebClient(str(srv.url)).login("alice", "alice-pass")
        assert res.status_code == 200
        assert set(res.json()) == {"token", "user_id"}


def test_get_task(pact: Pact):
    (pact.upon_receiving("a request for task 1")
         .given("task 1 exists and the token belongs to a project member")
         .with_request("GET", "/api/tasks/1")
         .with_header("Authorization", "Bearer abc123")
         .will_respond_with(200)
         .with_body({"id": match.int(1), "title": match.str("Write tests"),
                     "priority": match.str("MEDIUM"), "status": match.str("TODO"),
                     "project_id": match.int(1), "assignee_id": match.none()},
                    content_type="application/json"))
    with pact.serve() as srv:
        res = WebClient(str(srv.url)).get_task(1, "abc123")
        assert res.status_code == 200
        assert res.json()["title"] == "Write tests"

"""pytest-bdd steps for assign_task.feature. Run from examples/taskflow: pytest bdd -q"""
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app.main import app

scenarios("assign_task.feature")

USER_IDS = {"alice": 1, "bob": 2}  # seeded demo users


@pytest.fixture()
def client():
    from app.main import Base, TOKENS, engine
    Base.metadata.drop_all(engine)  # fresh database, lifespan re-seeds it
    TOKENS.clear()
    with TestClient(app) as c:
        yield c


@given("alice is logged in", target_fixture="headers")
def alice_logged_in(client):
    r = client.post("/api/auth/login", json={"username": "alice", "password": "alice-pass"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _create_task(client, headers, project_id):
    r = client.post("/api/tasks", headers=headers,
                    json={"title": "Write release notes", "priority": "LOW", "project_id": project_id})
    return r.json()["id"]


@given("a task exists in the Demo project", target_fixture="task_id")
def task_in_demo(client, headers):
    return _create_task(client, headers, project_id=1)


@given("a task exists in a project that only alice belongs to", target_fixture="task_id")
def task_in_solo(client, headers):
    project_id = client.post("/api/projects", headers=headers, json={"name": "Solo"}).json()["id"]
    return _create_task(client, headers, project_id)


@when(parsers.parse("alice assigns the task to {name}"), target_fixture="response")
def assign(client, headers, task_id, name):
    return client.post(f"/api/tasks/{task_id}/assign", headers=headers, json={"user_id": USER_IDS[name]})


@then(parsers.parse("the response status is {code:d}"))
def check_status(response, code):
    assert response.status_code == code, response.text


@then("the task assignee is bob")
def assignee_is_bob(client, headers, task_id):
    assert client.get(f"/api/tasks/{task_id}", headers=headers).json()["assignee_id"] == 2


@then("the task has no assignee")
def no_assignee(client, headers, task_id):
    assert client.get(f"/api/tasks/{task_id}", headers=headers).json()["assignee_id"] is None

"""Guard tests for login as bob and task listing by project."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    from app.main import Base, engine, TOKENS
    Base.metadata.drop_all(engine)
    TOKENS.clear()
    with TestClient(app) as c:
        yield c


def login(client, username, password):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_bob_with_wrong_password_is_401(client):
    r = client.post("/api/auth/login", json={"username": "bob", "password": "not-bobs-password"})
    assert r.status_code == 401


def test_list_only_returns_tasks_from_the_requested_project(client):
    alice = login(client, "alice", "alice-pass")
    bob = login(client, "bob", "bob-pass")
    # Bob makes a project that alice is not a member of, with one task in it.
    project = client.post("/api/projects", headers=bob, json={"name": "Bob only", "member_ids": []})
    assert project.status_code == 201, project.text
    task = client.post("/api/tasks", headers=bob,
                       json={"title": "Not for alice", "priority": "LOW", "project_id": project.json()["id"]})
    assert task.status_code == 201, task.text
    # Alice lists project 1, where she is a member. Bob's task must not appear.
    r = client.get("/api/tasks", headers=alice, params={"project_id": 1})
    assert r.status_code == 200, r.text
    assert task.json()["id"] not in [t["id"] for t in r.json()]
    assert all(t["project_id"] == 1 for t in r.json())

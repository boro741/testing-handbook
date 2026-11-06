"""API tests for TaskFlow. Run with: pytest -q (from examples/taskflow)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    # Fresh database for every test. Lifespan runs create_all + seed.
    from app.main import Base, engine, TOKENS
    Base.metadata.drop_all(engine)
    TOKENS.clear()
    with TestClient(app) as c:
        yield c


def login(client, username="alice", password="alice-pass"):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def new_task(client, headers, title="Write tests", priority="MEDIUM"):
    return client.post("/api/tasks", headers=headers,
                       json={"title": title, "priority": priority, "project_id": 1})


# --- authentication -------------------------------------------------------

def test_login_with_correct_password_returns_token(client):
    r = client.post("/api/auth/login", json={"username": "alice", "password": "alice-pass"})
    assert r.status_code == 200
    assert r.json()["token"]


def test_login_with_wrong_password_is_401(client):
    r = client.post("/api/auth/login", json={"username": "alice", "password": "nope"})
    assert r.status_code == 401


def test_request_without_token_is_401(client):
    r = client.post("/api/tasks", json={"title": "x", "priority": "LOW", "project_id": 1})
    assert r.status_code == 401


# --- title rule: 1 to 100 characters (boundary value analysis) --------------

@pytest.mark.parametrize("length, expected", [(0, 422), (1, 201), (100, 201), (101, 422)])
def test_task_title_length_boundaries(client, length, expected):
    r = new_task(client, login(client), title="a" * length)
    assert r.status_code == expected, r.text


# --- priority rule: LOW, MEDIUM or HIGH -------------------------------------

@pytest.mark.parametrize("priority", ["LOW", "MEDIUM", "HIGH"])
def test_valid_priorities_are_accepted(client, priority):
    assert new_task(client, login(client), priority=priority).status_code == 201


@pytest.mark.parametrize("priority", ["URGENT", "low", ""])
def test_invalid_priorities_are_rejected(client, priority):
    assert new_task(client, login(client), priority=priority).status_code == 422


# --- status flow: TODO -> IN_PROGRESS -> IN_REVIEW -> DONE, REOPENED ---------

def test_status_follows_the_allowed_path(client):
    h = login(client)
    task_id = new_task(client, h).json()["id"]
    for status in ["IN_PROGRESS", "IN_REVIEW", "DONE", "REOPENED", "IN_PROGRESS"]:
        r = client.put(f"/api/tasks/{task_id}", headers=h, json={"status": status})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == status


def test_skipping_a_step_is_409(client):
    h = login(client)
    task_id = new_task(client, h).json()["id"]
    r = client.put(f"/api/tasks/{task_id}", headers=h, json={"status": "DONE"})
    assert r.status_code == 409


# --- project membership -------------------------------------------------------

def test_non_member_cannot_create_task_in_project(client):
    # Create a project that only bob belongs to, then try as alice.
    bob = login(client, "bob", "bob-pass")
    project_id = client.post("/api/projects", headers=bob, json={"name": "Bob only"}).json()["id"]
    alice = login(client)
    r = client.post("/api/tasks", headers=alice,
                    json={"title": "sneaky", "priority": "LOW", "project_id": project_id})
    assert r.status_code == 403


def test_only_project_members_can_be_assigned(client):
    h = login(client)
    alice_bob_project = client.post("/api/projects", headers=h, json={"name": "Solo"}).json()["id"]
    task = client.post("/api/tasks", headers=h, json={
        "title": "Assign me", "priority": "LOW", "project_id": alice_bob_project}).json()
    # bob is in the Demo project (id 1), not in "Solo"
    r = client.post(f"/api/tasks/{task['id']}/assign", headers=h, json={"user_id": 2})
    assert r.status_code == 422


def test_assign_a_member_works(client):
    h = login(client)
    task_id = new_task(client, h).json()["id"]
    r = client.post(f"/api/tasks/{task_id}/assign", headers=h, json={"user_id": 2})
    assert r.status_code == 200
    assert r.json()["assignee_id"] == 2


# --- delete ------------------------------------------------------------------

def test_deleted_task_is_gone(client):
    h = login(client)
    task_id = new_task(client, h).json()["id"]
    assert client.delete(f"/api/tasks/{task_id}", headers=h).status_code == 204
    assert client.get(f"/api/tasks/{task_id}", headers=h).status_code == 404

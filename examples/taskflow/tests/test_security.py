"""Security tests for TaskFlow: injection, object-level access and missing tokens."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

PAYLOADS = ["' OR '1'='1", "alice'--", "'; DROP TABLE users;--", "\" OR \"\"=\""]


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


@pytest.fixture()
def private_task(client):
    """A task in a project that only alice belongs to. Returns (task_id, bob headers)."""
    alice = login(client, "alice", "alice-pass")
    # bob is the stranger: a real user who is NOT a member of the new project.
    project = client.post("/api/projects", headers=alice, json={"name": "Secret", "member_ids": []})
    task = client.post("/api/tasks", headers=alice,
                       json={"title": "Private", "priority": "LOW", "project_id": project.json()["id"]})
    assert task.status_code == 201, task.text
    return task.json()["id"], login(client, "bob", "bob-pass")


# --- (a) injection ----------------------------------------------------------

@pytest.mark.parametrize("payload", PAYLOADS)
def test_injection_in_login_username_is_rejected(client, payload):
    r = client.post("/api/auth/login", json={"username": payload, "password": payload})
    assert r.status_code == 401


@pytest.mark.parametrize("payload", PAYLOADS)
def test_injection_in_password_does_not_bypass_login(client, payload):
    r = client.post("/api/auth/login", json={"username": "alice", "password": payload})
    assert r.status_code == 401


@pytest.mark.parametrize("payload", PAYLOADS)
def test_injection_in_task_title_is_stored_as_plain_text(client, payload):
    h = login(client, "alice", "alice-pass")
    r = client.post("/api/tasks", headers=h, json={"title": payload, "priority": "LOW", "project_id": 1})
    assert r.status_code == 201
    assert client.get(f"/api/tasks/{r.json()['id']}", headers=h).json()["title"] == payload
    # The users table still works after the payload.
    login(client, "alice", "alice-pass")


# --- (b) object-level authorization (BOLA) ----------------------------------

def test_non_member_cannot_read_task(client, private_task):
    task_id, stranger = private_task
    assert client.get(f"/api/tasks/{task_id}", headers=stranger).status_code == 403


def test_non_member_cannot_update_task(client, private_task):
    task_id, stranger = private_task
    r = client.put(f"/api/tasks/{task_id}", headers=stranger, json={"title": "hacked"})
    assert r.status_code == 403


def test_non_member_cannot_delete_task(client, private_task):
    task_id, stranger = private_task
    assert client.delete(f"/api/tasks/{task_id}", headers=stranger).status_code == 403


def test_non_member_cannot_assign_task(client, private_task):
    task_id, stranger = private_task
    r = client.post(f"/api/tasks/{task_id}/assign", headers=stranger, json={"user_id": 2})
    assert r.status_code == 403


# --- (c) missing or invalid token -------------------------------------------

BAD_AUTH = [{}, {"Authorization": "Bearer not-a-real-token"}, {"Authorization": "Basic abc"}]
ENDPOINTS = [
    ("post", "/api/tasks", {"title": "x", "priority": "LOW", "project_id": 1}),
    ("get", "/api/tasks?project_id=1", None),
    ("get", "/api/tasks/1", None),
    ("put", "/api/tasks/1", {"title": "y"}),
    ("delete", "/api/tasks/1", None),
    ("post", "/api/tasks/1/assign", {"user_id": 1}),
]


@pytest.mark.parametrize("headers", BAD_AUTH, ids=["missing", "invalid", "wrong-scheme"])
@pytest.mark.parametrize("method, path, body", ENDPOINTS)
def test_task_endpoints_require_a_valid_token(client, method, path, body, headers):
    r = client.request(method.upper(), path, headers=headers, json=body)
    assert r.status_code == 401

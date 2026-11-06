"""Property-based tests (Hypothesis) for the TaskFlow title and priority rules."""
import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings, strategies as st

from app.main import app

# Characters that survive JSON and the database unchanged (no surrogates).
text_chars = st.characters(blacklist_categories=("Cs",))
SETTINGS = settings(max_examples=40, deadline=None,
                    suppress_health_check=[HealthCheck.function_scoped_fixture])


@pytest.fixture()
def client():
    from app.main import Base, engine, TOKENS
    Base.metadata.drop_all(engine)
    TOKENS.clear()
    with TestClient(app) as c:
        yield c


def headers(client):
    r = client.post("/api/auth/login", json={"username": "alice", "password": "alice-pass"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def create(client, title, priority="MEDIUM"):
    return client.post("/api/tasks", headers=headers(client),
                       json={"title": title, "priority": priority, "project_id": 1})


@SETTINGS
@given(title=st.text(alphabet=text_chars, min_size=1, max_size=100))
def test_any_title_of_1_to_100_chars_is_accepted_and_returned_unchanged(client, title):
    r = create(client, title)
    assert r.status_code == 201, r.text
    assert r.json()["title"] == title


@SETTINGS
@given(title=st.text(alphabet=text_chars, min_size=101, max_size=300))
def test_any_title_over_100_chars_is_rejected(client, title):
    assert create(client, title).status_code == 422


@SETTINGS
@given(priority=st.text(max_size=12).filter(lambda p: p not in {"LOW", "MEDIUM", "HIGH"}))
def test_any_other_priority_is_rejected(client, priority):
    assert create(client, "ok", priority).status_code == 422


@SETTINGS
@given(priority=st.sampled_from(["LOW", "MEDIUM", "HIGH"]))
def test_every_allowed_priority_is_accepted(client, priority):
    assert create(client, "ok", priority).status_code == 201

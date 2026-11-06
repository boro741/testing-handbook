"""Unit tests for TaskFlow's rule constants and validators.

No HTTP, no database, no server. Run from examples/taskflow: pytest unit -q
"""
import pytest
from pydantic import ValidationError

from app.main import PRIORITIES, TRANSITIONS, TaskCreate, TaskUpdate

ALL_STATUSES = {"TODO", "IN_PROGRESS", "IN_REVIEW", "DONE", "REOPENED"}


def test_priorities_are_exactly_low_medium_high():
    assert PRIORITIES == {"LOW", "MEDIUM", "HIGH"}


def test_every_status_has_a_rule_and_targets_are_real_statuses():
    assert set(TRANSITIONS) == ALL_STATUSES
    for targets in TRANSITIONS.values():
        assert targets <= ALL_STATUSES


@pytest.mark.parametrize("start, end", [
    ("TODO", "IN_PROGRESS"), ("IN_PROGRESS", "IN_REVIEW"), ("IN_PROGRESS", "TODO"),
    ("IN_REVIEW", "DONE"), ("IN_REVIEW", "IN_PROGRESS"),
    ("DONE", "REOPENED"), ("REOPENED", "IN_PROGRESS"),
])
def test_allowed_moves(start, end):
    assert end in TRANSITIONS[start]


@pytest.mark.parametrize("start, end", [
    ("TODO", "DONE"), ("TODO", "IN_REVIEW"), ("DONE", "TODO"), ("REOPENED", "DONE"),
])
def test_forbidden_moves(start, end):
    assert end not in TRANSITIONS[start]


def test_done_can_only_be_reopened():
    assert TRANSITIONS["DONE"] == {"REOPENED"}


@pytest.mark.parametrize("length, ok", [(0, False), (1, True), (100, True), (101, False)])
def test_title_length_rule(length, ok):
    make = lambda: TaskCreate(title="a" * length, priority="LOW", project_id=1)
    if ok:
        make()
    else:
        with pytest.raises(ValidationError):
            make()


@pytest.mark.parametrize("priority", ["URGENT", "low", ""])
def test_invalid_priority_is_rejected(priority):
    with pytest.raises(ValidationError):
        TaskCreate(title="x", priority=priority, project_id=1)


def test_update_allows_missing_priority_but_not_a_bad_one():
    assert TaskUpdate().priority is None
    with pytest.raises(ValidationError):
        TaskUpdate(priority="URGENT")

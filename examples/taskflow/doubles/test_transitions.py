"""Deliberately incomplete tests: they reach 100% line coverage but miss things."""
from doubles.transitions import can_move


def test_valid_move():
    assert can_move("TODO", "IN_PROGRESS")


def test_invalid_move():
    assert not can_move("TODO", "DONE")


def test_same_status_is_allowed():
    assert can_move("TODO", "TODO")

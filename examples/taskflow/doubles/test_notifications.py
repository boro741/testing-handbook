"""Test doubles in action. Run: pytest -q doubles (from examples/taskflow)."""
from unittest.mock import Mock

import pytest

from doubles.notifications import notify_assigned


class FakePublisher:
    """A fake: a real, simple working implementation (in-memory 'queue')."""

    def __init__(self, fail_first=0):
        self.messages = []
        self._fail = fail_first

    def publish(self, topic, event):
        if self._fail:
            self._fail -= 1
            raise ConnectionError("broker down")
        self.messages.append((topic, event))


def test_fake_collects_the_event():
    fake = FakePublisher()
    notify_assigned(fake, task_id=7, assignee_id=2, clock=lambda: 1000.0)  # stub clock
    assert fake.messages == [("task.assigned", {"type": "task.assigned", "task_id": 7,
                                                "assignee_id": 2, "at": 1000.0})]


def test_fake_survives_one_failure_then_delivers():
    fake = FakePublisher(fail_first=1)
    notify_assigned(fake, 7, 2)
    assert len(fake.messages) == 1


def test_mock_verifies_the_call():
    publisher = Mock()
    notify_assigned(publisher, 7, 2, clock=lambda: 5.0)
    publisher.publish.assert_called_once_with(
        "task.assigned",
        {"type": "task.assigned", "task_id": 7, "assignee_id": 2, "at": 5.0})


def test_mock_with_side_effect_checks_retry():
    publisher = Mock()
    publisher.publish.side_effect = [ConnectionError("down"), None]
    notify_assigned(publisher, 7, 2)
    assert publisher.publish.call_count == 2


def test_second_failure_is_raised():
    publisher = Mock()
    publisher.publish.side_effect = ConnectionError("down")
    with pytest.raises(ConnectionError):
        notify_assigned(publisher, 7, 2)


def test_no_assignee_publishes_nothing():
    publisher = Mock()
    with pytest.raises(ValueError):
        notify_assigned(publisher, 7, None)
    publisher.publish.assert_not_called()

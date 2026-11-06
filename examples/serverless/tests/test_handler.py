import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import handler  # noqa: E402


def _record(message_id: str, body) -> dict:
    text = body if isinstance(body, str) else json.dumps(body)
    return {"messageId": message_id, "body": text}


def _task(title: str = "Write docs", **extra) -> dict:
    return {"title": title, "priority": "MEDIUM", **extra}


def setup_function():
    handler.TASKS.clear()


def test_valid_record_is_stored():
    result = handler.handler({"Records": [_record("m1", _task("Write docs"))]})

    assert result == {"batchItemFailures": []}
    assert len(handler.TASKS) == 1
    stored = next(iter(handler.TASKS.values()))
    assert stored["title"] == "Write docs"
    assert stored["status"] == "TODO"


def test_bad_json_record_is_reported_in_batch_failures():
    event = {"Records": [_record("good", _task("OK")), _record("bad", "{not json")]}

    result = handler.handler(event)

    assert result == {"batchItemFailures": [{"itemIdentifier": "bad"}]}
    assert len(handler.TASKS) == 1


def test_empty_batch_returns_no_failures():
    assert handler.handler({"Records": []}) == {"batchItemFailures": []}
    assert handler.TASKS == {}


def test_title_longer_than_100_characters_is_rejected():
    too_long = "x" * 101
    result = handler.handler({"Records": [_record("long", _task(too_long))]})

    assert result == {"batchItemFailures": [{"itemIdentifier": "long"}]}
    assert handler.TASKS == {}


def test_title_of_exactly_100_characters_is_accepted():
    result = handler.handler({"Records": [_record("edge", _task("x" * 100))]})

    assert result == {"batchItemFailures": []}
    assert len(handler.TASKS) == 1


def test_missing_priority_is_rejected_like_the_taskflow_api():
    result = handler.handler({"Records": [_record("nopri", {"title": "No priority"})]})

    assert result == {"batchItemFailures": [{"itemIdentifier": "nopri"}]}
    assert handler.TASKS == {}


def test_unknown_priority_is_rejected():
    result = handler.handler({"Records": [_record("urgent", _task(priority="URGENT"))]})

    assert result == {"batchItemFailures": [{"itemIdentifier": "urgent"}]}
    assert handler.TASKS == {}

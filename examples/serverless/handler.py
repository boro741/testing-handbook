"""A small Lambda-style handler for an SQS event. No AWS calls are made here.

The handler reads each SQS record, parses its JSON body and stores a task in
the in-memory TASKS dict. Failed records are returned in batchItemFailures,
the response shape that Lambda uses for partial batch responses.
"""
import json

TASKS: dict[int, dict] = {}
MAX_TITLE = 100
_next_id = 1


def _validate(task: dict) -> None:
    title = task.get("title")
    if not isinstance(title, str) or not (1 <= len(title) <= MAX_TITLE):
        raise ValueError("title must be 1 to 100 characters")
    # Same rule as the TaskFlow API: priority is required, and it must be one of three values.
    if task.get("priority") not in ("LOW", "MEDIUM", "HIGH"):
        raise ValueError("priority is required and must be LOW, MEDIUM or HIGH")


def _store(task: dict) -> int:
    global _next_id
    task_id = _next_id
    _next_id += 1
    TASKS[task_id] = {"id": task_id, "status": "TODO", **task}
    return task_id


def handler(event: dict, context=None) -> dict:
    failures = []
    for record in event.get("Records", []):
        try:
            task = json.loads(record["body"])
            _validate(task)
            _store(task)
        except (ValueError, KeyError, TypeError):
            failures.append({"itemIdentifier": record.get("messageId", "")})
    return {"batchItemFailures": failures}

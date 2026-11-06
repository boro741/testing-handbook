"""Publish a task.assigned event. Lives here so we do not touch app/.

In the production reference architecture task-service sends this event to
SNS/SQS and notification-service reads it. Locally there is no queue, so the
publisher is passed in. That makes it easy to replace in tests.
"""
import time


def notify_assigned(publisher, task_id, assignee_id, clock=time.time):
    """Send one task.assigned event. Retry once if the publisher fails."""
    if assignee_id is None:
        raise ValueError("task has no assignee")
    event = {"type": "task.assigned", "task_id": task_id,
             "assignee_id": assignee_id, "at": clock()}
    try:
        publisher.publish("task.assigned", event)
    except ConnectionError:
        publisher.publish("task.assigned", event)  # one retry
    return event

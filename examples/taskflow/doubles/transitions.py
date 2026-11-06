"""Status transition check, re-implemented here as a small target for mutmut."""
TRANSITIONS = {
    "TODO": {"IN_PROGRESS"},
    "IN_PROGRESS": {"IN_REVIEW", "TODO"},
    "IN_REVIEW": {"DONE", "IN_PROGRESS"},
    "DONE": {"REOPENED"},
    "REOPENED": {"IN_PROGRESS"},
}


def can_move(current: str, new: str) -> bool:
    """Staying in the same status is allowed; other moves must be in TRANSITIONS."""
    if current == new:
        return True
    return new in TRANSITIONS.get(current, set())

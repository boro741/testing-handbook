"""Check that every seeded bug (B01 to B08) makes at least one existing test fail.

For each ID, runs `pytest tests` in examples/taskflow with TASKFLOW_BUGS set to
that ID. A bug is "caught" when at least one test fails. Exits 1 if any bug is
not caught, so it can run in CI.

Usage (from any directory):
    python3 examples/taskflow/bug-hunt/verify_bugs_detectable.py
"""
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
BUG_IDS = [f"B0{n}" for n in range(1, 9)]


def run_for_bug(bug_id: str) -> tuple[int, int]:
    """Return (number of failing tests, pytest exit code) for one bug."""
    env = dict(os.environ, TASKFLOW_BUGS=bug_id)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-rf"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    failed = [line for line in result.stdout.splitlines() if line.startswith("FAILED")]
    return len(failed), result.returncode


def main() -> int:
    not_caught = []
    for bug_id in BUG_IDS:
        failed, code = run_for_bug(bug_id)
        if code not in (0, 1):
            # 2+ means pytest itself broke (collection error, usage error, etc.)
            print(f"{bug_id}: ERROR (pytest exit code {code})")
            not_caught.append(bug_id)
        elif failed == 0:
            print(f"{bug_id}: NOT CAUGHT")
            not_caught.append(bug_id)
        else:
            print(f"{bug_id}: caught by {failed} test(s)")
    if not_caught:
        print(f"FAILED: {len(not_caught)} bug(s) not caught: {', '.join(not_caught)}")
        return 1
    print("OK: every bug is caught by at least one test")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# TaskFlow bug hunt

This folder holds a practice set for finding bugs. The TaskFlow app in
`examples/taskflow/app/main.py` contains eight seeded bugs. They are off by
default, so the app works normally until you turn them on.

## Turn bugs on

Set the environment variable `TASKFLOW_BUGS` before you start the app or run the tests.
It takes a comma-separated list of bug IDs, or `all`.

```bash
# One bug
TASKFLOW_BUGS=B01 uvicorn app.main:app --port 8000

# Several bugs
TASKFLOW_BUGS=B02,B05 python3 -m pytest tests -q

# Every bug
TASKFLOW_BUGS=all uvicorn app.main:app --port 8000
```

The app reads the variable on every request. Unset or empty means the bug-free app.

## The IDs are not the answers

The IDs (B01 to B08) are labels only. They do not say what is wrong or where
to look. Your job is to find out what each bug does, which test notices it,
and how to show it with a request.

**Spoilers.** The answers are in two places: the project answer key page in the handbook,
and `SPOILERS.md` in this folder. Try to find each bug before you open either one.
Please do not search `app/main.py` for the bug switch either: finding bugs by testing is the exercise.

One note for maintainers: bug B01 (an over-long title is accepted) behaves as described on the
default SQLite setup. On Postgres the column limit would reject that title with a server error.

## Check that every bug is detectable

The script `verify_bugs_detectable.py` runs the offline test suite once for each
bug ID. It prints how many tests fail for each bug. It exits with a non-zero
code if a bug has no failing test.

```bash
cd examples/taskflow
python3 bug-hunt/verify_bugs_detectable.py
```

The script uses only the standard library. It needs the project's test
requirements installed, for example in `.venv`.

## Rules for this practice

- Do not edit `app/main.py` to find a bug. Turn the bug on with `TASKFLOW_BUGS` instead.
- Use a separate database file when you run the server, so you do not reuse
  data from an earlier run.

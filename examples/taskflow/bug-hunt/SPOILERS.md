# SPOILERS: TaskFlow bug hunt answer key

Stop here if you are doing the practice project. This file names every seeded bug.

Each row was checked by running the offline suite with `TASKFLOW_BUGS` set to that ID
(`pytest tests unit bdd doubles`), and by the curl steps below against a live server.
Expected results with the bug off are in brackets.

Test counts below are for `tests unit bdd doubles`. `bug-hunt/verify_bugs_detectable.py`
runs `tests` only, so its counts are lower (B01: 2, B02: 1, B03: 1, B04: 1, B05: 1, B06: 1, B07: 1, B08: 4).

## Setup

Start a server with the bug on, using a fresh database file. Then run this once:

```bash
B=http://localhost:8000
A=$(curl -s -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice-pass"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
BOB=$(curl -s -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"username":"bob","password":"bob-pass"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
T=$(curl -s -X POST $B/api/tasks -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d '{"title":"s","priority":"LOW","project_id":1}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
P2=$(curl -s -X POST $B/api/projects -H "Authorization: Bearer $BOB" -H 'Content-Type: application/json' -d '{"name":"Bob only","member_ids":[]}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
T2=$(curl -s -X POST $B/api/tasks -H "Authorization: Bearer $BOB" -H 'Content-Type: application/json' -d "{\"title\":\"bob task\",\"priority\":\"LOW\",\"project_id\":$P2}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
P3=$(curl -s -X POST $B/api/projects -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d '{"name":"Alice only","member_ids":[]}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
T3=$(curl -s -X POST $B/api/tasks -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d "{\"title\":\"a\",\"priority\":\"LOW\",\"project_id\":$P3}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
```

## Answers

| ID | What it does | Test that catches it | Reproduce with curl (bug on, then off) |
|---|---|---|---|
| B01 | A 101-character title is accepted (201). [Off: 422 string_too_long] | `tests/test_taskflow_api.py::test_task_title_length_boundaries[101-422]`, `tests/test_properties.py::test_any_title_over_100_chars_is_rejected`, `unit/test_status_rules.py::test_title_length_rule[101-False]` | `curl -s -o /dev/null -w '%{http_code}\n' -X POST $B/api/tasks -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d "{\"title\":\"$(printf 'x%.0s' $(seq 101))\",\"priority\":\"LOW\",\"project_id\":1}"` → 201 [422] |
| B02 | TODO to DONE is allowed (200). [Off: 409 Cannot move from TODO to DONE] | `tests/test_taskflow_api.py::test_skipping_a_step_is_409` | `curl -s -X PUT $B/api/tasks/$T -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d '{"status":"DONE"}'` → 200 [409] |
| B03 | A non-member can read a task (200). [Off: 403 Not a member of this project] | `tests/test_security.py::test_non_member_cannot_read_task` | `curl -s -w ' %{http_code}\n' $B/api/tasks/$T2 -H "Authorization: Bearer $A"` → 200 [403] |
| B04 | A non-member can be assigned a task (200). [Off: 422 Assignee is not a project member] | `tests/test_taskflow_api.py::test_only_project_members_can_be_assigned`, `bdd/test_assign_task.py::test_assign_a_task_to_someone_who_is_not_a_member_of_the_project` | `curl -s -o /dev/null -w '%{http_code}\n' -X POST $B/api/tasks/$T3/assign -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d '{"user_id":2}'` → 200 [422] |
| B05 | DELETE returns 204, but the task is still there (GET returns 200). [Off: GET returns 404] | `tests/test_taskflow_api.py::test_deleted_task_is_gone` | `curl -s -o /dev/null -w '%{http_code}\n' -X DELETE $B/api/tasks/$T -H "Authorization: Bearer $A"` then `curl -s -o /dev/null -w '%{http_code}\n' $B/api/tasks/$T -H "Authorization: Bearer $A"` → 204, then 200 [404] |
| B06 | Bob logs in with any password (200 with a token). [Off: 401] | `tests/test_bug_guards.py::test_bob_with_wrong_password_is_401` | `curl -s -w ' %{http_code}\n' -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"username":"bob","password":"wrong"}'` → 200 [401] |
| B07 | The list ignores the project: tasks from other projects appear (Bob's task $T2 shows up in project 1). [Off: only project 1 tasks] | `tests/test_bug_guards.py::test_list_only_returns_tasks_from_the_requested_project` | `curl -s "$B/api/tasks?project_id=1" -H "Authorization: Bearer $A"` → includes task $T2 from project $P2 [only project 1 tasks] |
| B08 | Priority URGENT (and other non-allowed values) is accepted (201). [Off: 422] | `tests/test_taskflow_api.py::test_invalid_priorities_are_rejected`, `tests/test_properties.py::test_any_other_priority_is_rejected`, `unit/test_status_rules.py::test_invalid_priority_is_rejected` | `curl -s -o /dev/null -w '%{http_code}\n' -X POST $B/api/tasks -H "Authorization: Bearer $A" -H 'Content-Type: application/json' -d '{"title":"p","priority":"URGENT","project_id":1}'` → 201 [422] |

Run the B05 steps in order: the delete happens after B02 has used `$T`.

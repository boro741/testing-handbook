// k6 smoke test for TaskFlow. Run from examples/taskflow:
//   k6 run loadtest/k6-smoke.js
//   k6 run -e BASE_URL=http://localhost:8000 loadtest/k6-smoke.js
// Start the API first: .venv/bin/uvicorn app.main:app --port 8000
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const JSON_HEADERS = { 'Content-Type': 'application/json' };

export const options = {
  vus: 2,
  duration: '30s',
  thresholds: {
    // Overall error rate across all requests.
    http_req_failed: ['rate<0.01'],
    // Share of checks that pass.
    checks: ['rate>0.99'],
    // Per-endpoint latency. The tag is set on each request below.
    'http_req_duration{endpoint:login}': ['p(95)<500'],
    'http_req_duration{endpoint:create_task}': ['p(95)<500'],
    'http_req_duration{endpoint:get_task}': ['p(95)<300'],
    'http_req_duration{endpoint:list_tasks}': ['p(95)<500'],
    'http_req_duration{endpoint:update_task}': ['p(95)<500'],
  },
};

export default function () {
  // 1. Log in as a demo user. The token is a bearer token.
  const login = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ username: 'alice', password: 'alice-pass' }),
    { headers: JSON_HEADERS, tags: { endpoint: 'login' } },
  );
  check(login, { 'login is 200': (r) => r.status === 200 });
  const auth = { Authorization: `Bearer ${login.json('token')}` };

  // 2. Create a task in project 1 (Demo project).
  const created = http.post(
    `${BASE_URL}/api/tasks`,
    JSON.stringify({ title: 'k6 smoke task', priority: 'LOW', project_id: 1 }),
    { headers: { ...JSON_HEADERS, ...auth }, tags: { endpoint: 'create_task' } },
  );
  check(created, { 'create is 201': (r) => r.status === 201 });
  const taskId = created.json('id');

  // 3. Read the task back.
  const read = http.get(`${BASE_URL}/api/tasks/${taskId}`, {
    headers: auth,
    tags: { endpoint: 'get_task' },
  });
  check(read, { 'get is 200': (r) => r.status === 200 });

  // 4. List the project's tasks.
  const list = http.get(`${BASE_URL}/api/tasks?project_id=1`, {
    headers: auth,
    tags: { endpoint: 'list_tasks' },
  });
  check(list, { 'list is 200': (r) => r.status === 200 });

  // 5. Change the priority.
  const updated = http.put(
    `${BASE_URL}/api/tasks/${taskId}`,
    JSON.stringify({ priority: 'HIGH' }),
    { headers: { ...JSON_HEADERS, ...auth }, tags: { endpoint: 'update_task' } },
  );
  check(updated, { 'update is 200': (r) => r.status === 200 });

  sleep(1);
}

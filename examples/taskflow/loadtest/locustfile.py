"""Locust load test for TaskFlow. Locust generates the load; pytest is not used for this.

Smoke run (headless, 10 users, 1 minute):
  locust -f loadtest/locustfile.py --host http://localhost:8000 \
         --headless -u 10 -r 2 -t 1m --csv results/smoke
"""
from locust import HttpUser, between, task


class TaskFlowUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        r = self.client.post("/api/auth/login", json={"username": "alice", "password": "alice-pass"},
                             name="POST /api/auth/login")
        self.headers = {"Authorization": f"Bearer {r.json()['token']}"}
        self.task_ids: list[int] = []

    @task(3)
    def create_and_read(self):
        r = self.client.post("/api/tasks", headers=self.headers, name="POST /api/tasks",
                             json={"title": "Load test task", "priority": "LOW", "project_id": 1})
        if r.status_code == 201:
            task_id = r.json()["id"]
            self.task_ids.append(task_id)
            self.client.get(f"/api/tasks/{task_id}", headers=self.headers, name="GET /api/tasks/{id}")

    @task(5)
    def list_tasks(self):
        self.client.get("/api/tasks?project_id=1", headers=self.headers, name="GET /api/tasks")

    @task(1)
    def move_task(self):
        if self.task_ids:
            self.client.put(f"/api/tasks/{self.task_ids[-1]}", headers=self.headers,
                            name="PUT /api/tasks/{id}", json={"priority": "HIGH"})

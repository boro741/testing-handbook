"""Playwright UI tests for the TaskFlow demo UI (static/index.html).

Start the server first, for example:
  DATABASE_URL=sqlite:////tmp/taskflow-ui.db uvicorn app.main:app --port 8104
Then run:  pytest ui-tests --base-url http://localhost:8104
"""
import uuid

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def logged_in(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    page.get_by_test_id("login").click()
    expect(page.get_by_test_id("who")).to_have_text("Logged in")
    return page


def create_task(page: Page, title: str) -> None:
    page.get_by_test_id("task-title").fill(title)
    page.get_by_test_id("create-task").click()


def test_login_shows_logged_in(logged_in: Page):
    expect(logged_in.get_by_test_id("log")).to_contain_text('"status": 200')


def test_create_task_shows_201_in_log(logged_in: Page):
    title = f"ui-{uuid.uuid4().hex[:8]}"
    create_task(logged_in, title)
    log = logged_in.get_by_test_id("log")
    expect(log).to_contain_text('"status": 201')
    expect(log).to_contain_text(title)


@pytest.mark.parametrize("length", [1, 100])
def test_title_boundaries_accepted(logged_in: Page, length: int):
    create_task(logged_in, "a" * length)
    expect(logged_in.get_by_test_id("log")).to_contain_text('"status": 201')


def test_title_101_chars_shows_api_error(logged_in: Page):
    # The input has maxlength=100, so remove it to let the API see 101 characters.
    logged_in.get_by_test_id("task-title").evaluate("el => el.removeAttribute('maxlength')")
    create_task(logged_in, "a" * 101)
    log = logged_in.get_by_test_id("log")
    expect(log).to_contain_text('"status": 422')
    expect(log).to_contain_text("at most 100 characters")


def test_list_tasks_shows_created_task(logged_in: Page):
    title = f"list-{uuid.uuid4().hex[:8]}"
    create_task(logged_in, title)
    expect(logged_in.get_by_test_id("log")).to_contain_text('"status": 201')
    logged_in.get_by_test_id("list-tasks").click()
    expect(logged_in.get_by_test_id("task-item").filter(has_text=title)).to_have_count(1)

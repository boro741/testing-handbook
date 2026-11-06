"""Visual regression test for the TaskFlow UI.

Python Playwright has no expect(page).to_have_screenshot() (checked in 1.64.1),
so this file takes page.screenshot() and compares it with a baseline using Pillow.

Start the server first (see README in the handbook page), then run from examples/taskflow:
    BASE_URL=http://127.0.0.1:8102 pytest -q visual
First run: no baseline exists, so it is created. Second run: compares.
"""
import os
from pathlib import Path

import pytest
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8102")
HERE = Path(__file__).parent
BASELINES, OUTPUT = HERE / "baselines", HERE / "output"
MAX_DIFF_RATIO = 0.001   # up to 0.1% of pixels may differ
PIXEL_TOLERANCE = 16     # per-channel difference (0-255) that still counts as equal


def compare(name, png_path, baseline_name=None):
    """Return 'created' on first run, 'match' if equal enough. Fail with a diff image otherwise."""
    BASELINES.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)
    baseline = BASELINES / f"{baseline_name or name}.png"
    if not baseline.exists():
        baseline.write_bytes(Path(png_path).read_bytes())
        return "created"
    a, b = Image.open(baseline).convert("RGB"), Image.open(png_path).convert("RGB")
    assert a.size == b.size, f"{name}: size changed {a.size} -> {b.size}"
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > PIXEL_TOLERANCE else 0)
    changed = diff.histogram()[255]
    ratio = changed / (a.size[0] * a.size[1])
    if ratio > MAX_DIFF_RATIO:
        diff.save(OUTPUT / f"{name}-diff.png")
        pytest.fail(f"{name}: {changed} pixels differ ({ratio:.2%}), limit {MAX_DIFF_RATIO:.2%}")
    return "match"


@pytest.fixture()
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Fixed viewport and scale: the same pixel size on every machine.
        ctx = browser.new_context(viewport={"width": 800, "height": 700}, device_scale_factor=1)
        yield ctx.new_page()
        browser.close()


def shot(page, name, mask=()):
    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / f"{name}.png"
    page.screenshot(path=path, animations="disabled", caret="hide", mask=list(mask))
    return compare(name, path)


def test_login_screen(page):
    page.goto(BASE_URL)
    shot(page, "login-screen")


def test_after_login_masks_the_dynamic_log(page):
    page.goto(BASE_URL)
    page.get_by_test_id("login").click()
    page.get_by_test_id("who").wait_for()
    page.wait_for_function("document.getElementById('who').textContent === 'Logged in'")
    # The log box shows a random token, so cover it with a mask.
    shot(page, "after-login", mask=[page.get_by_test_id("log")])


def test_check_can_fail_when_the_ui_changes(page):
    if not (BASELINES / "login-screen.png").exists():
        pytest.skip("baseline not created yet (first run)")
    page.goto(BASE_URL)
    page.add_style_tag(content="h1 { color: red; font-size: 3rem; }")
    path = OUTPUT / "login-screen-changed.png"
    page.screenshot(path=path, animations="disabled")
    with pytest.raises(pytest.fail.Exception, match="pixels differ"):
        compare("login-screen-changed", path, baseline_name="login-screen")

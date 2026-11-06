"""Tests for capacity.tasks_needed and the CSV CLI. No AWS calls."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from capacity import tasks_needed, main  # noqa: E402


def test_worked_example_from_chapter_67():
    # 1,200 RPS peak, 150 RPS per task at the SLO, headroom 1.3 -> 10.4 -> 11
    assert tasks_needed(1200, 150, 1.3) == 11


def test_default_headroom_is_1_3():
    assert tasks_needed(1200, 150) == tasks_needed(1200, 150, 1.3)


def test_exact_division_with_no_headroom_gives_exact_count():
    assert tasks_needed(100, 50, 1.0) == 2


def test_partial_task_rounds_up():
    assert tasks_needed(101, 50, 1.0) == 3


def test_float_noise_does_not_add_a_task():
    # 1.1 / 0.1 is 11.000000000000002 in floating point; the answer must be 11.
    assert tasks_needed(1.1, 0.1, 1.0) == 11


def test_zero_peak_needs_zero_tasks():
    assert tasks_needed(0, 150) == 0


@pytest.mark.parametrize("per_task", [0, 0.0, -10, float("nan")])
def test_zero_or_invalid_per_task_rps_raises(per_task):
    with pytest.raises(ValueError, match="per_task_rps"):
        tasks_needed(100, per_task)


def test_negative_peak_raises():
    with pytest.raises(ValueError, match="peak_rps"):
        tasks_needed(-1, 10)


@pytest.mark.parametrize("headroom", [0.9, 0.0, -1.0])
def test_headroom_below_one_raises(headroom):
    with pytest.raises(ValueError, match="headroom"):
        tasks_needed(100, 10, headroom)


def test_cli_reads_csv_and_prints_counts(tmp_path, capsys):
    csv_file = tmp_path / "plan.csv"
    csv_file.write_text(
        "service,peak_rps,per_task_rps,headroom\n"
        "task-service,1200,150,\n"
        "notification-service,80,40,1.5\n",
        encoding="utf-8",
    )
    assert main([str(csv_file)]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "service,peak_rps,per_task_rps,headroom,tasks_needed"
    assert out[1] == "task-service,1200,150,1.3,11"
    assert out[2] == "notification-service,80,40,1.5,3"


def test_cli_reports_bad_row_and_returns_nonzero(tmp_path, capsys):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("service,peak_rps,per_task_rps\nsvc,100,0\n", encoding="utf-8")
    assert main([str(csv_file)]) == 1
    assert "per_task_rps" in capsys.readouterr().err

"""Seed test, so a shard repo's CI has something to run."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import add, multiply, validate_timeouts  # noqa: E402


def test_add() -> None:
    assert add(2, 3) == 5


def test_multiply() -> None:
    assert multiply(2, 3) == 6


def test_validate_timeouts_rejects_bad_combination() -> None:
    with pytest.raises(ValueError):
        validate_timeouts(
            triage_timeout_hours=168,
            escalation_timeout_hours=48,
            max_job_lifetime_hours=120,
        )


def test_validate_timeouts_accepts_good_combination() -> None:
    validate_timeouts(
        triage_timeout_hours=24,
        escalation_timeout_hours=12,
        max_job_lifetime_hours=120,
    )

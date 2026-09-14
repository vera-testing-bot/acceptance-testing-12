"""Seed test, so a shard repo's CI has something to run."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import add, validate_timeouts, truncate  # noqa: E402


def test_add() -> None:
    assert add(2, 3) == 5


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


def test_truncate_short_string_unchanged() -> None:
    assert truncate("hello", max_length=10) == "hello"


def test_truncate_long_string_with_ellipsis() -> None:
    text = "a" * 20
    assert truncate(text, max_length=10) == "aaaaaaa" + "..."


def test_truncate_exact_fit_no_ellipsis() -> None:
    assert truncate("exactly10", max_length=9) == "exactly10"


def test_truncate_empty_string() -> None:
    assert truncate("", max_length=5) == ""


def test_truncate_max_length_too_small_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        truncate("hello", max_length=2)

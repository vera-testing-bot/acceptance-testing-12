"""Tests for lifecycle timeout cross-validation.

The loader must reject a bad timeout combination: the sum of
``triage_timeout_hours`` and ``escalation_timeout_hours`` must be strictly
less than ``max_job_lifetime_hours``. Any other combination is accepted.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.lifecycle import (
    LifecycleTimeouts,
    cross_validate_timeouts,
    load_lifecycle_settings,
)


def test_valid_timeout_combination_accepted() -> None:
    timeouts = cross_validate_timeouts(
        {
            "triage_timeout_hours": 24,
            "escalation_timeout_hours": 48,
            "max_job_lifetime_hours": 120,
        }
    )
    assert timeouts.triage_timeout_hours == 24
    assert timeouts.escalation_timeout_hours == 48
    assert timeouts.max_job_lifetime_hours == 120


def test_defaults_form_a_valid_combination() -> None:
    timeouts = cross_validate_timeouts({})
    assert (
        timeouts.triage_timeout_hours + timeouts.escalation_timeout_hours
        < timeouts.max_job_lifetime_hours
    )


def test_bad_combination_sum_exceeds_lifetime_rejected() -> None:
    with pytest.raises(ValueError):
        cross_validate_timeouts(
            {
                "triage_timeout_hours": 168,
                "escalation_timeout_hours": 48,
                "max_job_lifetime_hours": 120,
            }
        )


def test_sum_equal_to_lifetime_rejected() -> None:
    with pytest.raises(ValueError):
        cross_validate_timeouts(
            {
                "triage_timeout_hours": 72,
                "escalation_timeout_hours": 48,
                "max_job_lifetime_hours": 120,
            }
        )


def test_just_under_lifetime_accepted() -> None:
    timeouts = cross_validate_timeouts(
        {
            "triage_timeout_hours": 71,
            "escalation_timeout_hours": 48,
            "max_job_lifetime_hours": 120,
        }
    )
    assert timeouts.triage_timeout_hours == 71


def test_non_integer_timeout_rejected() -> None:
    with pytest.raises(TypeError):
        cross_validate_timeouts({"triage_timeout_hours": "a week"})


def test_zero_triage_timeout_accepted() -> None:
    timeouts = cross_validate_timeouts(
        {
            "triage_timeout_hours": 0,
            "escalation_timeout_hours": 48,
            "max_job_lifetime_hours": 120,
        }
    )
    assert timeouts.triage_timeout_hours == 0


def test_load_lifecycle_settings_valid_file() -> None:
    path = Path(__file__).resolve().parent / "fixtures" / "lifecycle_valid.yaml"
    timeouts = load_lifecycle_settings(path)
    assert timeouts.triage_timeout_hours == 24
    assert timeouts.escalation_timeout_hours == 48
    assert timeouts.max_job_lifetime_hours == 120


def test_load_lifecycle_settings_rejects_bad_combination_file() -> None:
    path = (
        Path(__file__).resolve().parent / "fixtures" / "lifecycle_invalid_timeout.yaml"
    )
    with pytest.raises(ValueError):
        load_lifecycle_settings(path)


def test_load_lifecycle_settings_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_lifecycle_settings(Path("does-not-exist.yaml"))


def test_dataclass_is_frozen() -> None:
    timeouts = LifecycleTimeouts()
    with pytest.raises(AttributeError):
        timeouts.triage_timeout_hours = 999  # type: ignore[misc]

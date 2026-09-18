"""Tests for lifecycle settings validation — invalid values fail fast.

The settings loader must reject out-of-range or inconsistent values the
moment they are parsed rather than carrying them silently downstream.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.settings import load_settings, validate_settings


def test_valid_settings_returned() -> None:
    settings = validate_settings({"auto_manage_issues": False, "max_attempts": 3})
    assert settings.max_attempts == 3
    assert settings.auto_manage_issues is False


def test_defaults_applied_for_missing_keys() -> None:
    settings = validate_settings({})
    assert settings.max_attempts == 3
    assert settings.auto_manage_issues is False


def test_max_attempts_below_range_fails_fast() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": -1})


def test_max_attempts_above_range_fails_fast() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": 21})


def test_max_attempts_zero_fails_fast() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": 0})


def test_max_attempts_must_be_integer_fails_fast() -> None:
    with pytest.raises(TypeError):
        validate_settings({"max_attempts": "three"})


def test_escalation_after_must_be_strictly_less_than_max_attempts() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": 2, "escalation_after": 2})


def test_escalation_after_greater_than_max_attempts_fails_fast() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": 2, "escalation_after": 5})


def test_escalation_after_below_one_fails_fast() -> None:
    with pytest.raises(ValueError):
        validate_settings({"max_attempts": 3, "escalation_after": 0})


def test_auto_manage_issues_must_be_bool_fails_fast() -> None:
    with pytest.raises(TypeError):
        validate_settings({"auto_manage_issues": "yes"})


def test_load_settings_reads_yaml_file() -> None:
    path = Path(__file__).resolve().parent / "fixtures" / "valid_settings.yaml"
    settings = load_settings(path)
    assert settings.max_attempts == 5
    assert settings.auto_manage_issues is True


def test_load_settings_invalid_file_fails_fast() -> None:
    path = Path(__file__).resolve().parent / "fixtures" / "invalid_settings.yaml"
    with pytest.raises(ValueError):
        load_settings(path)


def test_load_settings_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_settings(Path("does-not-exist.yaml"))

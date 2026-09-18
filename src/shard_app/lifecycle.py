"""Lifecycle timeout cross-validation.

Settings are read from a ``.vera/settings.yaml``-style file and cross-validated
the instant they are parsed. The lifecycle contract requires that the sum of
``triage_timeout_hours`` and ``escalation_timeout_hours`` be strictly less than
``max_job_lifetime_hours``; a bad combination raises :class:`ValueError`
immediately instead of being carried silently downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_TRIAGE_TIMEOUT_HOURS = 24
DEFAULT_ESCALATION_TIMEOUT_HOURS = 48
DEFAULT_MAX_JOB_LIFETIME_HOURS = 120


@dataclass(frozen=True)
class LifecycleTimeouts:
    """Cross-validated lifecycle timeout settings."""

    triage_timeout_hours: int = DEFAULT_TRIAGE_TIMEOUT_HOURS
    escalation_timeout_hours: int = DEFAULT_ESCALATION_TIMEOUT_HOURS
    max_job_lifetime_hours: int = DEFAULT_MAX_JOB_LIFETIME_HOURS


def cross_validate_timeouts(raw: dict[str, Any]) -> LifecycleTimeouts:
    """Cross-validate a raw timeout mapping and return a :class:`LifecycleTimeouts`.

    Raises :class:`ValueError` when ``triage_timeout_hours`` plus
    ``escalation_timeout_hours`` is not strictly less than
    ``max_job_lifetime_hours``, so a bad combination fails fast instead of
    being carried silently downstream.
    """
    triage_timeout_hours = _coerce_int(
        raw.get("triage_timeout_hours", DEFAULT_TRIAGE_TIMEOUT_HOURS),
        "triage_timeout_hours",
    )
    escalation_timeout_hours = _coerce_int(
        raw.get("escalation_timeout_hours", DEFAULT_ESCALATION_TIMEOUT_HOURS),
        "escalation_timeout_hours",
    )
    max_job_lifetime_hours = _coerce_int(
        raw.get("max_job_lifetime_hours", DEFAULT_MAX_JOB_LIFETIME_HOURS),
        "max_job_lifetime_hours",
    )

    combined = triage_timeout_hours + escalation_timeout_hours
    if combined >= max_job_lifetime_hours:
        raise ValueError(
            f"triage_timeout_hours ({triage_timeout_hours}) + "
            f"escalation_timeout_hours ({escalation_timeout_hours}) "
            f"must be < max_job_lifetime_hours ({max_job_lifetime_hours})"
        )

    return LifecycleTimeouts(
        triage_timeout_hours=triage_timeout_hours,
        escalation_timeout_hours=escalation_timeout_hours,
        max_job_lifetime_hours=max_job_lifetime_hours,
    )


def load_lifecycle_settings(path: Path) -> LifecycleTimeouts:
    """Read and cross-validate lifecycle timeouts from a YAML file.

    Only the minimal subset of YAML used by the settings file is parsed
    (``key: value`` scalars and comments) so no third-party dependency is
    required. A bad timeout combination causes an immediate :class:`ValueError`.
    """
    if not path.exists():
        raise FileNotFoundError(f"settings file not found: {path}")
    raw = _parse_simple_yaml(path.read_text(encoding="utf-8"))
    return cross_validate_timeouts(raw)


def _coerce_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    return value


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        raw[key] = _parse_scalar(value)
    return raw


def _parse_scalar(value: str) -> Any:
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    try:
        return int(value)
    except ValueError:
        return value

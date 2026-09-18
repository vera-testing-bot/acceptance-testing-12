"""Lifecycle settings loader with fail-fast validation.

Settings are read from a ``.vera/settings.yaml``-style file and validated
the instant they are parsed. Out-of-range or inconsistent values raise
:class:`ValueError` immediately rather than being carried downstream where
they would surface as confusing behaviour partway through a run.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

MIN_MAX_ATTEMPTS = 1
MAX_MAX_ATTEMPTS = 20
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_AUTO_MANAGE_ISSUES = False
DEFAULT_ESCALATION_AFTER = 2


@dataclass(frozen=True)
class Settings:
    """Validated lifecycle settings."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    auto_manage_issues: bool = DEFAULT_AUTO_MANAGE_ISSUES
    escalation_after: int = DEFAULT_ESCALATION_AFTER


def validate_settings(raw: dict[str, Any]) -> Settings:
    """Validate a raw settings mapping and return a :class:`Settings`.

    Raises :class:`ValueError` for any out-of-range or inconsistent value
    so callers fail fast instead of persisting bad configuration.
    """
    max_attempts = _coerce_int(
        raw.get("max_attempts", DEFAULT_MAX_ATTEMPTS), "max_attempts"
    )
    if not MIN_MAX_ATTEMPTS <= max_attempts <= MAX_MAX_ATTEMPTS:
        raise ValueError(
            f"max_attempts={max_attempts} out of range "
            f"[{MIN_MAX_ATTEMPTS}, {MAX_MAX_ATTEMPTS}]"
        )

    escalation_after = _coerce_int(
        raw.get("escalation_after", DEFAULT_ESCALATION_AFTER), "escalation_after"
    )
    if escalation_after < MIN_MAX_ATTEMPTS:
        raise ValueError(
            f"escalation_after={escalation_after} must be >= {MIN_MAX_ATTEMPTS}"
        )
    if escalation_after >= max_attempts:
        raise ValueError(
            f"escalation_after ({escalation_after}) must be strictly "
            f"less than max_attempts ({max_attempts})"
        )

    auto_manage_issues = raw.get("auto_manage_issues", DEFAULT_AUTO_MANAGE_ISSUES)
    if not isinstance(auto_manage_issues, bool):
        raise TypeError(
            f"auto_manage_issues must be a boolean, got {auto_manage_issues!r}"
        )

    return Settings(
        max_attempts=max_attempts,
        auto_manage_issues=auto_manage_issues,
        escalation_after=escalation_after,
    )


def load_settings(path: Path) -> Settings:
    """Read and validate settings from a YAML file.

    Only the minimal subset of YAML used by the settings file is parsed
    (``key: value`` scalars and comments) so no third-party dependency is
    required. Invalid values cause an immediate :class:`ValueError`.
    """
    if not path.exists():
        raise FileNotFoundError(f"settings file not found: {path}")
    raw = _parse_simple_yaml(path.read_text(encoding="utf-8"))
    return validate_settings(raw)


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

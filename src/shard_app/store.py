"""Unified application state store.

This module is the single owner of calculator application state. Components
read and write state through typed accessors instead of holding their own
copies, module-level globals, or hand-rolled ``localStorage`` JSON.

The store is schema-versioned: persisted blobs carry a ``version`` integer and
a ``data`` payload. ``migrate`` walks legacy schema-less blobs (the shapes
already sitting in real users' browsers) forward to the current
``SCHEMA_VERSION``, so old data keeps working without a forced reset.

A bounded transition log records every write together with the component that
performed it, and ``debug_view`` exposes the current state plus that log — the
observability layer that lets someone tell where a given piece of state came
from.
"""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

SCHEMA_VERSION = 2

DEFAULTS: dict[str, Any] = {
    "display": "",
    "accumulator": 0.0,
    "history": [],
    "settings": {},
}

SCHEMA: dict[str, type] = {
    "display": str,
    "accumulator": float,
    "history": list,
    "settings": dict,
}

_MAX_TRANSITIONS = 100


class Backend(Protocol):
    """Persistence backend — the replacement for hand-rolled localStorage JSON."""

    def load(self) -> str | None: ...

    def save(self, blob: str) -> None: ...


class InMemoryBackend:
    """Process-local backend used by tests and the debug console."""

    def __init__(self) -> None:
        self._blob: str | None = None

    def load(self) -> str | None:
        return self._blob

    def save(self, blob: str) -> None:
        self._blob = blob


@dataclass(frozen=True)
class Transition:
    """A single recorded state write."""

    key: str
    old_value: Any
    new_value: Any
    writer: str


class UnknownKeyError(KeyError):
    """Raised when accessing a key that is not part of the schema."""


class WrongTypeError(TypeError):
    """Raised when a value does not match the key's declared type."""


def _coerce(key: str, value: Any) -> Any:
    expected = SCHEMA[key]
    if expected is float and isinstance(value, bool):
        # bool is a subclass of int; reject it explicitly so a flag never
        # silently becomes 0.0/1.0 in the accumulator.
        raise WrongTypeError(key, expected, type(value))
    if expected is float and isinstance(value, int):
        return float(value)
    if not isinstance(value, expected):
        raise WrongTypeError(key, expected, type(value))
    return value


def migrate(blob: Mapping[str, Any]) -> dict[str, Any]:
    """Walk a persisted blob forward to ``SCHEMA_VERSION``.

    Accepts three legacy shapes found in real browsers:

    * **v0** — a raw schema-less dict with bare state keys (no ``version``),
      e.g. ``{"display": "9", "acc": 9.0, "history": ["9"]}``.
    * **v1** — a versioned dict whose ``data`` used the old ``acc`` key instead
      of ``accumulator``.
    * **current** — already at ``SCHEMA_VERSION``; returned unchanged.
    """
    if "version" not in blob:
        raw = dict(blob)
        data = {key: raw.pop(key) for key in list(raw) if key in DEFAULTS}
        # Any stray keys are dropped: they were never part of the schema.
        data.setdefault("display", DEFAULTS["display"])
        data.setdefault("history", DEFAULTS["history"])
        data["accumulator"] = float(
            raw.pop("acc", data.get("accumulator", DEFAULTS["accumulator"]))
        )
        data.setdefault("settings", DEFAULTS["settings"])
        return {"version": SCHEMA_VERSION, "data": _normalize(data)}

    version = blob["version"]
    data = dict(blob.get("data", {}))
    if version < 2:
        # v1 -> v2: rename the legacy ``acc`` key to ``accumulator`` and
        # guarantee a ``settings`` slot exists.
        if "acc" in data:
            data["accumulator"] = float(data.pop("acc"))
        data.setdefault("settings", DEFAULTS["settings"])
    data.setdefault("display", DEFAULTS["display"])
    data.setdefault("accumulator", DEFAULTS["accumulator"])
    data.setdefault("history", DEFAULTS["history"])
    return {"version": SCHEMA_VERSION, "data": _normalize(data)}


def _normalize(data: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(DEFAULTS)
    for key, value in data.items():
        if key in SCHEMA:
            out[key] = _coerce(key, value)
    return out


@dataclass
class Store:
    """The single owner of application state."""

    backend: Backend
    max_transitions: int = _MAX_TRANSITIONS
    _state: dict[str, Any] = field(default_factory=lambda: dict(DEFAULTS))
    _log: deque[Transition] = field(default_factory=deque)

    def get(self, key: str) -> Any:
        if key not in SCHEMA:
            raise UnknownKeyError(key)
        return self._state[key]

    def set(self, key: str, value: Any, *, writer: str) -> None:
        if key not in SCHEMA:
            raise UnknownKeyError(key)
        coerced = _coerce(key, value)
        old = self._state[key]
        self._state[key] = coerced
        self._log.append(
            Transition(key=key, old_value=old, new_value=coerced, writer=writer)
        )
        if len(self._log) > self.max_transitions:
            self._log.popleft()

    def transitions(self) -> list[Transition]:
        return list(self._log)

    def load(self) -> None:
        blob = self.backend.load()
        if blob is None:
            self._state = dict(DEFAULTS)
            return
        migrated = migrate(json.loads(blob))
        self._state = migrated["data"]

    def persist(self) -> None:
        self.backend.save(json.dumps({"version": SCHEMA_VERSION, "data": self._state}))

    def debug_view(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "state": dict(self._state),
            "transitions": [
                {
                    "key": t.key,
                    "old_value": t.old_value,
                    "new_value": t.new_value,
                    "writer": t.writer,
                }
                for t in self._log
            ],
        }

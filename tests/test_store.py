"""Characterization and behavior tests for the unified state store.

These tests double as the characterization suite for the legacy schema-less
persistence shapes that already sit in real users' browsers: they pin the
migration path from a raw v0 blob through v1 to the current schema version.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.store import (
    SCHEMA_VERSION,
    InMemoryBackend,
    Store,
    UnknownKeyError,
    WrongTypeError,
    migrate,
)


def test_load_returns_defaults_when_backend_empty() -> None:
    store = Store(InMemoryBackend())
    assert store.get("display") == ""
    assert store.get("accumulator") == 0.0
    assert store.get("history") == []
    assert store.get("settings") == {}


def test_set_then_get_round_trips_value() -> None:
    store = Store(InMemoryBackend())
    store.set("display", "42", writer="calculator")
    assert store.get("display") == "42"


def test_set_rejects_unknown_key() -> None:
    store = Store(InMemoryBackend())
    with pytest.raises(UnknownKeyError):
        store.set("nope", 1, writer="calc")


def test_set_rejects_wrong_type() -> None:
    store = Store(InMemoryBackend())
    with pytest.raises(WrongTypeError):
        store.set("accumulator", "not a float", writer="calc")


def test_set_coerces_int_to_float_for_float_field() -> None:
    store = Store(InMemoryBackend())
    store.set("accumulator", 7, writer="calc")
    assert store.get("accumulator") == 7.0
    assert isinstance(store.get("accumulator"), float)


@pytest.mark.parametrize("flag", [True, False])
def test_set_rejects_bool_for_float_field(flag: bool) -> None:
    store = Store(InMemoryBackend())
    with pytest.raises(WrongTypeError):
        store.set("accumulator", flag, writer="calc")


def test_persist_then_reload_preserves_state() -> None:
    backend = InMemoryBackend()
    store = Store(backend)
    store.set("display", "1+1", writer="calculator")
    store.set("accumulator", 2.0, writer="calculator")
    store.set("history", ["1+1=2"], writer="history-panel")
    store.persist()

    reloaded = Store(backend)
    reloaded.load()
    assert reloaded.get("display") == "1+1"
    assert reloaded.get("accumulator") == 2.0
    assert reloaded.get("history") == ["1+1=2"]


def test_persist_writes_current_schema_version() -> None:
    import json

    backend = InMemoryBackend()
    store = Store(backend)
    store.persist()
    blob = json.loads(backend.load() or "{}")
    assert blob["version"] == SCHEMA_VERSION


def test_migrate_legacy_schemaless_blob_v0() -> None:
    legacy = {"display": "9", "acc": 9.0, "history": ["9"]}
    migrated = migrate(legacy)
    assert migrated["version"] == SCHEMA_VERSION
    assert migrated["data"]["display"] == "9"
    assert migrated["data"]["accumulator"] == 9.0
    assert migrated["data"]["history"] == ["9"]


def test_load_migrates_legacy_blob_with_unversioned_keys() -> None:
    import json

    backend = InMemoryBackend()
    backend.save(json.dumps({"display": "3", "acc": 3.0, "history": []}))
    store = Store(backend)
    store.load()
    assert store.get("accumulator") == 3.0
    assert store.get("display") == "3"


def test_load_migrates_v1_blob_renaming_acc_to_accumulator() -> None:
    import json

    backend = InMemoryBackend()
    v1_blob = {
        "version": 1,
        "data": {"display": "5", "acc": 5.0, "history": [], "settings": {}},
    }
    backend.save(json.dumps(v1_blob))
    store = Store(backend)
    store.load()
    assert store.get("accumulator") == 5.0
    assert store.get("display") == "5"


def test_load_with_already_current_schema_is_unchanged() -> None:

    backend = InMemoryBackend()
    store = Store(backend)
    store.set("display", "8", writer="calc")
    store.persist()
    fresh = Store(backend)
    fresh.load()
    assert fresh.get("display") == "8"


def test_transition_log_records_writes_and_writers() -> None:
    store = Store(InMemoryBackend())
    store.set("display", "1", writer="calculator")
    store.set("display", "2", writer="history-panel")
    transitions = store.transitions()
    assert len(transitions) == 2
    assert transitions[0].writer == "calculator"
    assert transitions[0].new_value == "1"
    assert transitions[1].writer == "history-panel"
    assert transitions[1].old_value == "1"


def test_debug_view_shows_state_transitions_and_writers() -> None:
    store = Store(InMemoryBackend())
    store.set("display", "7", writer="calculator")
    store.set("accumulator", 7.0, writer="calculator")
    view = store.debug_view()
    assert view["schema_version"] == SCHEMA_VERSION
    assert view["state"]["display"] == "7"
    assert view["state"]["accumulator"] == 7.0
    assert len(view["transitions"]) == 2
    assert view["transitions"][0]["writer"] == "calculator"
    assert view["transitions"][0]["key"] == "display"


def test_transition_log_caps_recent_history() -> None:
    store = Store(InMemoryBackend(), max_transitions=3)
    for i in range(5):
        store.set("display", str(i), writer="calc")
    assert len(store.transitions()) == 3
    assert store.transitions()[-1].new_value == "4"


def test_history_is_a_view_over_store_not_separate_storage() -> None:
    store = Store(InMemoryBackend())
    store.set("history", ["1+1=2", "2+2=4"], writer="history-panel")
    assert store.get("history") == ["1+1=2", "2+2=4"]
    store.set("history", store.get("history") + ["3+3=6"], writer="history-panel")
    assert store.get("history")[-1] == "3+3=6"


def test_migrate_idempotent_on_current_blob() -> None:
    current = {
        "version": SCHEMA_VERSION,
        "data": {"display": "x", "accumulator": 1.0, "history": [], "settings": {}},
    }
    assert migrate(current) == current

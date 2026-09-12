"""Seed test, so a shard repo's CI has something to run."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import add, truncate


def test_add() -> None:
    assert add(2, 3) == 5


def test_truncate_short_string_unchanged() -> None:
    assert truncate("hello", 10) == "hello"


def test_truncate_exact_length_unchanged() -> None:
    assert truncate("hello", 5) == "hello"


def test_truncate_long_string_without_suffix() -> None:
    assert truncate("hello world", 5) == "hello"


def test_truncate_long_string_with_suffix() -> None:
    result = truncate("hello world", 8, suffix="…")
    assert result == "hello w…"
    assert len(result) == 8


def test_truncate_suffix_exceeds_max_length() -> None:
    result = truncate("hello world", 3, suffix="…")
    assert result == "he…"
    assert len(result) == 3

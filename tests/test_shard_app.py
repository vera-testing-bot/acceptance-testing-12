"""Seed test, so a shard repo's CI has something to run."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import add, multiply, truncate


def test_add() -> None:
    assert add(2, 3) == 5


def test_multiply() -> None:
    assert multiply(2, 3) == 6


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

"""Tests for the string truncation helper."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import truncate


def test_truncate_short_string_unchanged() -> None:
    assert truncate("abc", 10) == "abc"


def test_truncate_exact_length_unchanged() -> None:
    assert truncate("abcdef", 6) == "abcdef"


def test_truncate_long_string_with_default_ellipsis() -> None:
    assert truncate("abcdef", 5) == "ab..."


def test_truncate_long_string_custom_ellipsis() -> None:
    assert truncate("abcdef", 4, "…") == "abc…"


def test_truncate_zero_max_length() -> None:
    assert truncate("abc", 0) == ""

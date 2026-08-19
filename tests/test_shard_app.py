"""Seed test, so a shard repo's CI has something to run."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app import add, validate_bounds


def test_add() -> None:
    assert add(2, 3) == 5


def test_validate_bounds_accepts_in_range() -> None:
    assert validate_bounds(10, 1, 20) == 10
    assert validate_bounds(1, 1, 20) == 1
    assert validate_bounds(20, 1, 20) == 20


def test_validate_bounds_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        validate_bounds(99, 1, 20)
    with pytest.raises(ValueError):
        validate_bounds(0, 1, 20)

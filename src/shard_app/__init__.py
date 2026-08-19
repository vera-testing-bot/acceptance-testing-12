"""Trivial module so an acceptance shard repo has code to change."""


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def validate_bounds(value: int, low: int, high: int) -> int:
    """Return ``value`` when it lies within the inclusive ``[low, high]`` range.

    Raise ``ValueError`` for out-of-range values so callers can reject them
    at the boundary instead of letting an invalid value propagate.
    """
    if not low <= value <= high:
        raise ValueError(f"value {value} is out of range [{low}, {high}]")
    return value

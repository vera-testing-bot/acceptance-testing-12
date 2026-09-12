"""Trivial module so an acceptance shard repo has code to change."""


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def subtract(left: int, right: int) -> int:
    """Return the difference of two integers."""
    return left - right


def truncate(value: str, max_length: int, suffix: str = "") -> str:
    """Return ``value`` truncated to at most ``max_length`` characters.

    If ``value`` exceeds ``max_length``, it is shortened so that the
    returned string (including ``suffix``) is never longer than
    ``max_length``. Strings at or below ``max_length`` are returned
    unchanged.
    """
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(value) <= max_length:
        return value
    if len(suffix) >= max_length:
        return suffix[:max_length]
    cut = max_length - len(suffix)
    return value[:cut] + suffix

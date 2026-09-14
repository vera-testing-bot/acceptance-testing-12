"""Trivial module so an acceptance shard repo has code to change."""


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def multiply(left: int, right: int) -> int:
    """Return the product of two integers."""
    return left * right


def truncate(text: str, max_length: int) -> str:
    """Return ``text`` trimmed to ``max_length`` characters.

    If ``text`` is longer than ``max_length`` it is cut to
    ``max_length - 3`` characters and an ``"..."`` ellipsis is appended so
    that the returned string is exactly ``max_length`` characters long.
    Strings that already fit are returned unchanged.

    Raises:
        ValueError: if ``max_length`` is smaller than 3, since the ellipsis
            would leave no room for any original content.
    """
    if max_length < 3:
        raise ValueError("max_length must be at least 3 to fit an ellipsis")
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."

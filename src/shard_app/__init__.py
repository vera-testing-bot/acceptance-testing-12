"""Trivial module so an acceptance shard repo has code to change."""


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def truncate(text: str, max_length: int, ellipsis: str = "...") -> str:
    """Return ``text`` truncated to ``max_length`` characters.

    If ``text`` fits within ``max_length`` it is returned unchanged.
    Otherwise the result is the first ``max_length - len(ellipsis)``
    characters of ``text`` followed by ``ellipsis``. When ``ellipsis``
    is longer than ``max_length`` only the ellipsis (truncated to
    ``max_length``) is returned.
    """
    if max_length <= 0:
        return ""
    if len(text) <= max_length:
        return text
    keep = max(0, max_length - len(ellipsis))
    return text[:keep] + ellipsis[: max_length - keep]

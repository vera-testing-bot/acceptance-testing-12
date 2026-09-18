"""Formatting helper for the calculator display.

Every value shown on the display is routed through :func:`format_value` so
formatting lives in exactly one place. Integers and floats are rendered
with thousands separators; values that cannot be parsed as numbers are
reported as ``Error`` rather than emitted raw.
"""

from __future__ import annotations

import math

Number = int | float
FormattedValue = str | Number

ERROR_TOKEN = "Error"
FALLBACK_VALUE = "0"


def format_value(value: FormattedValue) -> str:
    """Format a value for display.

    - Blank values fall back to ``0``.
    - Numbers get thousands separators on the integer part.
    - Anything that cannot be parsed as a number becomes ``Error``.
    """
    text = _coerce_to_text(value)
    if text == "":
        return FALLBACK_VALUE
    try:
        number = _parse_number(text)
    except (TypeError, ValueError):
        return ERROR_TOKEN
    return _format_number(number)


def _parse_number(text: str) -> Number:
    """Parse ``text`` into a number, preserving integer precision.

    Integer strings are parsed with :func:`int` (arbitrary precision) so the
    calculator never rounds a long digit string the user typed. Strings with
    a decimal point or exponent fall back to :func:`float`. Non-finite
    floats (``nan``/``inf``) are rejected so they display as ``Error``.
    """
    if any(ch in text for ch in (".", "e", "E")):
        number = float(text)
    else:
        try:
            number = int(text)
        except ValueError:
            number = float(text)
    if isinstance(number, float) and not math.isfinite(number):
        raise ValueError(f"non-finite value: {text!r}")
    return number


def _coerce_to_text(value: FormattedValue) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return ERROR_TOKEN
    return str(value)


def _format_number(number: Number) -> str:
    # Preserve a clean integer rendering when there is no fractional part,
    # otherwise keep the fractional digits the caller supplied. Integers are
    # formatted directly so arbitrarily large values keep their exact digits.
    if isinstance(number, int):
        return f"{number:,}"
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,}"

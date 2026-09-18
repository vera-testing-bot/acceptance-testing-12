"""Formatting helper for the calculator display.

Every value shown on the display is routed through :func:`format_value` so
formatting lives in exactly one place. Integers and floats are rendered
with thousands separators; values that cannot be parsed as numbers are
reported as ``Error`` rather than emitted raw.
"""

from __future__ import annotations

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
        number = float(text)
    except (TypeError, ValueError):
        return ERROR_TOKEN
    return _format_number(number)


def _coerce_to_text(value: FormattedValue) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return ERROR_TOKEN
    return str(value)


def _format_number(number: float) -> str:
    # Preserve a clean integer rendering when there is no fractional part,
    # otherwise keep the fractional digits the caller supplied.
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,}"

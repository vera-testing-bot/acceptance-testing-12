"""Standalone display component for the calculator.

The display markup lives in its own module so the calculator template
composes this component rather than inlining the markup. Keeping the
display isolated is the first step of the display-layer rework: later
phases hang formatting and accessibility off this single component.
"""

from __future__ import annotations

from shard_app.formatting import format_value

DISPLAY_CLASS = "calculator-display"
DISPLAY_ID = "display"
FALLBACK_VALUE = "0"


def render_display(value: str = FALLBACK_VALUE) -> str:
    """Render the display markup for a calculator value.

    Every value is routed through :func:`format_value` so formatting lives
    in a single helper; a blank value falls back to ``0``. The display
    carries an ``aria-live`` region so screen readers announce updates;
    the attribute is non-visual, so rendering is unchanged.
    """
    text = format_value(value)
    return (
        f'<div class="{DISPLAY_CLASS}" id="{DISPLAY_ID}"'
        f' role="status" aria-live="polite">{text}</div>'
    )

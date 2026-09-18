"""Standalone display component for the calculator.

The display markup lives in its own module so the calculator template
composes this component rather than inlining the markup. Keeping the
display isolated is the first step of the display-layer rework: later
phases hang formatting and accessibility off this single component.
"""

from __future__ import annotations

DISPLAY_CLASS = "calculator-display"
DISPLAY_ID = "display"
FALLBACK_VALUE = "0"


def render_display(value: str = FALLBACK_VALUE) -> str:
    """Render the display markup for a calculator value.

    A blank value falls back to ``0`` so the display never renders empty.
    """
    text = value if value else FALLBACK_VALUE
    return f'<div class="{DISPLAY_CLASS}" id="{DISPLAY_ID}" role="status">{text}</div>'

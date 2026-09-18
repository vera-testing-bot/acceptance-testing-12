"""Calculator that renders its UI by composing components.

The calculator owns a display value and renders its template by composing
the standalone :mod:`shard_app.display` component instead of inlining the
display markup. That keeps the display layer in one place so formatting
and accessibility changes land in a single component.
"""

from __future__ import annotations

from shard_app.display import render_display

CALCULATOR_CLASS = "calculator"


class Calculator:
    """A simple calculator with a display layer.

    The calculator holds a display value and renders its template by
    composing the standalone display component rather than inlining the
    display markup.
    """

    def __init__(self) -> None:
        self._display = "0"

    @property
    def display_value(self) -> str:
        """The raw value currently shown on the display."""
        return self._display

    def input_digit(self, digit: str) -> None:
        """Append a digit to the display, replacing a leading zero."""
        if not digit.isdigit():
            raise ValueError(f"expected a single digit, got {digit!r}")
        if self._display == "0":
            self._display = digit
        else:
            self._display += digit

    def clear(self) -> None:
        """Reset the display to its default value."""
        self._display = "0"

    def render(self) -> str:
        """Render the calculator template, composing the display component."""
        return f'<div class="{CALCULATOR_CLASS}">{render_display(self._display)}</div>'

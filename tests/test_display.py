"""Tests for the standalone display component."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.display import render_display


def test_render_display_default_value() -> None:
    html = render_display()
    assert "0" in html
    assert "calculator-display" in html


def test_render_display_shows_given_value() -> None:
    html = render_display("42")
    assert "42" in html


def test_render_display_blank_falls_back_to_zero() -> None:
    assert "0" in render_display("")


def test_render_display_routes_values_through_formatting_helper() -> None:
    # A value with thousands separators proves the display uses format_value
    # rather than emitting the raw input.
    assert "1,234,567" in render_display("1234567")


def test_render_display_invalid_input_shows_error() -> None:
    assert "Error" in render_display("not-a-number")


def test_render_display_announces_updates_to_screen_readers() -> None:
    # The display must carry an aria-live region so screen readers announce
    # value changes; role=status is the complementary landmark.
    html = render_display("123")
    assert 'aria-live="polite"' in html
    assert 'role="status"' in html


def test_render_display_accessibility_adds_no_visual_markup() -> None:
    # Accessibility attributes must not change the visible structure: the
    # display is still a single element wrapping the formatted value.
    html = render_display("42")
    assert html.count("<div") == 1
    assert html.count("</div>") == 1
    assert ">42</div>" in html

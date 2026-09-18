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

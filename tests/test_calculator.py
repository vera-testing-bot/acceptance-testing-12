"""Tests for the calculator and its display layer composition."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.calculator import Calculator


def test_calculator_default_display_is_zero() -> None:
    calc = Calculator()
    assert calc.display_value == "0"


def test_calculator_input_digit_appends() -> None:
    calc = Calculator()
    calc.input_digit("1")
    calc.input_digit("2")
    assert calc.display_value == "12"


def test_calculator_input_digit_replaces_leading_zero() -> None:
    calc = Calculator()
    calc.input_digit("5")
    assert calc.display_value == "5"


def test_calculator_clear_resets_display() -> None:
    calc = Calculator()
    calc.input_digit("9")
    calc.clear()
    assert calc.display_value == "0"


def test_calculator_render_includes_display_component() -> None:
    calc = Calculator()
    calc.input_digit("7")
    html = calc.render()
    assert "calculator" in html
    assert "calculator-display" in html
    assert "7" in html


def test_calculator_input_digit_rejects_non_digit() -> None:
    calc = Calculator()
    with pytest.raises(ValueError):
        calc.input_digit("a")

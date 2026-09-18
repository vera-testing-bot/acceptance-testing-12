"""Unit tests for the display formatting helper."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shard_app.formatting import format_value


def test_format_value_blank_falls_back_to_zero() -> None:
    assert format_value("") == "0"


def test_format_value_integer_adds_thousands_separators() -> None:
    assert format_value("1234567") == "1,234,567"


def test_format_value_small_integer_unchanged() -> None:
    assert format_value("42") == "42"


def test_format_value_decimal_preserves_fractional_part() -> None:
    assert format_value("1234.5") == "1,234.5"


def test_format_value_accepts_numeric_types() -> None:
    assert format_value(1000000) == "1,000,000"
    assert format_value(1234.5) == "1,234.5"


def test_format_value_invalid_input_reports_error() -> None:
    assert format_value("not-a-number") == "Error"


def test_format_value_leading_zero_decimal_preserved() -> None:
    assert format_value("0.5") == "0.5"


def test_format_value_large_integer_preserves_precision() -> None:
    assert format_value("99999999999999999999") == "99,999,999,999,999,999,999"


def test_format_value_nan_reports_error() -> None:
    assert format_value("nan") == "Error"


def test_format_value_inf_reports_error() -> None:
    assert format_value("inf") == "Error"
    assert format_value("-inf") == "Error"

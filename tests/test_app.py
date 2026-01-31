"""Tests for the Streamlit application."""

import pytest

from src.app import calculate_sum, get_greeting


class TestGreeting:
    """Tests for greeting functionality."""

    def test_get_greeting_basic(self) -> None:
        """Test basic greeting."""
        result = get_greeting("Alice")
        assert result == "Hello, Alice!"

    def test_get_greeting_empty(self) -> None:
        """Test greeting with empty string."""
        result = get_greeting("")
        assert result == "Hello, !"

    def test_get_greeting_special_chars(self) -> None:
        """Test greeting with special characters."""
        result = get_greeting("Jean-François")
        assert result == "Hello, Jean-François!"


class TestCalculator:
    """Tests for calculator functionality."""

    def test_calculate_sum_positive(self) -> None:
        """Test sum of positive numbers."""
        result = calculate_sum(2.0, 3.0)
        assert result == 5.0

    def test_calculate_sum_negative(self) -> None:
        """Test sum with negative numbers."""
        result = calculate_sum(-5.0, 3.0)
        assert result == -2.0

    def test_calculate_sum_zero(self) -> None:
        """Test sum with zero."""
        result = calculate_sum(0.0, 0.0)
        assert result == 0.0

    def test_calculate_sum_floats(self) -> None:
        """Test sum with decimal numbers."""
        result = calculate_sum(1.5, 2.5)
        assert result == 4.0

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (10, 5, 15),
            (-10, -5, -15),
            (100, -50, 50),
            (0.1, 0.2, pytest.approx(0.3)),
        ],
    )
    def test_calculate_sum_parametrized(self, a: float, b: float, expected: float) -> None:
        """Test sum with various parameters."""
        result = calculate_sum(a, b)
        assert result == expected

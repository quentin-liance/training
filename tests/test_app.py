"""Tests for the Streamlit application."""

# Import testing framework
import pytest

# Import functions to test from the main app module
from src.app import calculate_sum, get_greeting

# ========================================
# Greeting Function Tests
# ========================================


class TestGreeting:
    """Tests for greeting functionality."""

    def test_get_greeting_basic(self) -> None:
        """Test basic greeting."""
        # Test greeting with a simple name
        result = get_greeting("Alice")
        assert result == "Hello, Alice!"

    def test_get_greeting_empty(self) -> None:
        """Test greeting with empty string."""
        # Edge case: verify behavior with empty name
        result = get_greeting("")
        assert result == "Hello, !"

    def test_get_greeting_special_chars(self) -> None:
        """Test greeting with special characters."""
        # Test handling of special characters (accents, hyphens)
        result = get_greeting("Jean-François")
        assert result == "Hello, Jean-François!"


# ========================================
# Calculator Function Tests
# ========================================


class TestCalculator:
    """Tests for calculator functionality."""

    def test_calculate_sum_positive(self) -> None:
        """Test sum of positive numbers."""
        # Basic test case: adding two positive numbers
        result = calculate_sum(2.0, 3.0)
        assert result == 5.0

    def test_calculate_sum_negative(self) -> None:
        """Test sum with negative numbers."""
        # Test with one negative and one positive number
        result = calculate_sum(-5.0, 3.0)
        assert result == -2.0

    def test_calculate_sum_zero(self) -> None:
        """Test sum with zero."""
        # Edge case: verify that 0 + 0 = 0
        result = calculate_sum(0.0, 0.0)
        assert result == 0.0

    def test_calculate_sum_floats(self) -> None:
        """Test sum with decimal numbers."""
        # Test with decimal/floating-point numbers
        result = calculate_sum(1.5, 2.5)
        assert result == 4.0

    # Parametrized test: run the same test with multiple input combinations
    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (10, 5, 15),  # Positive integers
            (-10, -5, -15),  # Negative integers
            (100, -50, 50),  # Mixed signs
            (0.1, 0.2, pytest.approx(0.3)),  # Floating-point precision test
        ],
    )
    def test_calculate_sum_parametrized(self, a: float, b: float, expected: float) -> None:
        """Test sum with various parameters."""
        # Execute the function and verify the result matches expected value
        result = calculate_sum(a, b)
        assert result == expected

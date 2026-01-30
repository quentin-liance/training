"""Tests for the main module."""

import pytest

from src import add, main


def test_main() -> None:
    """Test main function runs without errors."""
    main()


def test_add() -> None:
    """Test add function with positive numbers."""
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0


def test_add_negative() -> None:
    """Test add function with negative numbers."""
    assert add(-2, -3) == -5
    assert add(-10, 5) == -5


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, 2),
        (10, 20, 30),
        (100, 200, 300),
        (-5, 5, 0),
    ],
)
def test_add_parametrized(a: int, b: int, expected: int) -> None:
    """Test add function with multiple test cases."""
    assert add(a, b) == expected

"""Tests for database functionality."""

import sqlite3
from pathlib import Path

import pytest

from src.database import (
    get_calculations,
    get_greetings,
    init_db,
    save_calculation,
    save_greeting,
)

# ========================================
# Fixtures
# ========================================


@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    """Create a temporary database for testing.

    Args:
        tmp_path: Pytest fixture providing temporary directory

    Returns:
        Path to the test database file
    """
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


# ========================================
# Database Initialization Tests
# ========================================


class TestDatabaseInit:
    """Tests for database initialization."""

    def test_init_db_creates_file(self, tmp_path: Path) -> None:
        """Test that init_db creates the database file."""
        db_path = tmp_path / "test.db"
        # Database file should not exist yet
        assert not db_path.exists()

        # Initialize database
        init_db(db_path)

        # Database file should now exist
        assert db_path.exists()

    def test_init_db_creates_tables(self, test_db: Path) -> None:
        """Test that init_db creates required tables."""
        # Connect to the database
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Check that calculations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calculations'")
        assert cursor.fetchone() is not None

        # Check that greetings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='greetings'")
        assert cursor.fetchone() is not None

        conn.close()


# ========================================
# Calculation Storage Tests
# ========================================


class TestCalculations:
    """Tests for calculation storage and retrieval."""

    def test_save_calculation(self, test_db: Path) -> None:
        """Test saving a calculation to the database."""
        # Save a calculation
        record_id = save_calculation(5.0, 3.0, 8.0, test_db)

        # Record ID should be positive
        assert record_id > 0

    def test_save_calculation_stores_correct_data(self, test_db: Path) -> None:
        """Test that saved calculation contains correct data."""
        # Save a calculation
        save_calculation(10.5, 20.3, 30.8, test_db)

        # Retrieve calculations
        calculations = get_calculations(limit=1, db_path=test_db)

        # Should have one calculation
        assert len(calculations) == 1

        # Check the data
        calc = calculations[0]
        assert calc["operand1"] == 10.5
        assert calc["operand2"] == 20.3
        assert calc["result"] == 30.8
        assert "timestamp" in calc

    def test_get_calculations_empty_database(self, test_db: Path) -> None:
        """Test retrieving calculations from empty database."""
        # Get calculations from empty database
        calculations = get_calculations(db_path=test_db)

        # Should return empty list
        assert calculations == []

    def test_get_calculations_limit(self, test_db: Path) -> None:
        """Test that limit parameter works correctly."""
        # Save multiple calculations
        for i in range(5):
            save_calculation(float(i), float(i + 1), float(i * 2), test_db)

        # Get with limit of 3
        calculations = get_calculations(limit=3, db_path=test_db)

        # Should return exactly 3 calculations
        assert len(calculations) == 3

    def test_get_calculations_order(self, test_db: Path) -> None:
        """Test that calculations are returned in descending order."""
        # Save calculations with small delay to ensure different timestamps
        save_calculation(1.0, 1.0, 2.0, test_db)
        save_calculation(2.0, 2.0, 4.0, test_db)
        save_calculation(3.0, 3.0, 6.0, test_db)

        # Get all calculations
        calculations = get_calculations(limit=10, db_path=test_db)

        # Most recent should be first (3.0 + 3.0 = 6.0)
        assert calculations[0]["result"] == 6.0
        assert calculations[1]["result"] == 4.0
        assert calculations[2]["result"] == 2.0


# ========================================
# Greeting Storage Tests
# ========================================


class TestGreetings:
    """Tests for greeting storage and retrieval."""

    def test_save_greeting(self, test_db: Path) -> None:
        """Test saving a greeting to the database."""
        # Save a greeting
        record_id = save_greeting("Alice", test_db)

        # Record ID should be positive
        assert record_id > 0

    def test_save_greeting_stores_correct_data(self, test_db: Path) -> None:
        """Test that saved greeting contains correct data."""
        # Save a greeting
        save_greeting("Bob", test_db)

        # Retrieve greetings
        greetings = get_greetings(limit=1, db_path=test_db)

        # Should have one greeting
        assert len(greetings) == 1

        # Check the data
        greeting = greetings[0]
        assert greeting["name"] == "Bob"
        assert "timestamp" in greeting

    def test_get_greetings_empty_database(self, test_db: Path) -> None:
        """Test retrieving greetings from empty database."""
        # Get greetings from empty database
        greetings = get_greetings(db_path=test_db)

        # Should return empty list
        assert greetings == []

    def test_get_greetings_limit(self, test_db: Path) -> None:
        """Test that limit parameter works correctly."""
        # Save multiple greetings
        names = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for name in names:
            save_greeting(name, test_db)

        # Get with limit of 3
        greetings = get_greetings(limit=3, db_path=test_db)

        # Should return exactly 3 greetings
        assert len(greetings) == 3

    def test_get_greetings_order(self, test_db: Path) -> None:
        """Test that greetings are returned in descending order."""
        # Save greetings
        save_greeting("First", test_db)
        save_greeting("Second", test_db)
        save_greeting("Third", test_db)

        # Get all greetings
        greetings = get_greetings(limit=10, db_path=test_db)

        # Most recent should be first
        assert greetings[0]["name"] == "Third"
        assert greetings[1]["name"] == "Second"
        assert greetings[2]["name"] == "First"

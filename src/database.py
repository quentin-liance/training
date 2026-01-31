"""Database module for storing calculation results."""

import sqlite3
from datetime import datetime
from pathlib import Path

# ========================================
# Database Configuration
# ========================================

# Default database path in the data directory
DB_PATH = Path("data/calculations.db")


# ========================================
# Database Initialization
# ========================================


def init_db(db_path: Path | None = None) -> None:
    """Initialize the database and create tables if they don't exist.

    Args:
        db_path: Path to the database file. Uses default if None.
    """
    if db_path is None:
        db_path = DB_PATH

    # Ensure the data directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to the database (creates file if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create calculations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operand1 REAL NOT NULL,
            operand2 REAL NOT NULL,
            result REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """
    )

    # Create greetings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()


# ========================================
# Calculation Operations
# ========================================


def save_calculation(
    operand1: float, operand2: float, result: float, db_path: Path | None = None
) -> int:
    """Save a calculation result to the database.

    Args:
        operand1: First number in the calculation
        operand2: Second number in the calculation
        result: Result of the calculation
        db_path: Path to the database file. Uses default if None.

    Returns:
        ID of the inserted record
    """
    if db_path is None:
        db_path = DB_PATH

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Insert the calculation
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO calculations (operand1, operand2, result, timestamp) VALUES (?, ?, ?, ?)",
        (operand1, operand2, result, timestamp),
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    assert record_id is not None, "Failed to get record ID"
    return record_id


def get_calculations(limit: int = 10, db_path: Path | None = None) -> list[dict]:
    """Retrieve recent calculations from the database.

    Args:
        limit: Maximum number of records to retrieve
        db_path: Path to the database file. Uses default if None.

    Returns:
        List of calculation dictionaries with keys: id, operand1, operand2, result, timestamp
    """
    if db_path is None:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM calculations ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )

    # Convert rows to dictionaries
    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results


# ========================================
# Greeting Operations
# ========================================


def save_greeting(name: str, db_path: Path | None = None) -> int:
    """Save a greeting to the database.

    Args:
        name: Name used in the greeting
        db_path: Path to the database file. Uses default if None.

    Returns:
        ID of the inserted record
    """
    if db_path is None:
        db_path = DB_PATH

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Insert the greeting
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO greetings (name, timestamp) VALUES (?, ?)",
        (name, timestamp),
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    assert record_id is not None, "Failed to get record ID"
    return record_id


def get_greetings(limit: int = 10, db_path: Path | None = None) -> list[dict]:
    """Retrieve recent greetings from the database.

    Args:
        limit: Maximum number of records to retrieve
        db_path: Path to the database file. Uses default if None.

    Returns:
        List of greeting dictionaries with keys: id, name, timestamp
    """
    if db_path is None:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM greetings ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )

    # Convert rows to dictionaries
    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results

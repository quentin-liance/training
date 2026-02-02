"""Pytest configuration and fixtures."""

import pandas as pd
import pytest


@pytest.fixture
def sample_raw_data():
    """Create sample raw data mimicking CSV input."""
    return pd.DataFrame(
        {
            "Categorie": ["Food", "Food", "Transport", "Transport", "Housing"],
            "Sous categorie": ["Restaurant", "Groceries", "Public", "Fuel", "Rent"],
            "Libelle operation": [
                "Lunch",
                "Weekly shopping",
                "Metro",
                "Gas station",
                "Monthly rent",
            ],
            "Debit": [-50.0, -120.0, -30.0, -60.0, -800.0],
            "Credit": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Date operation": [
                "2026-01-15",
                "2026-01-16",
                "2026-01-17",
                "2026-01-18",
                "2026-01-20",
            ],
        }
    )


@pytest.fixture
def sample_processed_data():
    """Create sample processed data after transformation."""
    return pd.DataFrame(
        {
            "CATEGORY": ["Food", "Food", "Transport", "Transport", "Housing"],
            "SUBCATEGORY": ["Restaurant", "Groceries", "Public", "Fuel", "Rent"],
            "OPERATION_LABEL": ["Lunch", "Weekly shopping", "Metro", "Gas station", "Monthly rent"],
            "OPERATION_DATE": [
                "2026-01-15",
                "2026-01-16",
                "2026-01-17",
                "2026-01-18",
                "2026-01-20",
            ],
            "AMOUNT": [-50.0, -120.0, -30.0, -60.0, -800.0],
        }
    )


@pytest.fixture
def sample_expenses():
    """Create sample expense data with AMOUNT_ABS column."""
    return pd.DataFrame(
        {
            "CATEGORY": ["Food", "Food", "Transport", "Transport", "Housing"],
            "SUBCATEGORY": ["Restaurant", "Groceries", "Public", "Fuel", "Rent"],
            "OPERATION_LABEL": ["Lunch", "Weekly shopping", "Metro", "Gas station", "Monthly rent"],
            "OPERATION_DATE": [
                "2026-01-15",
                "2026-01-16",
                "2026-01-17",
                "2026-01-18",
                "2026-01-20",
            ],
            "AMOUNT": [-50.0, -120.0, -30.0, -60.0, -800.0],
            "AMOUNT_ABS": [50.0, 120.0, 30.0, 60.0, 800.0],
        }
    )


@pytest.fixture
def empty_dataframe():
    """Create an empty DataFrame."""
    return pd.DataFrame()

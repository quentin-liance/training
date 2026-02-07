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


@pytest.fixture
def sample_operations_df():
    """Create sample operations DataFrame with datetime."""
    return pd.DataFrame(
        {
            "CATEGORY": ["Food", "Food", "Transport", "Transport", "Housing"],
            "SUBCATEGORY": ["Restaurant", "Groceries", "Public", "Fuel", "Rent"],
            "OPERATION_LABEL": ["Lunch", "Weekly shopping", "Metro", "Gas station", "Monthly rent"],
            "OPERATION_DATE": pd.to_datetime(
                [
                    "2026-01-15",
                    "2026-01-16",
                    "2026-01-17",
                    "2026-01-18",
                    "2026-01-20",
                ]
            ),
            "AMOUNT": [-50.0, -120.0, -30.0, -60.0, -800.0],
        }
    )


@pytest.fixture
def mock_csv_content():
    """Create mock CSV content for testing."""
    return (
        "Date de comptabilisation;Libelle simplifie;Libelle operation;"
        "Reference;Informations complementaires;Type operation;"
        "Categorie;Sous categorie;Debit;Credit;Date operation;"
        "Date de valeur;Pointage operation\n"
        "01/01/2026;Restaurant;Lunch at cafe;REF123;;DEBIT;"
        "Food;Restaurant;-50.0;0.0;01/01/2026;01/01/2026;N\n"
        "02/01/2026;Groceries;Weekly shopping;REF124;;DEBIT;"
        "Food;Groceries;-120.0;0.0;02/01/2026;02/01/2026;N"
    )


@pytest.fixture
def invalid_csv_content():
    """Create invalid CSV content missing required columns."""
    return "Date;Amount;Description\n01/01/2026;-50.0;Test\n02/01/2026;-30.0;Test2"

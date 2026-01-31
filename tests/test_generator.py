"""Tests for data generation utilities."""

import pandas as pd

from src.data.generator import generate_fake_data


class TestDataGenerator:
    """Tests for fake data generation."""

    def test_generate_fake_data_structure(self) -> None:
        """Test that generated data has correct structure."""
        data = generate_fake_data()

        # Check that data dictionary has required keys
        assert "incomes" in data
        assert "costs" in data

        # Check that both are DataFrames
        assert isinstance(data["incomes"], pd.DataFrame)
        assert isinstance(data["costs"], pd.DataFrame)

    def test_generate_fake_data_columns(self) -> None:
        """Test that generated data has required columns."""
        data = generate_fake_data()

        incomes = data["incomes"]
        costs = data["costs"]

        # Check columns for incomes
        required_income_cols = ["Month", "Category", "Amount", "Type"]
        for col in required_income_cols:
            assert col in incomes.columns, f"Missing column: {col}"

        # Check columns for costs
        required_cost_cols = ["Month", "Category", "Amount", "Type"]
        for col in required_cost_cols:
            assert col in costs.columns, f"Missing column: {col}"

    def test_generate_fake_data_not_empty(self) -> None:
        """Test that generated data is not empty."""
        data = generate_fake_data()

        assert len(data["incomes"]) > 0
        assert len(data["costs"]) > 0

    def test_generate_fake_data_months(self) -> None:
        """Test that data contains expected number of months."""
        data = generate_fake_data()

        incomes = data["incomes"]
        costs = data["costs"]

        # Should have multiple months (the generator creates 12 months worth of data)
        # But due to the way datetime works, we might get 11-12 months depending on timing
        assert len(incomes["Month"].unique()) >= 11
        assert len(costs["Month"].unique()) >= 11

    def test_generate_fake_data_amounts_positive(self) -> None:
        """Test that all amounts are positive."""
        data = generate_fake_data()

        incomes = data["incomes"]
        costs = data["costs"]

        # All amounts should be positive
        assert (incomes["Amount"] > 0).all()
        assert (costs["Amount"] > 0).all()

    def test_generate_fake_data_type_field(self) -> None:
        """Test that Type field is correctly set."""
        data = generate_fake_data()

        incomes = data["incomes"]
        costs = data["costs"]

        # All incomes should have Type = "Income"
        assert (incomes["Type"] == "Income").all()
        # All costs should have Type = "Cost"
        assert (costs["Type"] == "Cost").all()

    def test_generate_fake_data_categories(self) -> None:
        """Test that data contains expected categories."""
        data = generate_fake_data()

        incomes = data["incomes"]
        costs = data["costs"]

        # Check that we have multiple income categories
        income_categories = incomes["Category"].unique()
        assert len(income_categories) >= 3, "Should have at least 3 income categories"

        # Check that we have multiple cost categories
        cost_categories = costs["Category"].unique()
        assert len(cost_categories) >= 5, "Should have at least 5 cost categories"

    def test_generate_fake_data_consistency(self) -> None:
        """Test that multiple calls generate consistent structure."""
        data1 = generate_fake_data()
        data2 = generate_fake_data()

        # Should have same columns
        assert list(data1["incomes"].columns) == list(data2["incomes"].columns)
        assert list(data1["costs"].columns) == list(data2["costs"].columns)

        # Should have same number of categories (structure)
        assert len(data1["incomes"]["Category"].unique()) == len(
            data2["incomes"]["Category"].unique()
        )
        assert len(data1["costs"]["Category"].unique()) == len(data2["costs"]["Category"].unique())

"""Tests for calculation utilities."""

import pandas as pd
import pytest

from src.utils.calculations import (
    calculate_margin_by_category,
    calculate_margins,
    calculate_totals,
)


class TestCalculations:
    """Tests for margin calculation functions."""

    def test_calculate_totals_basic(self) -> None:
        """Test basic total calculations."""
        incomes = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-01"],
                "Category": ["Sales", "Services"],
                "Amount": [1000.0, 500.0],
            }
        )
        costs = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-01"],
                "Category": ["Rent", "Salaries"],
                "Amount": [300.0, 400.0],
            }
        )

        result = calculate_totals(incomes, costs)

        assert result["total_income"] == 1500.0
        assert result["total_costs"] == 700.0
        assert result["net_margin"] == 800.0

    def test_calculate_margins_by_month(self) -> None:
        """Test margin calculation by month."""
        incomes = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-02"],
                "Category": ["Sales", "Sales"],
                "Amount": [1000.0, 1200.0],
            }
        )
        costs = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-02"],
                "Category": ["Rent", "Rent"],
                "Amount": [300.0, 300.0],
            }
        )

        result = calculate_margins(incomes, costs)

        assert len(result) == 2
        assert result.loc[result["Month"] == "2024-01", "Margin"].values[0] == 700.0
        assert result.loc[result["Month"] == "2024-02", "Margin"].values[0] == 900.0

    def test_calculate_totals_empty(self) -> None:
        """Test calculation with empty dataframes."""
        incomes = pd.DataFrame(columns=["Month", "Category", "Amount"])
        costs = pd.DataFrame(columns=["Month", "Category", "Amount"])

        result = calculate_totals(incomes, costs)

        assert result["total_income"] == 0
        assert result["total_costs"] == 0
        assert result["net_margin"] == 0

    def test_calculate_margins_with_zero_income(self) -> None:
        """Test margin calculation with zero income (avoid division by zero)."""
        incomes = pd.DataFrame(
            {
                "Month": ["2024-01"],
                "Category": ["Sales"],
                "Amount": [0.0],
            }
        )
        costs = pd.DataFrame(
            {
                "Month": ["2024-01"],
                "Category": ["Rent"],
                "Amount": [300.0],
            }
        )

        result = calculate_margins(incomes, costs)

        assert len(result) == 1
        assert result.loc[result["Month"] == "2024-01", "Margin"].values[0] == -300.0
        assert result.loc[result["Month"] == "2024-01", "Margin %"].values[0] == 0.0

    def test_calculate_margins_missing_months(self) -> None:
        """Test margin calculation when months don't align."""
        incomes = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-03"],
                "Category": ["Sales", "Sales"],
                "Amount": [1000.0, 1500.0],
            }
        )
        costs = pd.DataFrame(
            {
                "Month": ["2024-01", "2024-02"],
                "Category": ["Rent", "Rent"],
                "Amount": [300.0, 300.0],
            }
        )

        result = calculate_margins(incomes, costs)

        assert len(result) == 3  # Should have 2024-01, 2024-02, 2024-03
        # Month with only costs (2024-02)
        feb_row = result.loc[result["Month"] == "2024-02"]
        assert feb_row["Income"].values[0] == 0.0
        assert feb_row["Costs"].values[0] == 300.0
        assert feb_row["Margin %"].values[0] == 0.0

    def test_calculate_totals_missing_column(self) -> None:
        """Test error handling when required column is missing."""
        incomes = pd.DataFrame({"Month": ["2024-01"], "Category": ["Sales"]})
        costs = pd.DataFrame({"Month": ["2024-01"], "Category": ["Rent"], "Amount": [300.0]})

        with pytest.raises(ValueError, match="missing required column"):
            calculate_totals(incomes, costs)

    def test_calculate_margins_missing_column(self) -> None:
        """Test error handling when required column is missing."""
        incomes = pd.DataFrame({"Category": ["Sales"], "Amount": [1000.0]})
        costs = pd.DataFrame({"Month": ["2024-01"], "Category": ["Rent"], "Amount": [300.0]})

        with pytest.raises(ValueError, match="missing required column"):
            calculate_margins(incomes, costs)

    def test_calculate_margin_by_category(self) -> None:
        """Test margin calculation by category."""
        incomes = pd.DataFrame(
            {
                "Category": ["Sales", "Services", "Sales"],
                "Amount": [1000.0, 500.0, 2000.0],
            }
        )
        costs = pd.DataFrame(
            {
                "Category": ["Rent", "Salaries", "Salaries"],
                "Amount": [300.0, 400.0, 600.0],
            }
        )

        result = calculate_margin_by_category(incomes, costs)

        assert "income_by_category" in result
        assert "costs_by_category" in result
        assert result["income_by_category"]["Sales"] == 3000.0
        assert result["income_by_category"]["Services"] == 500.0
        assert result["costs_by_category"]["Rent"] == 300.0
        assert result["costs_by_category"]["Salaries"] == 1000.0

    def test_calculate_margin_by_category_missing_column(self) -> None:
        """Test error handling for calculate_margin_by_category."""
        incomes = pd.DataFrame({"Month": ["2024-01"], "Amount": [1000.0]})
        costs = pd.DataFrame({"Category": ["Rent"], "Amount": [300.0]})

        with pytest.raises(ValueError, match="missing required columns"):
            calculate_margin_by_category(incomes, costs)

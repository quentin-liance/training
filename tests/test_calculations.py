"""Tests for calculation utilities."""

import pandas as pd

from src.utils.calculations import calculate_margins, calculate_totals


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

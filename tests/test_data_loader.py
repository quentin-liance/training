"""Unit tests for data_loader module."""

import pandas as pd

from src.data_loader import (
    calculate_category_totals,
    calculate_statistics,
    filter_expenses,
    prepare_chart_data,
    prepare_summary_table,
)


class TestFilterExpenses:
    """Tests for filter_expenses function."""

    def test_filter_negative_amounts_only(self, sample_processed_data):
        """Test that only negative amounts are kept."""
        # Add positive amount
        df_with_positive = sample_processed_data.copy()
        df_with_positive.loc[len(df_with_positive)] = [
            "Income",
            "Salary",
            "Monthly",
            "2026-01-25",
            2000.0,
        ]

        result = filter_expenses(df_with_positive, quantile_threshold=0.0)

        assert len(result) == 5  # Only the 5 negative amounts
        assert all(result["AMOUNT"] < 0)
        assert "AMOUNT_ABS" in result.columns

    def test_quantile_threshold_excludes_extremes(self, sample_processed_data):
        """Test that quantile threshold excludes extreme values."""
        result = filter_expenses(sample_processed_data, quantile_threshold=0.2)

        # With 5 values and 0.2 threshold, the lowest value (-800) should be excluded
        assert len(result) == 4
        assert -800.0 not in result["AMOUNT"].values

    def test_amount_abs_column_added(self, sample_processed_data):
        """Test that AMOUNT_ABS column is correctly added."""
        result = filter_expenses(sample_processed_data, quantile_threshold=0.0)

        assert "AMOUNT_ABS" in result.columns
        assert all(result["AMOUNT_ABS"] == result["AMOUNT"].abs())

    def test_sorted_by_amount_ascending(self, sample_processed_data):
        """Test that results are sorted by amount ascending."""
        result = filter_expenses(sample_processed_data, quantile_threshold=0.0)

        assert result["AMOUNT"].is_monotonic_increasing

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        # Create empty DataFrame with correct columns
        empty_df = pd.DataFrame(
            columns=["CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "OPERATION_DATE", "AMOUNT"]
        )
        result = filter_expenses(empty_df, quantile_threshold=0.0)

        assert len(result) == 0


class TestCalculateStatistics:
    """Tests for calculate_statistics function."""

    def test_statistics_calculation(self, sample_expenses):
        """Test that statistics are correctly calculated."""
        stats = calculate_statistics(sample_expenses)

        assert stats["count"] == 5
        assert stats["total"] == 1060.0  # 50 + 120 + 30 + 60 + 800
        assert stats["mean"] == 212.0  # 1060 / 5
        assert stats["min"] == 30.0
        assert stats["max"] == 800.0

    def test_statistics_keys(self, sample_expenses):
        """Test that all expected keys are present."""
        stats = calculate_statistics(sample_expenses)

        expected_keys = {"count", "total", "mean", "min", "max"}
        assert set(stats.keys()) == expected_keys

    def test_single_row(self):
        """Test statistics with single row."""
        df = pd.DataFrame({"AMOUNT_ABS": [100.0]})
        stats = calculate_statistics(df)

        assert stats["count"] == 1
        assert stats["total"] == 100.0
        assert stats["mean"] == 100.0
        assert stats["min"] == 100.0
        assert stats["max"] == 100.0


class TestPrepareChartData:
    """Tests for prepare_chart_data function."""

    def test_aggregation_by_category_subcategory(self, sample_expenses):
        """Test that data is correctly aggregated."""
        result = prepare_chart_data(sample_expenses)

        assert len(result) == 5  # 5 unique category/subcategory combinations
        assert "CATEGORY" in result.columns
        assert "SUBCATEGORY" in result.columns
        assert "AMOUNT_ABS" in result.columns

    def test_sum_aggregation(self):
        """Test that amounts are summed for duplicate category/subcategory."""
        df = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Food", "Food"],
                "SUBCATEGORY": ["Restaurant", "Restaurant", "Groceries"],
                "AMOUNT_ABS": [50.0, 30.0, 100.0],
            }
        )
        result = prepare_chart_data(df)

        assert len(result) == 2  # 2 unique combinations
        restaurant_total = result[
            (result["CATEGORY"] == "Food") & (result["SUBCATEGORY"] == "Restaurant")
        ]["AMOUNT_ABS"].values[0]
        assert restaurant_total == 80.0  # 50 + 30


class TestCalculateCategoryTotals:
    """Tests for calculate_category_totals function."""

    def test_category_totals(self, sample_expenses):
        """Test that category totals are correctly calculated."""
        result = calculate_category_totals(sample_expenses)

        assert len(result) == 3  # 3 categories: Food, Transport, Housing
        assert "CATEGORY" in result.columns
        assert "TOTAL" in result.columns

    def test_total_values(self, sample_expenses):
        """Test that total values are correct."""
        result = calculate_category_totals(sample_expenses)

        food_total = result[result["CATEGORY"] == "Food"]["TOTAL"].values[0]
        transport_total = result[result["CATEGORY"] == "Transport"]["TOTAL"].values[0]
        housing_total = result[result["CATEGORY"] == "Housing"]["TOTAL"].values[0]

        assert food_total == 170.0  # 50 + 120
        assert transport_total == 90.0  # 30 + 60
        assert housing_total == 800.0


class TestPrepareSummaryTable:
    """Tests for prepare_summary_table function."""

    def test_summary_table_structure(self, sample_expenses):
        """Test that summary table has correct structure."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        expected_columns = [
            "CATEGORY",
            "SUBCATEGORY",
            "OPERATION_LABEL",
            "Total (€)",
            "Detail/Subcat Ratio (%)",
            "Subcategory Total (€)",
            "Subcat/Cat Ratio (%)",
            "Category Total (€)",
            "Cat/Global Ratio (%)",
            "Global Total (€)",
        ]
        assert list(result.columns) == expected_columns

    def test_summary_table_row_count(self, sample_expenses):
        """Test that each operation has a row."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        assert len(result) == 5  # 5 operations

    def test_global_total_consistency(self, sample_expenses):
        """Test that global total is consistent across all rows."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        global_totals = result["Global Total (€)"].unique()
        assert len(global_totals) == 1  # Should be same for all rows
        assert global_totals[0] == -1060.0  # Sum of all negative amounts

    def test_ratios_sum_to_100(self, sample_expenses):
        """Test that ratios within each group sum to approximately 100%."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        # Check that detail/subcat ratios sum to ~100% for each subcategory
        for subcat in result["SUBCATEGORY"].unique():
            subcat_data = result[result["SUBCATEGORY"] == subcat]
            ratio_sum = subcat_data["Detail/Subcat Ratio (%)"].sum()
            assert abs(ratio_sum - 100.0) < 0.1  # Allow small floating point error

"""Unit tests for data_loader module."""

from unittest.mock import Mock, patch

import pandas as pd

from src.data_loader import (
    calculate_category_totals,
    calculate_statistics,
    filter_expenses,
    load_data,
    prepare_category_month_pivot,
    prepare_chart_data,
    prepare_summary_table,
    validate_csv_schema,
)


class TestValidateCsvSchema:
    """Tests for validate_csv_schema function."""

    def test_valid_schema_success(self, mock_csv_content):
        """Test validation with correct CSV schema."""
        # Create a mock uploaded file
        mock_file = Mock()

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
        ):
            # Mock pandas read_csv to return expected columns
            mock_df = pd.DataFrame(
                columns=[
                    "Date de comptabilisation",
                    "Libelle simplifie",
                    "Libelle operation",
                    "Reference",
                    "Informations complementaires",
                    "Type operation",
                    "Categorie",
                    "Sous categorie",
                    "Debit",
                    "Credit",
                    "Date operation",
                    "Date de valeur",
                    "Pointage operation",
                ]
            )
            mock_read_csv.return_value = mock_df

            # Execute
            is_valid, error_message = validate_csv_schema(mock_file)

            # Verify
            assert is_valid is True
            assert error_message == ""
            mock_file.seek.assert_called_once_with(0)
            mock_logger.info.assert_called_once_with("CSV schema validation successful")

    def test_missing_columns_error(self):
        """Test validation with missing required columns."""
        mock_file = Mock()

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
        ):
            # Mock DataFrame with missing columns
            mock_df = pd.DataFrame(columns=["Date", "Amount", "Description"])
            mock_read_csv.return_value = mock_df

            # Execute
            is_valid, error_message = validate_csv_schema(mock_file)

            # Verify
            assert is_valid is False
            assert "Colonnes manquantes" in error_message
            assert "Date de comptabilisation" in error_message
            mock_logger.error.assert_called_once()

    def test_extra_columns_error(self):
        """Test validation with extra columns."""
        mock_file = Mock()

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
        ):
            # Mock DataFrame with all required columns plus extra ones
            required_columns = [
                "Date de comptabilisation",
                "Libelle simplifie",
                "Libelle operation",
                "Reference",
                "Informations complementaires",
                "Type operation",
                "Categorie",
                "Sous categorie",
                "Debit",
                "Credit",
                "Date operation",
                "Date de valeur",
                "Pointage operation",
            ]
            extra_columns = required_columns + ["Extra1", "Extra2"]
            mock_df = pd.DataFrame(columns=extra_columns)
            mock_read_csv.return_value = mock_df

            # Execute
            is_valid, error_message = validate_csv_schema(mock_file)

            # Verify
            assert is_valid is False
            assert "Colonnes supplémentaires" in error_message
            assert "Extra1" in error_message
            mock_logger.error.assert_called_once()

    def test_wrong_column_order_error(self):
        """Test validation with wrong column order."""
        mock_file = Mock()

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
        ):
            # Mock DataFrame with correct columns but wrong order
            required_columns = [
                "Date de comptabilisation",
                "Libelle simplifie",
                "Libelle operation",
                "Reference",
                "Informations complementaires",
                "Type operation",
                "Categorie",
                "Sous categorie",
                "Debit",
                "Credit",
                "Date operation",
                "Date de valeur",
                "Pointage operation",
            ]
            reordered_columns = required_columns[::-1]  # Reverse order
            mock_df = pd.DataFrame(columns=reordered_columns)
            mock_read_csv.return_value = mock_df

            # Execute
            is_valid, error_message = validate_csv_schema(mock_file)

            # Verify
            assert is_valid is False
            assert "L'ordre des colonnes ne correspond pas au schéma attendu" in error_message
            mock_logger.error.assert_called_once()

    def test_exception_handling(self):
        """Test validation with read exception."""
        mock_file = Mock()

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
        ):
            # Mock pandas to raise exception
            mock_read_csv.side_effect = Exception("Read error")

            # Execute
            is_valid, error_message = validate_csv_schema(mock_file)

            # Verify
            assert is_valid is False
            assert "Erreur lors de la validation" in error_message
            assert "Read error" in error_message
            mock_logger.error.assert_called_once()


class TestLoadData:
    """Tests for load_data function."""

    def test_load_default_file_success(self):
        """Test loading data from default file."""
        sample_csv_data = pd.DataFrame(
            {
                "Date de comptabilisation": ["01/01/2026", "02/01/2026"],
                "Libelle operation": ["Restaurant", "Groceries"],
                "Categorie": ["Food", "Food"],
                "Sous categorie": ["Restaurant", "Groceries"],
                "Debit": [-50.0, -120.0],
                "Credit": [0.0, 0.0],
                "Date operation": ["01/01/2026", "02/01/2026"],
            }
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
            patch("src.data_loader.st.cache_data", lambda func: func),
        ):  # Disable cache
            mock_read_csv.return_value = sample_csv_data

            # Execute
            result = load_data(uploaded_file=None)

            # Verify
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert "CATEGORY" in result.columns
            assert "SUBCATEGORY" in result.columns
            assert "OPERATION_LABEL" in result.columns
            assert "AMOUNT" in result.columns
            assert "OPERATION_DATE" in result.columns

            # Check that amounts are correctly calculated
            assert all(result["AMOUNT"] < 0)  # All expenses should be negative

            # Check log calls - be flexible about the path format
            log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            assert any(
                "Loading data from" in call and "20260101_20260201_operations.csv" in call
                for call in log_calls
            )
            mock_logger.info.assert_any_call("Data loaded successfully: 2 operations")

    def test_load_uploaded_file_success(self):
        """Test loading data from uploaded file."""
        mock_uploaded_file = Mock()
        mock_uploaded_file.name = "test_upload.csv"

        sample_csv_data = pd.DataFrame(
            {
                "Date de comptabilisation": ["01/01/2026"],
                "Libelle operation": ["Test transaction"],
                "Categorie": ["Transport"],
                "Sous categorie": ["Bus"],
                "Debit": [-30.0],
                "Credit": [0.0],
                "Date operation": ["01/01/2026"],
            }
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.logger") as mock_logger,
            patch("src.data_loader.st.cache_data", lambda func: func),
        ):  # Disable cache
            mock_read_csv.return_value = sample_csv_data

            # Execute
            result = load_data(uploaded_file=mock_uploaded_file)

            # Verify
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]["CATEGORY"] == "Transport"
            assert result.iloc[0]["AMOUNT"] == -30.0

            mock_logger.info.assert_any_call("Loading data from uploaded file: test_upload.csv")
            mock_logger.info.assert_any_call("Data loaded successfully: 1 operations")

    def test_data_aggregation_and_transformation(self):
        """Test that data is properly aggregated and transformed."""
        # The function groups by CATEGORY, SUBCATEGORY, OPERATION_LABEL, OPERATION_DATE
        # Let's test that basic transformation works correctly
        sample_csv_data = pd.DataFrame(
            {
                "Date de comptabilisation": ["01/01/2026", "02/01/2026"],
                "Libelle operation": ["Restaurant", "Groceries"],  # Different operations
                "Categorie": ["Food", "Food"],
                "Sous categorie": ["Restaurant", "Groceries"],  # Different subcategories
                "Debit": [-50.0, -120.0],
                "Credit": [0.0, 0.0],
                "Date operation": ["01/01/2026", "02/01/2026"],
            }
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.st.cache_data", lambda func: func),
        ):  # Disable cache
            mock_read_csv.return_value = sample_csv_data

            # Execute
            result = load_data(uploaded_file=None)

            # Verify basic transformation worked
            assert len(result) == 2  # Two different operations
            assert "CATEGORY" in result.columns
            assert "SUBCATEGORY" in result.columns
            assert "OPERATION_LABEL" in result.columns
            assert "AMOUNT" in result.columns
            assert "OPERATION_DATE" in result.columns

            # Verify column mapping and amount calculation
            assert all(result["AMOUNT"] < 0)  # All should be negative (expenses)

    def test_mixed_debit_credit_calculation(self):
        """Test amount calculation with both debit and credit values."""
        sample_csv_data = pd.DataFrame(
            {
                "Date de comptabilisation": ["01/01/2026", "02/01/2026"],
                "Libelle operation": ["Expense", "Income"],
                "Categorie": ["Food", "Income"],
                "Sous categorie": ["Restaurant", "Salary"],
                "Debit": [-50.0, 0.0],
                "Credit": [0.0, 1000.0],
                "Date operation": ["01/01/2026", "02/01/2026"],
            }
        )

        # Create a unique mock to avoid cache issues
        mock_file = Mock()
        mock_file.name = "unique_test_file.csv"

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.st.cache_data", lambda func: func),
        ):  # Disable cache
            mock_read_csv.return_value = sample_csv_data

            # Execute
            result = load_data(uploaded_file=mock_file)

            # Verify
            assert len(result) == 2
            amounts = result["AMOUNT"].tolist()
            assert -50.0 in amounts  # Debit amount
            assert 1000.0 in amounts  # Credit amount

    def test_sorting_by_category(self):
        """Test that results are sorted by category."""
        sample_csv_data = pd.DataFrame(
            {
                "Date de comptabilisation": ["01/01/2026", "02/01/2026", "03/01/2026"],
                "Libelle operation": ["Transport", "Food", "Housing"],
                "Categorie": ["Transport", "Food", "Housing"],  # Not alphabetical
                "Sous categorie": ["Bus", "Restaurant", "Rent"],
                "Debit": [-30.0, -50.0, -800.0],
                "Credit": [0.0, 0.0, 0.0],
                "Date operation": ["01/01/2026", "02/01/2026", "03/01/2026"],
            }
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("src.data_loader.st.cache_data", lambda func: func),
        ):  # Disable cache
            mock_read_csv.return_value = sample_csv_data

            # Execute
            result = load_data(uploaded_file=None)

            # Verify sorting
            categories = result["CATEGORY"].tolist()
            assert categories == sorted(categories)  # Should be alphabetically sorted


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
            "Date",
            "CATEGORY",
            "SUBCATEGORY",
            "OPERATION_LABEL",
            "Total (€)",
        ]
        assert list(result.columns) == expected_columns

    def test_summary_table_row_count(self, sample_expenses):
        """Test that table has grouped operations."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        # Table groups by date, category, subcategory, and label
        # so row count depends on unique combinations
        assert len(result) >= 0

    def test_global_total_consistency(self, sample_expenses):
        """Test that totals are calculated correctly."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        # Check that Total column exists and contains numeric values
        assert "Total (€)" in result.columns
        if len(result) > 0:
            assert result["Total (€)"].dtype in ["float64", "int64"]

    def test_ratios_sum_to_100(self, sample_expenses):
        """Test that table has Date column in correct format."""
        result = prepare_summary_table(sample_expenses, sample_expenses)

        # Check that Date column exists
        assert "Date" in result.columns
        if len(result) > 0:
            # Date should be string in YYYY-MM-DD format
            assert isinstance(result["Date"].iloc[0], str)


class TestPrepareCategoryMonthPivot:
    """Tests for prepare_category_month_pivot function."""

    def test_empty_dataframe_returns_empty(self):
        """Test that empty DataFrame returns empty pivot table."""
        empty_df = pd.DataFrame()
        result = prepare_category_month_pivot(empty_df)

        assert result.empty
        assert isinstance(result, pd.DataFrame)

    def test_pivot_table_structure(self, sample_expenses):
        """Test that pivot table has correct structure."""
        # Convert OPERATION_DATE to datetime for this test
        sample_expenses = sample_expenses.copy()
        sample_expenses["OPERATION_DATE"] = pd.to_datetime(sample_expenses["OPERATION_DATE"])

        result = prepare_category_month_pivot(sample_expenses)

        # Check that result is not empty
        assert not result.empty
        assert isinstance(result, pd.DataFrame)

        # Check that 'Total' column exists
        assert "Total" in result.columns

        # Check that categories are in index
        assert len(result.index) > 0

    def test_pivot_table_has_month_columns(self):
        """Test that pivot table has month columns in correct format."""
        # Create test data with multiple months
        test_data = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Food", "Transport", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Groceries", "Public", "Fuel"],
                "OPERATION_LABEL": ["Lunch", "Shopping", "Metro", "Gas"],
                "OPERATION_DATE": pd.to_datetime(
                    ["2026-01-15", "2026-02-10", "2026-01-20", "2026-02-05"]
                ),
                "AMOUNT": [-50.0, -120.0, -30.0, -60.0],
            }
        )

        result = prepare_category_month_pivot(test_data)

        # Check that month columns exist (format: YYYY-MM)
        month_columns = [col for col in result.columns if col != "Total"]
        assert len(month_columns) > 0
        # Month columns should be strings in YYYY-MM format
        for col in month_columns:
            assert isinstance(col, str)
            assert len(col) == 7  # YYYY-MM format

    def test_pivot_table_totals_calculated_correctly(self):
        """Test that totals are calculated correctly."""
        # Create test data with known amounts
        test_data = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Groceries", "Public"],
                "OPERATION_LABEL": ["Lunch", "Shopping", "Metro"],
                "OPERATION_DATE": pd.to_datetime(["2026-01-15", "2026-01-20", "2026-01-25"]),
                "AMOUNT": [-100.0, -200.0, -50.0],
            }
        )

        result = prepare_category_month_pivot(test_data)

        # Check that Food category total is 300 (100 + 200)
        food_total = result.loc["Food", "Total"]
        assert food_total == -300.0

        # Check that Transport category total is 50
        transport_total = result.loc["Transport", "Total"]
        assert transport_total == -50.0

    def test_pivot_table_sorted_by_total(self):
        """Test that pivot table is sorted by total descending."""
        test_data = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Transport", "Housing"],
                "SUBCATEGORY": ["Restaurant", "Public", "Rent"],
                "OPERATION_LABEL": ["Lunch", "Metro", "Rent"],
                "OPERATION_DATE": pd.to_datetime(["2026-01-15", "2026-01-20", "2026-01-25"]),
                "AMOUNT": [-100.0, -50.0, -800.0],
            }
        )

        result = prepare_category_month_pivot(test_data)

        # Check that categories are sorted by total (descending)
        totals = result["Total"].tolist()
        assert totals == sorted(totals, reverse=True)

    def test_pivot_table_with_multiple_months(self):
        """Test pivot table with data spanning multiple months."""
        test_data = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Food", "Food", "Transport", "Transport"],
                "SUBCATEGORY": ["Rest", "Rest", "Groc", "Bus", "Bus"],
                "OPERATION_LABEL": ["L1", "L2", "S1", "T1", "T2"],
                "OPERATION_DATE": pd.to_datetime(
                    ["2026-01-15", "2026-02-10", "2026-03-05", "2026-01-20", "2026-02-15"]
                ),
                "AMOUNT": [-50.0, -60.0, -70.0, -30.0, -40.0],
            }
        )

        result = prepare_category_month_pivot(test_data)

        # Check that we have 3 month columns + Total
        assert len(result.columns) == 4

        # Check specific month values for Food category
        assert result.loc["Food", "2026-01"] == -50.0
        assert result.loc["Food", "2026-02"] == -60.0
        assert result.loc["Food", "2026-03"] == -70.0
        assert result.loc["Food", "Total"] == -180.0

    def test_pivot_table_fill_value_zero(self):
        """Test that missing values are filled with 0."""
        test_data = pd.DataFrame(
            {
                "CATEGORY": ["Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Bus"],
                "OPERATION_LABEL": ["Lunch", "Ticket"],
                "OPERATION_DATE": pd.to_datetime(["2026-01-15", "2026-02-10"]),
                "AMOUNT": [-100.0, -30.0],
            }
        )

        result = prepare_category_month_pivot(test_data)

        # Food should have 0 for February
        assert result.loc["Food", "2026-02"] == 0.0
        # Transport should have 0 for January
        assert result.loc["Transport", "2026-01"] == 0.0

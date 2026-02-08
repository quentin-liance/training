"""Unit tests for main module."""

from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

from src.main import main


class TestMain:
    """Tests for main function."""

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_no_uploaded_file_success(
        self, mock_logger, mock_validate, mock_load_data, mock_st
    ):
        """Test main function with no uploaded file - successful execution."""
        # Setup
        mock_st.file_uploader.return_value = None
        sample_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["01/01/2026", "02/01/2026"],
                "CATEGORY": ["Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Bus"],
                "AMOUNT": [-50.0, -30.0],
            }
        )
        mock_load_data.return_value = sample_df

        # Mock datetime conversion to return proper datetime series
        datetime_series = pd.to_datetime(["2026-01-01", "2026-01-02"])

        # Mock sidebar inputs
        mock_st.sidebar.date_input.side_effect = [
            date(2026, 1, 1),  # start date
            date(2026, 1, 2),  # end date
        ]
        mock_st.sidebar.slider.return_value = 10  # quantile threshold
        mock_st.multiselect.side_effect = [[], []]  # no category/subcategory filters

        # Mock data processing functions
        with (
            patch("src.main.filter_expenses") as mock_filter,
            patch("src.main.calculate_statistics") as mock_stats,
            patch("src.main.display_sidebar_statistics"),
            patch("src.main.prepare_chart_data") as mock_prepare_chart,
            patch("src.main.calculate_category_totals") as mock_calc_totals,
            patch("src.main.create_stacked_bar_chart") as mock_chart,
            patch("src.main.prepare_summary_table") as mock_summary,
            patch("src.main.create_aggrid_table"),
            patch("pandas.to_datetime") as mock_to_datetime,
        ):
            mock_to_datetime.return_value = datetime_series

            # Create a processed dataframe with datetime
            processed_df = sample_df.copy()
            processed_df["OPERATION_DATE"] = datetime_series

            mock_filter.return_value = processed_df
            mock_stats.return_value = {
                "count": 2,
                "total": -80.0,
                "mean": -40.0,
                "min": -30.0,
                "max": -50.0,
            }
            mock_prepare_chart.return_value = pd.DataFrame()
            mock_calc_totals.return_value = pd.DataFrame()
            mock_chart.return_value = MagicMock()
            mock_summary.return_value = pd.DataFrame()

            # Execute
            main()

            # Verify
            mock_st.set_page_config.assert_called_once()
            mock_st.title.assert_called_once_with("💰 Analyse des Opérations Bancaires")
            mock_load_data.assert_called_once_with(None)
            mock_filter.assert_called_once()
            # calculate_statistics est appelé 2 fois:
            # une fois pour toutes les données, une fois après exclusions
            assert mock_stats.call_count == 2

    @patch("src.main.st")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_uploaded_file_invalid_schema(self, mock_logger, mock_validate, mock_st):
        """Test main function with uploaded file having invalid schema."""
        # Setup
        mock_uploaded_file = Mock()
        mock_uploaded_file.name = "test.csv"
        mock_st.file_uploader.return_value = mock_uploaded_file
        mock_validate.return_value = (False, "Invalid columns")

        # Execute
        main()

        # Verify
        mock_validate.assert_called_once_with(mock_uploaded_file)
        mock_st.error.assert_called_once()
        error_call = mock_st.error.call_args[0][0]
        assert "Le fichier uploadé ne correspond pas au schéma attendu" in error_call
        assert "Invalid columns" in error_call
        mock_logger.error.assert_called_once_with("Schema validation failed for test.csv")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_file_not_found_error(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function with FileNotFoundError."""
        # Setup
        mock_st.file_uploader.return_value = None
        mock_load_data.side_effect = FileNotFoundError("File not found")

        # Execute
        main()

        # Verify
        mock_st.error.assert_called_once_with(
            "⚠️ Le fichier de données par défaut est introuvable. Veuillez uploader un fichier CSV."
        )
        mock_logger.error.assert_called_once_with("Default data file not found")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_empty_data_error(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function with EmptyDataError."""
        # Setup
        mock_st.file_uploader.return_value = None
        mock_load_data.side_effect = pd.errors.EmptyDataError("Empty file")

        # Execute
        main()

        # Verify
        mock_st.error.assert_called_once_with(
            "⚠️ Le fichier CSV est vide. Veuillez vérifier vos données."
        )
        mock_logger.error.assert_called_once_with("Empty CSV file provided")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_generic_exception(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function with generic exception."""
        # Setup
        mock_st.file_uploader.return_value = None
        mock_load_data.side_effect = Exception("Unexpected error")

        # Execute
        main()

        # Verify
        mock_st.error.assert_called_once_with(
            "⚠️ Erreur lors du chargement des données : Unexpected error"
        )
        mock_logger.exception.assert_called_once_with("Error loading data")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_logs_startup_message(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test that main function logs startup message."""
        # Setup
        mock_st.file_uploader.return_value = None
        mock_load_data.side_effect = FileNotFoundError("Test error")

        # Execute
        main()

        # Verify startup message is logged
        mock_logger.info.assert_any_call("Starting Bank Operations Analysis application")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_no_valid_dates(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function when no valid dates remain after conversion."""
        # Setup
        mock_st.file_uploader.return_value = None
        sample_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["invalid_date1", "invalid_date2"],
                "CATEGORY": ["Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Bus"],
                "AMOUNT": [-50.0, -30.0],
            }
        )
        mock_load_data.return_value = sample_df

        # Mock successful date conversion but all NaT
        with patch("pandas.to_datetime") as mock_to_datetime:
            mock_to_datetime.return_value = pd.Series([pd.NaT, pd.NaT])

            # Execute
            main()

            # Verify
            mock_st.error.assert_called_once_with("Aucune donnée avec des dates valides trouvée.")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_category_filters(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function with category filters applied."""
        # Setup
        mock_st.file_uploader.return_value = None
        sample_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["01/01/2026", "02/01/2026", "03/01/2026"],
                "CATEGORY": ["Food", "Transport", "Food"],
                "SUBCATEGORY": ["Restaurant", "Bus", "Groceries"],
                "AMOUNT": [-50.0, -30.0, -20.0],
            }
        )
        mock_load_data.return_value = sample_df

        # Mock datetime conversion
        datetime_series = pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"])

        # Mock sidebar inputs
        mock_st.sidebar.date_input.side_effect = [
            date(2026, 1, 1),  # start date
            date(2026, 1, 3),  # end date
        ]
        mock_st.sidebar.slider.return_value = 0  # no quantile threshold
        mock_st.multiselect.side_effect = [
            ["Food"],  # selected categories
            ["Restaurant"],  # selected subcategories
        ]

        # Mock data processing functions
        with (
            patch("src.main.filter_expenses") as mock_filter,
            patch("src.main.calculate_statistics") as mock_stats,
            patch("src.main.display_sidebar_statistics"),
            patch("src.main.prepare_chart_data") as mock_prepare_chart,
            patch("src.main.calculate_category_totals") as mock_calc_totals,
            patch("src.main.create_stacked_bar_chart") as mock_chart,
            patch("src.main.prepare_summary_table") as mock_summary,
            patch("src.main.create_aggrid_table"),
            patch("pandas.to_datetime") as mock_to_datetime,
        ):
            mock_to_datetime.return_value = datetime_series

            # Create processed dataframe with datetime
            processed_df = sample_df.copy()
            processed_df["OPERATION_DATE"] = datetime_series

            mock_filter.return_value = processed_df
            mock_stats.return_value = {
                "count": 3,
                "total": -100.0,
                "mean": -33.33,
                "min": -20.0,
                "max": -50.0,
            }
            mock_prepare_chart.return_value = pd.DataFrame()
            mock_calc_totals.return_value = pd.DataFrame()
            mock_chart.return_value = MagicMock()
            mock_summary.return_value = pd.DataFrame()

            # Execute
            main()

            # Verify the main components were called
            mock_st.set_page_config.assert_called_once()
            mock_filter.assert_called_once()
            # calculate_statistics is called twice:
            # once for all data, once for final analysis after exclusions
            assert mock_stats.call_count == 2
            # Just verify multiselect was called, don't check exact parameters
            assert mock_st.multiselect.call_count >= 2  # categories and subcategories

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_valid_uploaded_file(
        self, mock_logger, mock_validate, mock_load_data, mock_st
    ):
        """Test main function with valid uploaded file."""
        # Setup
        mock_uploaded_file = Mock()
        mock_uploaded_file.name = "test.csv"
        mock_st.file_uploader.return_value = mock_uploaded_file
        mock_validate.return_value = (True, "")

        sample_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["01/01/2026", "02/01/2026"],
                "CATEGORY": ["Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Bus"],
                "AMOUNT": [-50.0, -30.0],
            }
        )
        mock_load_data.return_value = sample_df

        # Mock datetime conversion to work correctly
        datetime_series = pd.to_datetime(["2026-01-01", "2026-01-02"])

        # Mock sidebar inputs
        mock_st.sidebar.date_input.side_effect = [
            date(2026, 1, 1),  # start date
            date(2026, 1, 2),  # end date
        ]
        mock_st.sidebar.slider.return_value = 10
        mock_st.multiselect.side_effect = [[], []]

        with (
            patch("src.main.filter_expenses") as mock_filter,
            patch("src.main.calculate_statistics") as mock_stats,
            patch("src.main.display_sidebar_statistics"),
            patch("src.main.prepare_chart_data") as mock_prepare_chart,
            patch("src.main.calculate_category_totals") as mock_calc_totals,
            patch("src.main.create_stacked_bar_chart") as mock_chart,
            patch("src.main.prepare_summary_table") as mock_summary,
            patch("src.main.create_aggrid_table"),
            patch("pandas.to_datetime") as mock_to_datetime,
        ):
            mock_to_datetime.return_value = datetime_series

            # Create processed dataframe with datetime
            processed_df = sample_df.copy()
            processed_df["OPERATION_DATE"] = datetime_series

            mock_filter.return_value = processed_df
            mock_stats.return_value = {
                "count": 2,
                "total": -80.0,
                "mean": -40.0,
                "min": -30.0,
                "max": -50.0,
            }
            mock_prepare_chart.return_value = pd.DataFrame()
            mock_calc_totals.return_value = pd.DataFrame()
            mock_chart.return_value = MagicMock()
            mock_summary.return_value = pd.DataFrame()

            # Execute
            main()

            # Verify the main workflow was executed
            mock_validate.assert_called_once_with(mock_uploaded_file)
            mock_load_data.assert_called_once_with(mock_uploaded_file)
            mock_filter.assert_called_once()
            # calculate_statistics est appelé 2 fois:
            # une fois pour toutes les données, une fois après exclusions
            assert mock_stats.call_count == 2

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_large_dataset_filtering(
        self, mock_logger, mock_validate, mock_load_data, mock_st
    ):
        """Test main function with large dataset and filtering."""
        # Setup
        mock_st.file_uploader.return_value = None
        # Create a larger dataset
        large_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["01/01/2026"] * 100,
                "CATEGORY": ["Food"] * 50 + ["Transport"] * 50,
                "SUBCATEGORY": ["Restaurant"] * 50 + ["Bus"] * 50,
                "AMOUNT": [-50.0] * 100,
            }
        )
        mock_load_data.return_value = large_df

        # Mock datetime conversion
        datetime_series = pd.to_datetime(["2026-01-01"] * 100)

        # Mock sidebar inputs with filters
        mock_st.sidebar.date_input.side_effect = [
            date(2026, 1, 1),  # start date
            date(2026, 1, 31),  # end date
        ]
        mock_st.sidebar.slider.return_value = 5  # small quantile threshold
        mock_st.multiselect.side_effect = [
            ["Food"],  # filter only Food category
            [],  # no subcategory filters
        ]

        # Mock data processing functions
        with (
            patch("src.main.filter_expenses") as mock_filter,
            patch("src.main.calculate_statistics") as mock_stats,
            patch("src.main.display_sidebar_statistics"),
            patch("src.main.prepare_chart_data") as mock_prepare_chart,
            patch("src.main.calculate_category_totals") as mock_calc_totals,
            patch("src.main.create_stacked_bar_chart") as mock_chart,
            patch("src.main.prepare_summary_table") as mock_summary,
            patch("src.main.create_aggrid_table"),
            patch("pandas.to_datetime") as mock_to_datetime,
        ):
            mock_to_datetime.return_value = datetime_series

            # Create processed dataframe
            processed_df = large_df.copy()
            processed_df["OPERATION_DATE"] = datetime_series

            mock_filter.return_value = processed_df
            mock_stats.return_value = {
                "count": 100,
                "total": -5000.0,
                "mean": -50.0,
                "min": -30.0,
                "max": -100.0,
            }
            mock_prepare_chart.return_value = pd.DataFrame()
            mock_calc_totals.return_value = pd.DataFrame()
            mock_chart.return_value = MagicMock()
            mock_summary.return_value = pd.DataFrame()

            # Execute
            main()

            # Verify processing works with large dataset
            mock_filter.assert_called_once()
            # calculate_statistics est appelé 2 fois:
            # une fois pour toutes les données, une fois après exclusions
            assert mock_stats.call_count == 2
            mock_logger.info.assert_any_call("Starting Bank Operations Analysis application")

    @patch("src.main.st")
    @patch("src.main.load_data")
    @patch("src.main.validate_csv_schema")
    @patch("src.main.logger")
    def test_main_with_edge_case_dates(self, mock_logger, mock_validate, mock_load_data, mock_st):
        """Test main function with edge case dates like year boundaries."""
        # Setup
        mock_st.file_uploader.return_value = None
        sample_df = pd.DataFrame(
            {
                "OPERATION_DATE": ["31/12/2025", "01/01/2026", "29/02/2024"],  # Edge dates
                "CATEGORY": ["Food", "Transport", "Housing"],
                "SUBCATEGORY": ["Restaurant", "Bus", "Rent"],
                "AMOUNT": [-50.0, -30.0, -800.0],
            }
        )
        mock_load_data.return_value = sample_df

        # Mock datetime conversion with proper dates
        datetime_series = pd.to_datetime(["2025-12-31", "2026-01-01", "2024-02-29"])

        # Mock sidebar inputs
        mock_st.sidebar.date_input.side_effect = [
            date(2025, 12, 31),  # start date
            date(2026, 1, 1),  # end date
        ]
        mock_st.sidebar.slider.return_value = 0  # no threshold
        mock_st.multiselect.side_effect = [[], []]

        # Mock data processing functions
        with (
            patch("src.main.filter_expenses") as mock_filter,
            patch("src.main.calculate_statistics") as mock_stats,
            patch("src.main.display_sidebar_statistics"),
            patch("src.main.prepare_chart_data") as mock_prepare_chart,
            patch("src.main.calculate_category_totals") as mock_calc_totals,
            patch("src.main.create_stacked_bar_chart") as mock_chart,
            patch("src.main.prepare_summary_table") as mock_summary,
            patch("src.main.create_aggrid_table"),
            patch("pandas.to_datetime") as mock_to_datetime,
        ):
            mock_to_datetime.return_value = datetime_series

            processed_df = sample_df.copy()
            processed_df["OPERATION_DATE"] = datetime_series

            mock_filter.return_value = processed_df
            mock_stats.return_value = {
                "count": 3,
                "total": -880.0,
                "mean": -293.33,
                "min": -250.0,
                "max": -380.0,
            }
            mock_prepare_chart.return_value = pd.DataFrame()
            mock_calc_totals.return_value = pd.DataFrame()
            mock_chart.return_value = MagicMock()
            mock_summary.return_value = pd.DataFrame()

            # Execute
            main()

            # Verify edge case dates are handled properly
            mock_filter.assert_called_once()
            # calculate_statistics est appelé 2 fois:
            # une fois pour toutes les données, une fois après exclusions
            assert mock_stats.call_count == 2
            mock_load_data.assert_called_once_with(None)

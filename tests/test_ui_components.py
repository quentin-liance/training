"""Unit tests for ui_components module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.ui_components import (
    create_aggrid_table,
    create_stacked_bar_chart,
    display_sidebar_statistics,
)


class TestDisplaySidebarStatistics:
    """Tests for display_sidebar_statistics function."""

    @patch("src.ui_components.st")
    def test_display_statistics_all_metrics(self, mock_st):
        """Test display of all statistics metrics."""
        stats = {"count": 42, "total": -1250.75, "mean": -29.78, "min": -5.50, "max": -150.25}

        # Execute
        display_sidebar_statistics(stats)

        # Verify sidebar elements are called
        mock_st.sidebar.markdown.assert_called_once_with("---")
        mock_st.sidebar.subheader.assert_called_once_with("📊 Statistiques")

        # Verify all metrics are displayed
        assert mock_st.sidebar.metric.call_count == 5

        # Check specific metric calls
        calls = mock_st.sidebar.metric.call_args_list
        assert calls[0][0] == ("Nombre d'opérations", 42)
        assert calls[1][0] == ("Total des dépenses", "-1251 €")
        assert calls[2][0] == ("Dépense moyenne", "-30 €")
        assert calls[3][0] == ("Dépense min", "-6 €")
        assert calls[4][0] == ("Dépense max", "-150 €")

    @patch("src.ui_components.st")
    def test_display_statistics_zero_values(self, mock_st):
        """Test display with zero values."""
        stats = {"count": 0, "total": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}

        # Execute
        display_sidebar_statistics(stats)

        # Verify zero values are handled correctly
        calls = mock_st.sidebar.metric.call_args_list
        assert calls[0][0] == ("Nombre d'opérations", 0)
        assert calls[1][0] == ("Total des dépenses", "0 €")
        assert calls[2][0] == ("Dépense moyenne", "0 €")
        assert calls[3][0] == ("Dépense min", "0 €")
        assert calls[4][0] == ("Dépense max", "0 €")

    @patch("src.ui_components.st")
    def test_display_statistics_positive_values(self, mock_st):
        """Test display with positive values (income)."""
        stats = {"count": 3, "total": 2500.50, "mean": 833.17, "min": 500.00, "max": 1200.00}

        # Execute
        display_sidebar_statistics(stats)

        # Verify positive values formatting
        calls = mock_st.sidebar.metric.call_args_list
        assert calls[1][0] == ("Total des dépenses", "2500 €")  # 2500.50 rounds to 2500
        assert calls[2][0] == ("Dépense moyenne", "833 €")


class TestCreateStackedBarChart:
    """Tests for create_stacked_bar_chart function."""

    @pytest.fixture
    def sample_cat_subcat_data(self):
        """Sample category-subcategory data."""
        return pd.DataFrame(
            {
                "CATEGORY": ["Food", "Food", "Transport", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Groceries", "Bus", "Fuel"],
                "AMOUNT_ABS": [150.0, 200.0, 50.0, 80.0],
            }
        )

    @pytest.fixture
    def sample_totals_data(self):
        """Sample category totals data."""
        return pd.DataFrame({"CATEGORY": ["Food", "Transport"], "TOTAL": [350.0, 130.0]})

    def test_create_chart_basic_structure(self, sample_cat_subcat_data, sample_totals_data):
        """Test basic chart creation and structure."""
        # Execute
        fig = create_stacked_bar_chart(sample_cat_subcat_data, sample_totals_data)

        # Verify figure is created - check if it's a plotly figure
        assert hasattr(fig, "data")  # Plotly figures have data attribute
        assert hasattr(fig, "layout")  # Plotly figures have layout attribute

        # Verify data is set correctly
        assert len(fig.data) == 4  # 4 subcategories = 4 traces

        # Check chart configuration
        layout = fig.layout
        assert "Répartition des Dépenses par Catégorie et Sous-catégorie" in layout.title.text
        assert layout.height == 550
        assert layout.xaxis.title.text == "<b>Catégorie</b>"
        assert layout.yaxis.title.text == "<b>Montant (€)</b>"

    def test_create_chart_with_annotations(self, sample_cat_subcat_data, sample_totals_data):
        """Test that annotations are added for totals."""
        # Execute
        fig = create_stacked_bar_chart(sample_cat_subcat_data, sample_totals_data)

        # Verify annotations are added (one for each category total)
        assert len(fig.layout.annotations) == 2

        # Check annotation content
        annotations = fig.layout.annotations
        annotation_texts = [ann.text for ann in annotations]
        assert "<b>350 €</b>" in annotation_texts
        assert "<b>130 €</b>" in annotation_texts

    def test_create_chart_color_sequence(self, sample_cat_subcat_data, sample_totals_data):
        """Test that color sequence is applied."""
        # Execute
        fig = create_stacked_bar_chart(sample_cat_subcat_data, sample_totals_data)

        # Check that traces have colors assigned
        for trace in fig.data:
            assert hasattr(trace, "marker")
            assert trace.marker.color is not None

    def test_create_chart_empty_data(self):
        """Test chart creation with empty data."""
        empty_cat_subcat = pd.DataFrame(columns=["CATEGORY", "SUBCATEGORY", "AMOUNT_ABS"])
        empty_totals = pd.DataFrame(columns=["CATEGORY", "TOTAL"])

        # Execute
        fig = create_stacked_bar_chart(empty_cat_subcat, empty_totals)

        # Verify figure is still created but with no data traces
        assert hasattr(fig, "data")  # Plotly figure
        assert hasattr(fig, "layout")  # Plotly figure
        assert len(fig.data) == 0
        assert len(fig.layout.annotations) == 0

    def test_create_chart_single_category(self):
        """Test chart creation with single category."""
        single_cat_data = pd.DataFrame(
            {"CATEGORY": ["Food"], "SUBCATEGORY": ["Restaurant"], "AMOUNT_ABS": [100.0]}
        )
        single_total = pd.DataFrame({"CATEGORY": ["Food"], "TOTAL": [100.0]})

        # Execute
        fig = create_stacked_bar_chart(single_cat_data, single_total)

        # Verify
        assert len(fig.data) == 1
        assert len(fig.layout.annotations) == 1
        assert "<b>100 €</b>" in fig.layout.annotations[0].text

    def test_create_chart_layout_configuration(self, sample_cat_subcat_data, sample_totals_data):
        """Test detailed layout configuration."""
        # Execute
        fig = create_stacked_bar_chart(sample_cat_subcat_data, sample_totals_data)

        layout = fig.layout

        # Test layout properties
        assert layout.plot_bgcolor == "rgba(0,0,0,0)"
        assert layout.paper_bgcolor == "rgba(0,0,0,0)"
        assert layout.title.x == 0.5
        assert layout.title.xanchor == "center"

        # Test legend configuration
        assert layout.legend.orientation == "v"
        assert layout.legend.title.text == "<b>Sous-catégorie</b>"

        # Test axis configuration
        assert layout.xaxis.categoryorder == "total descending"
        assert layout.yaxis.showgrid is True


class TestCreateAggridTable:
    """Tests for create_aggrid_table function."""

    @pytest.fixture
    def sample_summary_data(self):
        """Sample summary table data."""
        return pd.DataFrame(
            {
                "CATEGORY": ["Food", "Transport"],
                "SUBCATEGORY": ["Restaurant", "Bus"],
                "OPERATION_LABEL": ["Lunch", "Metro ticket"],
                "Total (€)": [-50.0, -30.0],
                "Subcategory Total (€)": [-150.0, -80.0],
                "Category Total (€)": [-300.0, -120.0],
                "Global Total (€)": [-420.0, -420.0],
                "Detail/Subcat Ratio (%)": [33.3, 37.5],
                "Subcat/Cat Ratio (%)": [50.0, 66.7],
                "Cat/Global Ratio (%)": [71.4, 28.6],
            }
        )

    @patch("src.ui_components.logger")
    @patch("src.ui_components.AgGrid")
    @patch("src.ui_components.GridOptionsBuilder")
    def test_create_table_basic_functionality(
        self, mock_grid_builder, mock_aggrid, mock_logger, sample_summary_data
    ):
        """Test basic table creation."""
        # Setup mocks
        mock_builder_instance = Mock()
        mock_grid_builder.from_dataframe.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = {"test": "options"}

        # Execute
        create_aggrid_table(sample_summary_data)

        # Verify logger is called
        mock_logger.debug.assert_called_once()
        log_message = mock_logger.debug.call_args[0][0]
        assert "Creating AG Grid table with 2 rows" in log_message

        # Verify GridOptionsBuilder is used
        mock_grid_builder.from_dataframe.assert_called_once_with(sample_summary_data)

        # Verify AgGrid is called
        mock_aggrid.assert_called_once()
        call_args = mock_aggrid.call_args
        assert call_args[0][0].equals(sample_summary_data)  # DataFrame argument
        assert call_args[1]["theme"] == "streamlit"
        assert call_args[1]["height"] == 500

    @patch("src.ui_components.logger")
    @patch("src.ui_components.AgGrid")
    @patch("src.ui_components.GridOptionsBuilder")
    def test_create_table_column_configuration(
        self, mock_grid_builder, mock_aggrid, mock_logger, sample_summary_data
    ):
        """Test column configuration."""
        # Setup mocks
        mock_builder_instance = Mock()
        mock_grid_builder.from_dataframe.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = {"test": "options"}

        # Execute
        create_aggrid_table(sample_summary_data)

        # Verify column configurations are called
        mock_builder_instance.configure_default_column.assert_called_once_with(
            filterable=True, sortable=True, resizable=True
        )

        # Check that specific columns are configured
        configure_calls = mock_builder_instance.configure_column.call_args_list

        # Verify CATEGORY column is pinned left
        category_call = next(call for call in configure_calls if call[0][0] == "CATEGORY")
        assert category_call[1]["pinned"] == "left"
        assert category_call[1]["header_name"] == "Catégorie"

        # Verify numeric columns have value formatters
        total_call = next(call for call in configure_calls if call[0][0] == "Total (€)")
        assert "valueFormatter" in total_call[1]

    @patch("src.ui_components.logger")
    @patch("src.ui_components.AgGrid")
    @patch("src.ui_components.GridOptionsBuilder")
    def test_create_table_pagination_sidebar(
        self, mock_grid_builder, mock_aggrid, mock_logger, sample_summary_data
    ):
        """Test pagination and sidebar configuration."""
        # Setup mocks
        mock_builder_instance = Mock()
        mock_grid_builder.from_dataframe.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = {"test": "options"}

        # Execute
        create_aggrid_table(sample_summary_data)

        # Verify pagination configuration
        mock_builder_instance.configure_pagination.assert_called_once_with(
            paginationAutoPageSize=False,
            paginationPageSize=25,  # PAGINATION_PAGE_SIZE
        )

        # Verify sidebar is configured
        mock_builder_instance.configure_side_bar.assert_called_once()

    @patch("src.ui_components.logger")
    @patch("src.ui_components.AgGrid")
    @patch("src.ui_components.GridOptionsBuilder")
    def test_create_table_empty_dataframe(self, mock_grid_builder, mock_aggrid, mock_logger):
        """Test table creation with empty DataFrame."""
        empty_df = pd.DataFrame(columns=["CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "Total (€)"])

        # Setup mocks
        mock_builder_instance = Mock()
        mock_grid_builder.from_dataframe.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = {"test": "options"}

        # Execute
        create_aggrid_table(empty_df)

        # Verify logger shows 0 rows
        mock_logger.debug.assert_called_once()
        log_message = mock_logger.debug.call_args[0][0]
        assert "Creating AG Grid table with 0 rows" in log_message

        # Verify AgGrid is still called
        mock_aggrid.assert_called_once()

    @patch("src.ui_components.logger")
    @patch("src.ui_components.AgGrid")
    @patch("src.ui_components.GridOptionsBuilder")
    def test_create_table_large_dataset(self, mock_grid_builder, mock_aggrid, mock_logger):
        """Test table creation with large dataset."""
        # Create a large DataFrame
        large_df = pd.DataFrame(
            {
                "CATEGORY": ["Food"] * 100,
                "SUBCATEGORY": ["Restaurant"] * 100,
                "OPERATION_LABEL": [f"Transaction {i}" for i in range(100)],
                "Total (€)": [-50.0] * 100,
            }
        )

        # Setup mocks
        mock_builder_instance = Mock()
        mock_grid_builder.from_dataframe.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = {"test": "options"}

        # Execute
        create_aggrid_table(large_df)

        # Verify logger shows correct row count
        mock_logger.debug.assert_called_once()
        log_message = mock_logger.debug.call_args[0][0]
        assert "Creating AG Grid table with 100 rows" in log_message

        # Verify pagination is used for large datasets
        mock_builder_instance.configure_pagination.assert_called_once()

"""Unit tests for config module."""

from pathlib import Path

from src.config import (
    COLUMNS_MAPPING,
    DATA_DIR,
    DECIMAL,
    DEFAULT_QUANTILE_THRESHOLD,
    ENCODING,
    OPERATIONS_FILE,
    PAGE_CONFIG,
    PAGINATION_PAGE_SIZE,
    PROJECT_ROOT,
    SEPARATOR,
)


class TestConfigPaths:
    """Tests for path configuration."""

    def test_project_root_is_path(self):
        """Test that PROJECT_ROOT is a Path object."""
        assert isinstance(PROJECT_ROOT, Path)

    def test_data_dir_is_path(self):
        """Test that DATA_DIR is a Path object."""
        assert isinstance(DATA_DIR, Path)

    def test_operations_file_is_path(self):
        """Test that OPERATIONS_FILE is a Path object."""
        assert isinstance(OPERATIONS_FILE, Path)

    def test_data_dir_relative_to_project_root(self):
        """Test that DATA_DIR is under PROJECT_ROOT."""
        assert str(DATA_DIR).startswith(str(PROJECT_ROOT))

    def test_operations_file_in_data_dir(self):
        """Test that OPERATIONS_FILE is in DATA_DIR."""
        assert str(OPERATIONS_FILE).startswith(str(DATA_DIR))


class TestCSVParameters:
    """Tests for CSV loading parameters."""

    def test_separator_is_string(self):
        """Test that SEPARATOR is a string."""
        assert isinstance(SEPARATOR, str)
        assert len(SEPARATOR) == 1

    def test_decimal_is_string(self):
        """Test that DECIMAL is a string."""
        assert isinstance(DECIMAL, str)
        assert len(DECIMAL) == 1

    def test_encoding_is_valid(self):
        """Test that ENCODING is a valid encoding name."""
        assert isinstance(ENCODING, str)
        # Test that encoding is valid by trying to encode/decode
        test_string = "Test"
        encoded = test_string.encode(ENCODING)
        decoded = encoded.decode(ENCODING)
        assert decoded == test_string


class TestColumnsMapping:
    """Tests for columns mapping."""

    def test_columns_mapping_is_dict(self):
        """Test that COLUMNS_MAPPING is a dictionary."""
        assert isinstance(COLUMNS_MAPPING, dict)

    def test_columns_mapping_not_empty(self):
        """Test that COLUMNS_MAPPING has entries."""
        assert len(COLUMNS_MAPPING) > 0

    def test_columns_mapping_keys_values_are_strings(self):
        """Test that all keys and values in COLUMNS_MAPPING are strings."""
        for key, value in COLUMNS_MAPPING.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_columns_mapping_has_required_columns(self):
        """Test that COLUMNS_MAPPING has required source columns."""
        required_source_columns = [
            "Categorie",
            "Sous categorie",
            "Libelle operation",
            "Debit",
            "Credit",
            "Date operation",
        ]
        for col in required_source_columns:
            assert col in COLUMNS_MAPPING

    def test_columns_mapping_target_uppercase(self):
        """Test that target column names are uppercase."""
        for value in COLUMNS_MAPPING.values():
            assert value.isupper() or "_" in value


class TestPageConfig:
    """Tests for Streamlit page configuration."""

    def test_page_config_is_dict(self):
        """Test that PAGE_CONFIG is a dictionary."""
        assert isinstance(PAGE_CONFIG, dict)

    def test_page_config_has_required_keys(self):
        """Test that PAGE_CONFIG has required keys."""
        required_keys = ["page_title", "page_icon", "layout", "initial_sidebar_state"]
        for key in required_keys:
            assert key in PAGE_CONFIG

    def test_page_title_is_string(self):
        """Test that page_title is a string."""
        assert isinstance(PAGE_CONFIG["page_title"], str)
        assert len(PAGE_CONFIG["page_title"]) > 0

    def test_layout_is_valid(self):
        """Test that layout is a valid Streamlit layout."""
        valid_layouts = ["centered", "wide"]
        assert PAGE_CONFIG["layout"] in valid_layouts

    def test_sidebar_state_is_valid(self):
        """Test that initial_sidebar_state is valid."""
        valid_states = ["auto", "expanded", "collapsed"]
        assert PAGE_CONFIG["initial_sidebar_state"] in valid_states


class TestDefaultParameters:
    """Tests for default parameters."""

    def test_default_quantile_threshold_is_int(self):
        """Test that DEFAULT_QUANTILE_THRESHOLD is an integer."""
        assert isinstance(DEFAULT_QUANTILE_THRESHOLD, int)

    def test_default_quantile_threshold_in_valid_range(self):
        """Test that DEFAULT_QUANTILE_THRESHOLD is in valid range."""
        assert 0 <= DEFAULT_QUANTILE_THRESHOLD <= 100

    def test_pagination_page_size_is_int(self):
        """Test that PAGINATION_PAGE_SIZE is an integer."""
        assert isinstance(PAGINATION_PAGE_SIZE, int)

    def test_pagination_page_size_is_positive(self):
        """Test that PAGINATION_PAGE_SIZE is positive."""
        assert PAGINATION_PAGE_SIZE > 0

"""Application configuration."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OPERATIONS_FILE = DATA_DIR / "20260101_20260201_operations.csv"

# CSV loading parameters
SEPARATOR = ";"
DECIMAL = ","
ENCODING = "utf-8"

# Column mapping
COLUMNS_MAPPING = {
    "Categorie": "CATEGORY",
    "Sous categorie": "SUBCATEGORY",
    "Libelle operation": "OPERATION_LABEL",
    "Debit": "DEBIT",
    "Credit": "CREDIT",
    "Date operation": "OPERATION_DATE",
}

# Streamlit configuration
PAGE_CONFIG = {
    "page_title": "Analyse des Opérations Bancaires",
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Default parameters
DEFAULT_QUANTILE_THRESHOLD = 10  # Percentage
PAGINATION_PAGE_SIZE = 25

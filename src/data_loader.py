"""Loading and processing of bank data."""

import pandas as pd
import streamlit as st
from loguru import logger

from src.config import (
    COLUMNS_MAPPING,
    DECIMAL,
    ENCODING,
    OPERATIONS_FILE,
    REQUIRED_CSV_COLUMNS,
    SEPARATOR,
)


def validate_csv_schema(uploaded_file) -> tuple[bool, str]:
    """Validate that uploaded CSV has the expected schema.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Read only the header to check columns
        df_header = pd.read_csv(
            uploaded_file,
            sep=SEPARATOR,
            encoding=ENCODING,
            nrows=0,  # Only read header
        )
        uploaded_file.seek(0)  # Reset file pointer for later reading

        uploaded_columns = list(df_header.columns)
        expected_columns = REQUIRED_CSV_COLUMNS

        # Check if columns match exactly
        if uploaded_columns != expected_columns:
            missing = set(expected_columns) - set(uploaded_columns)
            extra = set(uploaded_columns) - set(expected_columns)

            error_parts = []
            if missing:
                error_parts.append(f"Colonnes manquantes : {', '.join(sorted(missing))}")
            if extra:
                error_parts.append(f"Colonnes supplémentaires : {', '.join(sorted(extra))}")
            if set(uploaded_columns) == set(expected_columns):
                error_parts.append("L'ordre des colonnes ne correspond pas au schéma attendu")

            error_message = " | ".join(error_parts)
            logger.error(f"Schema validation failed: {error_message}")
            return False, error_message

        logger.info("CSV schema validation successful")
        return True, ""

    except Exception as e:
        error_message = f"Erreur lors de la validation : {str(e)}"
        logger.error(error_message)
        return False, error_message


@st.cache_data
def load_data(uploaded_file=None) -> pd.DataFrame:
    """Load and process bank operations data.

    Args:
        uploaded_file: Streamlit UploadedFile object or None to use default file

    Returns:
        DataFrame with normalized and aggregated columns
    """
    if uploaded_file is not None:
        logger.info(f"Loading data from uploaded file: {uploaded_file.name}")
        file_to_read = uploaded_file
    else:
        logger.info(f"Loading data from {OPERATIONS_FILE}")
        file_to_read = OPERATIONS_FILE

    df = (
        pd.read_csv(
            file_to_read,
            sep=SEPARATOR,
            decimal=DECIMAL,
            encoding=ENCODING,
        )
        .rename(columns=COLUMNS_MAPPING)
        .assign(AMOUNT=lambda df_: df_["DEBIT"].fillna(0) + df_["CREDIT"].fillna(0))
        .groupby(
            by=["CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "OPERATION_DATE"],
            as_index=False,
            dropna=False,
        )
        .agg({"AMOUNT": "sum"})
        .sort_values("CATEGORY", ascending=True)
    )
    logger.info(f"Data loaded successfully: {len(df)} operations")
    logger.debug(f"Columns: {list(df.columns)}")
    return df


@st.cache_data
def filter_expenses(df: pd.DataFrame, quantile_threshold: float = 0.10) -> pd.DataFrame:
    """Filter expenses and exclude extreme values.

    Args:
        df: DataFrame containing operations
        quantile_threshold: Quantile threshold to exclude extreme values (0 to 1)

    Returns:
        Filtered DataFrame with only expenses (negative amounts)
        and an AMOUNT_ABS column added
    """
    logger.info(f"Filtering expenses with quantile threshold: {quantile_threshold}")
    initial_count = len(df[df["AMOUNT"] < 0])

    df_negative = (
        df[df["AMOUNT"] < 0]
        .copy()
        .pipe(lambda df_: df_[df_["AMOUNT"] >= df_["AMOUNT"].quantile(quantile_threshold)])
        .sort_values("AMOUNT", ascending=True)
        .reset_index(drop=True)
    )
    df_negative["AMOUNT_ABS"] = df_negative["AMOUNT"].abs()

    excluded_count = initial_count - len(df_negative)
    logger.info(f"Expenses filtered: {len(df_negative)} kept, {excluded_count} excluded")
    return df_negative


def calculate_statistics(df: pd.DataFrame) -> dict:
    """Calculate descriptive statistics on expenses.

    Args:
        df: DataFrame containing expenses with AMOUNT_ABS column

    Returns:
        Dictionary with statistics (count, total, mean, min, max)
    """
    stats = {
        "count": len(df),
        "total": df["AMOUNT_ABS"].sum(),
        "mean": df["AMOUNT_ABS"].mean(),
        "min": df["AMOUNT_ABS"].min(),
        "max": df["AMOUNT_ABS"].max(),
    }
    logger.debug(f"Statistics calculated: total={stats['total']:.2f}€, mean={stats['mean']:.2f}€")
    return stats


def prepare_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare aggregated data for stacked bar chart.

    Args:
        df: DataFrame of filtered expenses

    Returns:
        DataFrame aggregated by category and subcategory
    """
    return df.groupby(["CATEGORY", "SUBCATEGORY"])["AMOUNT_ABS"].sum().reset_index()


def calculate_category_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate totals by category.

    Args:
        df: DataFrame of filtered expenses

    Returns:
        DataFrame with totals by category
    """
    totals = df.groupby("CATEGORY")["AMOUNT_ABS"].sum().reset_index()
    totals.columns = ["CATEGORY", "TOTAL"]
    return totals


def prepare_summary_table(df: pd.DataFrame, df_negative: pd.DataFrame) -> pd.DataFrame:
    """Prepare summary table with essential columns only.

    Args:
        df: DataFrame of filtered expenses (for calculations)
        df_negative: Complete DataFrame of expenses (not used but kept for compatibility)

    Returns:
        DataFrame with essential columns only
    """
    logger.info("Preparing summary table with essential columns")

    # Vérifier que le DataFrame n'est pas vide
    if df.empty:
        logger.warning("DataFrame is empty, returning empty summary table")
        return pd.DataFrame(
            columns=["Date", "CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "Total (€)"]
        )

    try:
        # Simple aggregation keeping essential information
        summary = (
            df.groupby(["CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "OPERATION_DATE"])
            .agg({"AMOUNT": "sum"})
            .round(2)
        )
        summary.columns = ["Total (€)"]
        summary = summary.reset_index()

        # Format date for display
        summary["Date"] = summary["OPERATION_DATE"].dt.strftime("%Y-%m-%d")

        # Keep only essential columns
        summary = summary[
            [
                "Date",
                "CATEGORY",
                "SUBCATEGORY",
                "OPERATION_LABEL",
                "Total (€)",
            ]
        ]

        logger.info(f"Summary table prepared: {len(summary)} rows")
        return summary

    except Exception as e:
        logger.error(f"Error preparing summary table: {e}")
        return pd.DataFrame(
            columns=["Date", "CATEGORY", "SUBCATEGORY", "OPERATION_LABEL", "Total (€)"]
        )


def prepare_category_month_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare pivot table with categories as rows and months as columns.

    Args:
        df: DataFrame of filtered expenses with OPERATION_DATE and CATEGORY

    Returns:
        DataFrame pivot table with categories (rows) and months (columns)
    """
    logger.info("Preparing category × month pivot table")

    # Vérifier que le DataFrame n'est pas vide
    if df.empty:
        logger.warning("DataFrame is empty, returning empty pivot table")
        return pd.DataFrame()

    try:
        # Créer une colonne pour le mois (format YYYY-MM)
        df_copy = df.copy()
        df_copy["Month"] = df_copy["OPERATION_DATE"].dt.to_period("M")

        # Créer le tableau croisé
        pivot = df_copy.pivot_table(
            values="AMOUNT",
            index="CATEGORY",
            columns="Month",
            aggfunc="sum",
            fill_value=0,
        )

        # Convertir les périodes en chaînes de caractères pour l'affichage
        pivot.columns = pivot.columns.astype(str)

        # Ajouter une colonne Total
        pivot["Total"] = pivot.sum(axis=1)

        # Trier par total décroissant
        pivot = pivot.sort_values("Total", ascending=False)

        logger.info(
            f"Pivot table prepared: {len(pivot)} categories × " f"{len(pivot.columns)-1} months"
        )
        return pivot

    except Exception as e:
        logger.error(f"Error preparing pivot table: {e}")
        return pd.DataFrame()

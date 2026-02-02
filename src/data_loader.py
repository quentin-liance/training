"""Loading and processing of bank data."""

import pandas as pd
import streamlit as st
from loguru import logger

from src.config import (
    COLUMNS_MAPPING,
    DECIMAL,
    ENCODING,
    OPERATIONS_FILE,
    SEPARATOR,
)


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
    """Prepare summary table with all ratios.

    Args:
        df: DataFrame of filtered expenses (for calculations)
        df_negative: Complete DataFrame of expenses (for global total)

    Returns:
        DataFrame with detailed columns and calculated ratios
    """
    logger.info("Preparing summary table with ratios")
    # Calculate totals and ratios
    summary = (
        df.groupby(["CATEGORY", "SUBCATEGORY", "OPERATION_LABEL"]).agg({"AMOUNT": "sum"}).round(2)
    )
    summary.columns = ["Total (€)"]
    summary = summary.reset_index()

    # Total by subcategory
    total_subcat = df.groupby(["CATEGORY", "SUBCATEGORY"])["AMOUNT"].sum().reset_index()
    total_subcat.columns = ["CATEGORY", "SUBCATEGORY", "Subcategory Total (€)"]

    # Total by category
    total_cat = df.groupby("CATEGORY")["AMOUNT"].sum().reset_index()
    total_cat.columns = ["CATEGORY", "Category Total (€)"]

    # Global total
    total_global = df_negative["AMOUNT"].sum()

    # Merge totals
    summary = summary.merge(total_subcat, on=["CATEGORY", "SUBCATEGORY"], how="left")
    summary = summary.merge(total_cat, on="CATEGORY", how="left")
    summary["Global Total (€)"] = total_global

    # Calculate ratios (in %)
    summary["Detail/Subcat Ratio (%)"] = (
        summary["Total (€)"] / summary["Subcategory Total (€)"] * 100
    ).round(1)
    summary["Subcat/Cat Ratio (%)"] = (
        summary["Subcategory Total (€)"] / summary["Category Total (€)"] * 100
    ).round(1)
    summary["Cat/Global Ratio (%)"] = (
        summary["Category Total (€)"] / summary["Global Total (€)"] * 100
    ).round(1)

    # Reorganize columns
    summary = summary[
        [
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
    ]

    logger.info(f"Summary table prepared: {len(summary)} rows")
    return summary

"""Utility functions for margin calculations."""

import pandas as pd


def calculate_totals(incomes_df: pd.DataFrame, costs_df: pd.DataFrame) -> dict[str, float]:
    """Calculate total income, costs, and net margin.

    Args:
        incomes_df: DataFrame with columns [Month, Category, Amount]
        costs_df: DataFrame with columns [Month, Category, Amount]

    Returns:
        Dictionary with total_income, total_costs, and net_margin

    Raises:
        ValueError: If required columns are missing
    """
    # Validate input DataFrames
    required_cols = ["Amount"]
    for col in required_cols:
        if col not in incomes_df.columns:
            raise ValueError(f"incomes_df missing required column: {col}")
        if col not in costs_df.columns:
            raise ValueError(f"costs_df missing required column: {col}")

    total_income = float(incomes_df["Amount"].sum()) if not incomes_df.empty else 0.0
    total_costs = float(costs_df["Amount"].sum()) if not costs_df.empty else 0.0
    net_margin = total_income - total_costs

    return {"total_income": total_income, "total_costs": total_costs, "net_margin": net_margin}


def calculate_margins(incomes_df: pd.DataFrame, costs_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate margin by month.

    Args:
        incomes_df: DataFrame with columns [Month, Category, Amount]
        costs_df: DataFrame with columns [Month, Category, Amount]

    Returns:
        DataFrame with columns [Month, Income, Costs, Margin, Margin %]

    Raises:
        ValueError: If required columns are missing
    """
    # Validate input DataFrames
    required_cols = ["Month", "Amount"]
    for col in required_cols:
        if col not in incomes_df.columns:
            raise ValueError(f"incomes_df missing required column: {col}")
        if col not in costs_df.columns:
            raise ValueError(f"costs_df missing required column: {col}")

    # Group by month
    income_by_month = incomes_df.groupby("Month")["Amount"].sum().reset_index()
    income_by_month.columns = ["Month", "Income"]

    costs_by_month = costs_df.groupby("Month")["Amount"].sum().reset_index()
    costs_by_month.columns = ["Month", "Costs"]

    # Merge and calculate margin
    margin_df = pd.merge(income_by_month, costs_by_month, on="Month", how="outer")
    margin_df = margin_df.fillna(0)  # Fill NaN values with 0
    margin_df["Margin"] = margin_df["Income"] - margin_df["Costs"]
    # Avoid division by zero
    margin_df["Margin %"] = margin_df.apply(
        lambda row: round((row["Margin"] / row["Income"] * 100), 2) if row["Income"] > 0 else 0.0,
        axis=1,
    )

    return margin_df


def calculate_margin_by_category(
    incomes_df: pd.DataFrame, costs_df: pd.DataFrame
) -> dict[str, dict[str, float]]:
    """Calculate margin breakdown by category.

    Args:
        incomes_df: DataFrame with columns [Category, Amount]
        costs_df: DataFrame with columns [Category, Amount]

    Returns:
        Dictionary with income_by_category and costs_by_category

    Raises:
        ValueError: If required columns are missing
    """
    # Validate input DataFrames
    if "Category" not in incomes_df.columns or "Amount" not in incomes_df.columns:
        raise ValueError("incomes_df missing required columns: Category or Amount")
    if "Category" not in costs_df.columns or "Amount" not in costs_df.columns:
        raise ValueError("costs_df missing required columns: Category or Amount")

    income_summary = incomes_df.groupby("Category")["Amount"].sum()
    cost_summary = costs_df.groupby("Category")["Amount"].sum()

    return {
        "income_by_category": income_summary.to_dict(),
        "costs_by_category": cost_summary.to_dict(),
    }

"""Utility functions for margin calculations."""

import pandas as pd


def calculate_totals(incomes_df, costs_df):
    """Calculate total income, costs, and net margin."""
    total_income = incomes_df["Amount"].sum()
    total_costs = costs_df["Amount"].sum()
    net_margin = total_income - total_costs

    return {"total_income": total_income, "total_costs": total_costs, "net_margin": net_margin}


def calculate_margins(incomes_df, costs_df):
    """Calculate margin by month."""
    # Group by month
    income_by_month = incomes_df.groupby("Month")["Amount"].sum().reset_index()
    income_by_month.columns = ["Month", "Income"]

    costs_by_month = costs_df.groupby("Month")["Amount"].sum().reset_index()
    costs_by_month.columns = ["Month", "Costs"]

    # Merge and calculate margin
    margin_df = pd.merge(income_by_month, costs_by_month, on="Month", how="outer")
    margin_df["Margin"] = margin_df["Income"] - margin_df["Costs"]
    margin_df["Margin %"] = (margin_df["Margin"] / margin_df["Income"] * 100).round(2)

    return margin_df


def calculate_margin_by_category(incomes_df, costs_df):
    """Calculate margin breakdown by category."""
    income_summary = incomes_df.groupby("Category")["Amount"].sum()
    cost_summary = costs_df.groupby("Category")["Amount"].sum()

    return {
        "income_by_category": income_summary.to_dict(),
        "costs_by_category": cost_summary.to_dict(),
    }

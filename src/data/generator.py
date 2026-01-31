"""Generate fake data for the margin analysis app."""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_fake_data():
    """Generate fake income and cost data for analysis."""

    # Generate months for the last 12 months
    end_date = datetime.now()
    months = [(end_date - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(11, -1, -1)]

    # Income categories and base amounts
    income_categories = {
        "Product Sales": (50000, 80000),
        "Service Revenue": (30000, 50000),
        "Consulting": (20000, 40000),
        "Subscriptions": (15000, 25000),
        "Licensing": (10000, 20000),
    }

    # Cost categories and base amounts
    cost_categories = {
        "Salaries": (40000, 45000),
        "Office Rent": (8000, 8500),
        "Marketing": (5000, 15000),
        "Software & Tools": (3000, 6000),
        "Utilities": (2000, 3000),
        "Travel": (1000, 5000),
        "Supplies": (1000, 3000),
        "Insurance": (2000, 2500),
    }

    # Generate income data
    income_data = []
    for month in months:
        for category, (min_amt, max_amt) in income_categories.items():
            # Add some randomness and trend
            trend_factor = 1 + (months.index(month) * 0.02)  # 2% growth per month
            amount = np.random.uniform(min_amt, max_amt) * trend_factor
            income_data.append(
                {"Month": month, "Category": category, "Amount": round(amount, 2), "Type": "Income"}
            )

    # Generate cost data
    cost_data = []
    for month in months:
        for category, (min_amt, max_amt) in cost_categories.items():
            # Add some randomness but less trend than income
            trend_factor = 1 + (months.index(month) * 0.01)  # 1% growth per month
            amount = np.random.uniform(min_amt, max_amt) * trend_factor
            cost_data.append(
                {"Month": month, "Category": category, "Amount": round(amount, 2), "Type": "Cost"}
            )

    incomes_df = pd.DataFrame(income_data)
    costs_df = pd.DataFrame(cost_data)

    return {"incomes": incomes_df, "costs": costs_df}

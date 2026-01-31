"""Streamlit app for company margin analysis."""

import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from loguru import logger

from src.data.generator import generate_fake_data
from src.utils.calculations import calculate_margins, calculate_totals

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

st.set_page_config(page_title="Company Margin Analyzer", page_icon="📊", layout="wide")

logger.info("Application started")

st.title("📊 Company Margin Analysis")
st.markdown("---")

# Generate fake data
logger.info("Generating fake data...")
data = generate_fake_data()
logger.debug(
    f"Generated {len(data['incomes'])} income records and {len(data['costs'])} cost records"
)

# Sidebar filters
st.sidebar.header("Filters")
selected_months = st.sidebar.multiselect(
    "Select Months",
    options=data["incomes"]["Month"].unique(),
    default=data["incomes"]["Month"].unique(),
)

selected_categories = st.sidebar.multiselect(
    "Select Income Categories",
    options=data["incomes"]["Category"].unique(),
    default=data["incomes"]["Category"].unique(),
)

logger.debug(
    f"Filters applied: {len(selected_months)} months, {len(selected_categories)} categories"
)

# Filter data
filtered_incomes = data["incomes"][
    (data["incomes"]["Month"].isin(selected_months))
    & (data["incomes"]["Category"].isin(selected_categories))
]
filtered_costs = data["costs"][data["costs"]["Month"].isin(selected_months)]

# Calculate metrics
logger.info("Calculating totals and margins...")
totals = calculate_totals(filtered_incomes, filtered_costs)
margin_data = calculate_margins(filtered_incomes, filtered_costs)
logger.debug(
    f"Calculations: income={totals['total_income']:.2f}, margin={totals['net_margin']:.2f}"
)

# Display KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Income", f"${totals['total_income']:,.2f}")
with col2:
    st.metric("Total Costs", f"${totals['total_costs']:,.2f}")
with col3:
    st.metric("Net Margin", f"${totals['net_margin']:,.2f}")
with col4:
    margin_pct = (
        (totals["net_margin"] / totals["total_income"] * 100) if totals["total_income"] > 0 else 0
    )
    st.metric("Margin %", f"{margin_pct:.1f}%")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💰 Incomes", "💸 Costs", "📊 Detailed Data"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Margin Trend")
        fig = px.line(
            margin_data,
            x="Month",
            y=["Income", "Costs", "Margin"],
            title="Income, Costs & Margin Over Time",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Income vs Costs Breakdown")
        breakdown_data = pd.DataFrame(
            {"Type": ["Income", "Costs"], "Amount": [totals["total_income"], totals["total_costs"]]}
        )
        fig = px.pie(
            breakdown_data,
            values="Amount",
            names="Type",
            color_discrete_sequence=["#2ecc71", "#e74c3c"],
        )
        st.plotly_chart(fig, width="stretch")

with tab2:
    st.subheader("💰 Detailed Income Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Income by category
        income_by_category = filtered_incomes.groupby("Category")["Amount"].sum().reset_index()
        fig = px.bar(
            income_by_category,
            x="Category",
            y="Amount",
            title="Income by Category",
            color="Amount",
            color_continuous_scale="Greens",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        # Income by month
        income_by_month = filtered_incomes.groupby("Month")["Amount"].sum().reset_index()
        fig = px.area(income_by_month, x="Month", y="Amount", title="Monthly Income Trend")
        st.plotly_chart(fig, width="stretch")

    # Detailed income table
    st.subheader("Income Details")
    st.dataframe(filtered_incomes.style.format({"Amount": "${:,.2f}"}), width="stretch")

with tab3:
    st.subheader("💸 Detailed Cost Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Costs by category
        costs_by_category = filtered_costs.groupby("Category")["Amount"].sum().reset_index()
        fig = px.bar(
            costs_by_category,
            x="Category",
            y="Amount",
            title="Costs by Category",
            color="Amount",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        # Costs by month
        costs_by_month = filtered_costs.groupby("Month")["Amount"].sum().reset_index()
        fig = px.area(
            costs_by_month,
            x="Month",
            y="Amount",
            title="Monthly Cost Trend",
            color_discrete_sequence=["#e74c3c"],
        )
        st.plotly_chart(fig, width="stretch")

    # Detailed costs table
    st.subheader("Cost Details")
    st.dataframe(filtered_costs.style.format({"Amount": "${:,.2f}"}), width="stretch")

with tab4:
    st.subheader("📊 Comprehensive Data View")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Income Data**")
        st.dataframe(filtered_incomes, width="stretch")

    with col2:
        st.write("**Cost Data**")
        st.dataframe(filtered_costs, width="stretch")

    # Download buttons
    st.subheader("Export Data")
    col1, col2 = st.columns(2)

    with col1:
        csv_income = filtered_incomes.to_csv(index=False)
        st.download_button(
            label="Download Income Data (CSV)",
            data=csv_income,
            file_name="income_data.csv",
            mime="text/csv",
        )

    with col2:
        csv_costs = filtered_costs.to_csv(index=False)
        st.download_button(
            label="Download Cost Data (CSV)",
            data=csv_costs,
            file_name="cost_data.csv",
            mime="text/csv",
        )

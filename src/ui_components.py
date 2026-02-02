"""UI components for the Streamlit application."""

import pandas as pd
import plotly.express as px
import streamlit as st
from loguru import logger
from st_aggrid import AgGrid, GridOptionsBuilder

from src.config import PAGINATION_PAGE_SIZE


def display_sidebar_statistics(stats: dict) -> None:
    """Display statistics in the sidebar.

    Args:
        stats: Dictionary containing statistics (count, total, mean, min, max)
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Statistics")
    st.sidebar.metric("Number of operations", stats["count"])
    st.sidebar.metric("Total expenses", f"{stats['total']:.0f} €")
    st.sidebar.metric("Average expense", f"{stats['mean']:.0f} €")
    st.sidebar.metric("Min expense", f"{stats['min']:.0f} €")
    st.sidebar.metric("Max expense", f"{stats['max']:.0f} €")


def create_stacked_bar_chart(cat_subcat: pd.DataFrame, totals_cat: pd.DataFrame) -> px.bar:
    """Create stacked bar chart.

    Args:
        cat_subcat: DataFrame aggregated by category and subcategory
        totals_cat: DataFrame with totals by category

    Returns:
        Plotly figure
    """
    fig = px.bar(
        cat_subcat,
        x="CATEGORY",
        y="AMOUNT_ABS",
        color="SUBCATEGORY",
        title="Distribution by Subcategory",
        labels={"AMOUNT_ABS": "Amount (€)", "CATEGORY": "Category"},
        text_auto=True,
    )
    fig.update_traces(texttemplate="%{y:.0f} €", textposition="inside")
    fig.update_layout(xaxis={"categoryorder": "total descending"}, height=500)

    # Add totals on bars
    for _, row in totals_cat.iterrows():
        fig.add_annotation(
            x=row["CATEGORY"],
            y=row["TOTAL"],
            text=f"{row['TOTAL']:.0f} €",
            showarrow=False,
            yshift=30,
            font={"size": 12, "color": "black", "family": "Arial Black"},
            bgcolor="rgba(255, 255, 255, 0.8)",
            borderpad=4,
        )

    return fig


def create_aggrid_table(summary: pd.DataFrame) -> None:
    """Create and display AG Grid table with configuration.

    Args:
        summary: DataFrame of summary table
    """
    logger.debug(f"Creating AG Grid table with {len(summary)} rows")
    gb_summary = GridOptionsBuilder.from_dataframe(summary)
    gb_summary.configure_default_column(filterable=True, sortable=True, resizable=True)
    gb_summary.configure_column("CATEGORY", header_name="Category", pinned="left", width=150)
    gb_summary.configure_column("SUBCATEGORY", header_name="Subcategory", width=150)
    gb_summary.configure_column("OPERATION_LABEL", header_name="Label", width=250)
    gb_summary.configure_column(
        "Total (€)", width=120, type=["numericColumn"], valueFormatter="value.toFixed(0) + ' €'"
    )
    gb_summary.configure_column(
        "Subcategory Total (€)",
        width=150,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' €'",
    )
    gb_summary.configure_column(
        "Category Total (€)",
        width=140,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' €'",
    )
    gb_summary.configure_column(
        "Global Total (€)",
        width=130,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' €'",
    )
    gb_summary.configure_column(
        "Detail/Subcat Ratio (%)",
        width=160,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' %'",
    )
    gb_summary.configure_column(
        "Subcat/Cat Ratio (%)",
        width=150,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' %'",
    )
    gb_summary.configure_column(
        "Cat/Global Ratio (%)",
        width=140,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' %'",
    )
    gb_summary.configure_pagination(
        paginationAutoPageSize=False, paginationPageSize=PAGINATION_PAGE_SIZE
    )
    gb_summary.configure_side_bar()

    grid_options = gb_summary.build()

    AgGrid(
        summary,
        gridOptions=grid_options,
        fit_columns_on_grid_load=False,
        theme="streamlit",
        height=500,
        allow_unsafe_jscode=True,
    )

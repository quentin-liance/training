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
    st.sidebar.subheader("📊 Statistiques")
    st.sidebar.metric("Nombre d'opérations", stats["count"])
    st.sidebar.metric("Total des dépenses", f"{stats['total']:.0f} €")
    st.sidebar.metric("Dépense moyenne", f"{stats['mean']:.0f} €")
    st.sidebar.metric("Dépense min", f"{stats['min']:.0f} €")
    st.sidebar.metric("Dépense max", f"{stats['max']:.0f} €")


def create_stacked_bar_chart(cat_subcat: pd.DataFrame, totals_cat: pd.DataFrame) -> px.bar:
    """Create stacked bar chart.

    Args:
        cat_subcat: DataFrame aggregated by category and subcategory
        totals_cat: DataFrame with totals by category

    Returns:
        Plotly figure
    """
    # Use a more pleasant color palette
    color_sequence = [
        "#FF6B6B",  # Red
        "#4ECDC4",  # Teal
        "#45B7D1",  # Blue
        "#FFA07A",  # Light salmon
        "#98D8C8",  # Mint
        "#F7DC6F",  # Yellow
        "#BB8FCE",  # Purple
        "#85C1E2",  # Sky blue
        "#F8B739",  # Orange
        "#52BE80",  # Green
    ]

    fig = px.bar(
        cat_subcat,
        x="CATEGORY",
        y="AMOUNT_ABS",
        color="SUBCATEGORY",
        title="<b>Répartition des Dépenses par Catégorie et Sous-catégorie</b>",
        labels={
            "AMOUNT_ABS": "Montant (€)",
            "CATEGORY": "Catégorie",
            "SUBCATEGORY": "Sous-catégorie",
        },
        text_auto=True,
        color_discrete_sequence=color_sequence,
    )

    # Update traces for better visuals
    fig.update_traces(
        texttemplate="%{y:.0f} €",
        textposition="inside",
        textfont={"size": 18, "color": "white", "family": "Arial"},
        marker={"line": {"color": "white", "width": 1}},  # Add white borders
        hovertemplate="<b>%{fullData.name}</b><br>Montant : %{y:.2f} €<extra></extra>",
    )

    # Enhanced layout
    fig.update_layout(
        xaxis={
            "categoryorder": "total descending",
            "title": {"text": "<b>Catégorie</b>", "font": {"size": 22}},
            "tickfont": {"size": 20},
            "showgrid": False,
        },
        yaxis={
            "title": {"text": "<b>Montant (€)</b>", "font": {"size": 22}},
            "tickfont": {"size": 18},
            "showgrid": True,
            "gridcolor": "rgba(128, 128, 128, 0.1)",
            "gridwidth": 1,
        },
        height=550,
        margin={"l": 70, "r": 50, "t": 80, "b": 70},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title={
            "font": {"size": 26, "color": "#2C3E50", "family": "Arial"},
            "x": 0.5,
            "xanchor": "center",
        },
        legend={
            "title": {"text": "<b>Sous-catégorie</b>", "font": {"size": 20}},
            "font": {"size": 17},
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02,
            "bgcolor": "rgba(255, 255, 255, 0.8)",
            "bordercolor": "#CCCCCC",
            "borderwidth": 1,
        },
        hoverlabel={
            "bgcolor": "white",
            "font_size": 16,
            "font_family": "Arial",
        },
    )

    # Add totals on bars with improved styling
    for _, row in totals_cat.iterrows():
        fig.add_annotation(
            x=row["CATEGORY"],
            y=row["TOTAL"],
            text=f"<b>{row['TOTAL']:.0f} €</b>",
            showarrow=False,
            yshift=35,
            font={"size": 20, "color": "#2C3E50", "family": "Arial Black"},
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#2C3E50",
            borderwidth=1.5,
            borderpad=6,
            opacity=0.95,
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
    gb_summary.configure_column("CATEGORY", header_name="Catégorie", pinned="left", width=150)
    gb_summary.configure_column("SUBCATEGORY", header_name="Sous-catégorie", width=150)
    gb_summary.configure_column("OPERATION_LABEL", header_name="Libellé", width=250)
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
    # Configuration de pagination robuste pour la production
    gb_summary.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=PAGINATION_PAGE_SIZE
    )
    gb_summary.configure_side_bar()

    # Options de grille avec pagination explicite
    grid_options = gb_summary.build()
    grid_options["pagination"] = True
    grid_options["paginationPageSize"] = PAGINATION_PAGE_SIZE
    grid_options["paginationNumberFormatter"] = None
    grid_options["suppressPaginationPanel"] = False

    AgGrid(
        summary,
        gridOptions=grid_options,
        fit_columns_on_grid_load=False,
        theme="streamlit",
        height=600,  # Hauteur augmentée pour mieux voir la pagination
        allow_unsafe_jscode=True,
        reload_data=False,
        update_mode="NO_UPDATE",
    )

"""UI components for the Streamlit application."""

import pandas as pd
import plotly.express as px
import streamlit as st
from loguru import logger
from st_aggrid import AgGrid, GridOptionsBuilder


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
        color_discrete_sequence=color_sequence,
    )

    # Update traces for better visuals
    fig.update_traces(
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
        showlegend=False,
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


def create_aggrid_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Create and display AG Grid table with configuration.

    Args:
        summary: DataFrame of summary table

    Returns:
        DataFrame with selected rows to exclude from analysis
    """
    logger.debug(f"Creating AG Grid table with {len(summary)} rows")

    # Vérifier que le summary n'est pas vide
    if summary.empty:
        st.error("⚠️ Aucune donnée à afficher dans le tableau")
        return pd.DataFrame()

    # Configuration AG Grid
    gb_summary = GridOptionsBuilder.from_dataframe(summary)

    # Configuration par défaut
    gb_summary.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        headerHeight=50,
    )

    # Configuration des colonnes essentielles uniquement
    gb_summary.configure_column(
        "Date",
        header_name="Date",
        pinned="left",
        width=120,
    )
    gb_summary.configure_column(
        "CATEGORY",
        header_name="Catégorie",
        pinned="left",
        width=200,
    )
    gb_summary.configure_column(
        "SUBCATEGORY",
        header_name="Sous-catégorie",
        width=220,
    )
    gb_summary.configure_column(
        "OPERATION_LABEL",
        header_name="Libellé de l'opération",
        width=400,
    )
    gb_summary.configure_column(
        "Total (€)",
        header_name="Montant (€)",
        width=150,
        type=["numericColumn"],
        valueFormatter="value.toFixed(0) + ' €'",
        cellStyle={"textAlign": "right"},
    )

    # Cacher la colonne de couleur
    gb_summary.configure_column("_row_color", hide=True)

    # Configuration pour afficher toutes les lignes sans restriction
    gb_summary.configure_side_bar()

    # Configuration de la sélection des lignes
    gb_summary.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
        groupSelectsChildren=False,
        groupSelectsFiltered=False,
    )

    # Affichage du nombre total de lignes
    st.markdown(f"**📊 Nombre total d'opérations : {len(summary)} - Toutes affichées**")
    st.markdown("✅ **Cochez les lignes que vous souhaitez exclure de l'analyse**")

    # Construction des options pour afficher TOUTES les données
    grid_options = gb_summary.build()

    # Configuration simplifiée pour éviter les conflits
    grid_options["pagination"] = False
    grid_options["rowSelection"] = "multiple"
    grid_options["suppressRowClickSelection"] = True  # Seulement checkbox pour sélection

    grid_response = AgGrid(
        summary,
        gridOptions=grid_options,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        height=600,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=False,
        update_mode="SELECTION_CHANGED",
        data_return_mode="FILTERED_AND_SORTED",
        custom_css={
            ".ag-header-cell-text": {
                "font-size": "16px !important",
                "font-weight": "bold !important",
                "color": "#2C3E50 !important",
            },
            ".ag-cell": {"font-size": "16px !important", "line-height": "40px !important"},
            ".ag-selection-checkbox": {"transform": "scale(1.2) !important"},
            ".ag-row-even": {
                "background-color": "#F8F8F8 !important",
            },
            ".ag-row-odd": {
                "background-color": "#FFFFFF !important",
            },
        },
    )

    # Récupération des lignes sélectionnées
    selected_rows = grid_response.get("selected_rows", [])

    # Vérification robuste si des lignes sont sélectionnées (éviter l'ambiguïté DataFrame)
    has_selection = False
    try:
        if isinstance(selected_rows, list):
            has_selection = len(selected_rows) > 0
        elif hasattr(selected_rows, "__len__"):
            has_selection = len(selected_rows) > 0
        else:
            has_selection = False
    except Exception:
        has_selection = False

    if has_selection:
        selected_df = pd.DataFrame(selected_rows)
        st.markdown(f"🚫 **{len(selected_rows)} opération(s) sélectionnée(s) pour exclusion**")

        # Affichage des lignes sélectionnées pour confirmation
        with st.expander(f"📋 Voir les {len(selected_rows)} opération(s) à exclure"):
            # Préparer les données à afficher avec seulement 3 colonnes
            display_columns = ["OPERATION_LABEL", "Total (€)", "Date"]
            selected_display = selected_df[display_columns].copy()

            # Renommer les colonnes pour l'export
            selected_display.columns = ["Libellé", "Montant (€)", "Date"]

            # Afficher le tableau
            st.dataframe(selected_display, use_container_width=True)

            # Préparer les données pour le presse-papier
            # Format TSV pour Excel avec virgule comme séparateur décimal
            clipboard_data = selected_display.to_csv(sep="\t", index=False, decimal=",")
            st.code(clipboard_data, language=None)

        return selected_df
    else:
        st.markdown("ℹ️ **Aucune opération sélectionnée pour exclusion**")
        return pd.DataFrame()

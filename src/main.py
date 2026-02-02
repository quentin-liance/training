"""Streamlit application for bank operations analysis."""

import pandas as pd
import streamlit as st

from src.config import DEFAULT_QUANTILE_THRESHOLD, PAGE_CONFIG
from src.data_loader import (
    calculate_category_totals,
    calculate_statistics,
    filter_expenses,
    load_data,
    prepare_chart_data,
    prepare_summary_table,
)
from src.logger import logger  # Initialize logger configuration
from src.ui_components import (
    create_aggrid_table,
    create_stacked_bar_chart,
    display_sidebar_statistics,
)


def main() -> None:
    """Main entry point of the application."""
    logger.info("Starting Bank Operations Analysis application")

    # Page configuration
    st.set_page_config(**PAGE_CONFIG)

    # Main title
    st.title("💰 Analyse des Opérations Bancaires")
    st.markdown("---")

    # File upload section
    uploaded_file = st.file_uploader(
        "📁 Importer un fichier CSV d'opérations bancaires",
        type=["csv"],
        help="Sélectionnez un fichier CSV contenant vos opérations bancaires",
    )

    # Load data with error handling
    try:
        df = load_data(uploaded_file)
        logger.debug(f"Data shape: {df.shape}")
    except FileNotFoundError:
        st.error(
            "⚠️ Le fichier de données par défaut est introuvable. Veuillez uploader un fichier CSV."
        )
        logger.error("Default data file not found")
        return
    except pd.errors.EmptyDataError:
        st.error("⚠️ Le fichier CSV est vide. Veuillez vérifier vos données.")
        logger.error("Empty CSV file provided")
        return
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des données : {str(e)}")
        logger.exception("Error loading data")
        return

    # Convert OPERATION_DATE to datetime (format DD/MM/YYYY in CSV)
    try:
        df["OPERATION_DATE"] = pd.to_datetime(
            df["OPERATION_DATE"], format="%d/%m/%Y", errors="coerce"
        )
    except Exception as e:
        st.warning(
            f"⚠️ Problème lors de la conversion des dates : {str(e)}. "
            "Certaines dates peuvent être invalides."
        )
        logger.warning(f"Date conversion issue: {e}")

    # Remove rows with invalid dates
    df = df.dropna(subset=["OPERATION_DATE"])

    # Check if we have valid dates
    if len(df) == 0:
        st.error("Aucune donnée avec des dates valides trouvée.")
        return

    # Sidebar - Filters
    st.sidebar.header("⚙️ Paramètres")

    # Date filters
    st.sidebar.subheader("📅 Filtres de Date")
    min_date = df["OPERATION_DATE"].min().date()
    max_date = df["OPERATION_DATE"].max().date()

    date_start = st.sidebar.date_input(
        "Date de début",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        help="Sélectionnez la date de début de la période",
    )

    date_end = st.sidebar.date_input(
        "Date de fin",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        help="Sélectionnez la date de fin de la période",
    )

    # Apply date filter
    df = df[
        (df["OPERATION_DATE"].dt.date >= date_start) & (df["OPERATION_DATE"].dt.date <= date_end)
    ]
    logger.info(f"Date filter applied: {date_start} to {date_end} ({len(df)} operations)")

    st.sidebar.markdown("---")

    quantile_threshold = (
        st.sidebar.slider(
            "Seuil d'exclusion des valeurs extrêmes (%)",
            min_value=0,
            max_value=20,
            value=DEFAULT_QUANTILE_THRESHOLD,
            step=1,
            help="Pourcentage des dépenses les plus élevées à exclure",
        )
        / 100
    )

    # Filter expenses
    logger.info(f"User selected quantile threshold: {quantile_threshold * 100}%")
    df_negative = filter_expenses(df, quantile_threshold)

    # General statistics in sidebar
    stats = calculate_statistics(df_negative)
    display_sidebar_statistics(stats)

    # Main section - Analysis by subcategory
    st.subheader("Analyse par Sous-catégorie")

    # Category multi-selection
    categories = sorted(df_negative["CATEGORY"].unique())
    selected_categories = st.multiselect(
        "Filtrer par catégories (laisser vide pour toutes)",
        options=categories,
        default=[],
        help="Sélectionnez une ou plusieurs catégories à afficher",
    )

    # Filter by selected categories
    if selected_categories:
        df_filtered = df_negative[df_negative["CATEGORY"].isin(selected_categories)]
        logger.info(
            f"Category filter applied: {len(selected_categories)} categories selected "
            f"({len(df_filtered)} operations)"
        )
    else:
        df_filtered = df_negative
        logger.info("Displaying all categories")

    # Subcategory multi-selection
    available_subcategories = sorted(df_filtered["SUBCATEGORY"].unique())
    selected_subcategories = st.multiselect(
        "Filtrer par sous-catégories (laisser vide pour toutes)",
        options=available_subcategories,
        default=[],
        help="Sélectionnez une ou plusieurs sous-catégories à afficher",
    )

    # Apply subcategory filter if any selected
    if selected_subcategories:
        df_filtered = df_filtered[df_filtered["SUBCATEGORY"].isin(selected_subcategories)]
        logger.info(
            f"Subcategory filter applied: {len(selected_subcategories)} subcategories "
            f"selected ({len(df_filtered)} operations)"
        )

    # Prepare data for chart
    cat_subcat = prepare_chart_data(df_filtered)
    totals_cat = calculate_category_totals(df_filtered)

    # Display stacked bar chart
    fig_stacked = create_stacked_bar_chart(cat_subcat, totals_cat)
    st.plotly_chart(fig_stacked, width="stretch")

    # Summary table
    st.subheader("Tableau Récapitulatif")
    summary = prepare_summary_table(df_filtered, df_negative)
    create_aggrid_table(summary)

    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Astuce**: Utilisez les filtres de la barre latérale pour explorer vos données !"
    )


if __name__ == "__main__":
    main()

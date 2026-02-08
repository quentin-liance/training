"""Streamlit application for bank operations analysis."""

import pandas as pd
import streamlit as st

from src.config import PAGE_CONFIG
from src.data_loader import (
    calculate_category_totals,
    calculate_statistics,
    filter_expenses,
    load_data,
    prepare_category_month_pivot,
    prepare_chart_data,
    prepare_summary_table,
    validate_csv_schema,
)
from src.logger import logger  # Initialize logger configuration
from src.monitoring import log_performance, metrics, setup_monitoring
from src.ui_components import (
    create_aggrid_table,
    create_stacked_bar_chart,
    display_category_month_table,
    display_sidebar_statistics,
)


@log_performance("main_application")
def main() -> None:
    """Main entry point of the application."""
    logger.info("Starting Bank Operations Analysis application")

    # Setup monitoring
    setup_monitoring()

    # Page configuration
    st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=PAGE_CONFIG["page_icon"],
        layout=PAGE_CONFIG["layout"],
        initial_sidebar_state=PAGE_CONFIG["initial_sidebar_state"],
    )

    # Main title
    st.title("💰 Analyse des Opérations Bancaires")
    st.markdown("---")

    # File upload section
    uploaded_file = st.file_uploader(
        "📁 Importer un fichier CSV d'opérations bancaires",
        type=["csv"],
        help="Sélectionnez un fichier CSV contenant vos opérations bancaires",
    )

    # Validate schema if file is uploaded
    if uploaded_file is not None:
        # Track file upload metrics
        metrics.increment_file_uploads(uploaded_file.name, uploaded_file.size)

        is_valid, error_message = validate_csv_schema(uploaded_file)
        if not is_valid:
            st.error(
                f"⚠️ **Le fichier uploadé ne correspond pas au schéma attendu.**\\n\\n"
                f"{error_message}\\n\\n"
                f"Veuillez utiliser un fichier avec la même structure que le fichier de référence."
            )
            logger.error(f"Schema validation failed for {uploaded_file.name}")
            return

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

    # Filter expenses without quantile threshold (show all expenses)
    logger.info("Processing all expenses without quantile exclusion")
    df_negative = filter_expenses(df, 0.0)  # 0.0 = no exclusion

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

    # Summary table with row selection (afficher en premier)
    st.subheader("Tableau Récapitulatif")
    summary = prepare_summary_table(df_filtered, df_negative)
    selected_for_exclusion = create_aggrid_table(summary)

    # Tableau catégories × mois
    st.markdown("---")
    st.subheader("📅 Dépenses par Catégorie et par Mois")
    pivot_table = prepare_category_month_pivot(df_filtered)
    if not pivot_table.empty:
        display_category_month_table(pivot_table)
    else:
        st.info("ℹ️ Aucune donnée disponible pour le tableau catégories × mois")

    # Calculer les données pour le graphique en fonction des exclusions
    if not selected_for_exclusion.empty and len(selected_for_exclusion) > 0:
        # Exclure les lignes sélectionnées
        excluded_labels = selected_for_exclusion["OPERATION_LABEL"].tolist()
        df_analysis = df_filtered[~df_filtered["OPERATION_LABEL"].isin(excluded_labels)]

        st.markdown(
            f"📊 **{len(df_analysis)} opérations analysées** "
            f"(exclu : {len(selected_for_exclusion)})"
        )

        if df_analysis.empty:
            st.warning("⚠️ Toutes les opérations ont été exclues de l'analyse!")
            return
    else:
        df_analysis = df_filtered
        st.markdown(f"📊 **{len(df_analysis)} opérations analysées** (aucune exclusion)")

    # Préparer et afficher LE graphique unique basé sur les données après exclusions
    cat_subcat = prepare_chart_data(df_analysis)
    totals_cat = calculate_category_totals(df_analysis)

    st.markdown("---")
    st.subheader("📊 Répartition des Dépenses")
    fig_stacked = create_stacked_bar_chart(cat_subcat, totals_cat)
    st.plotly_chart(fig_stacked, use_container_width=True)

    # Afficher les statistiques mises à jour dans la sidebar
    stats_updated = calculate_statistics(df_analysis)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Statistiques Finales")
    st.sidebar.metric("Opérations analysées", stats_updated["count"])
    st.sidebar.metric("Total", f"{stats_updated['total']:.0f} €")
    st.sidebar.metric("Moyenne", f"{stats_updated['mean']:.0f} €")
    st.sidebar.metric("Min", f"{stats_updated['min']:.0f} €")
    st.sidebar.metric("Max", f"{stats_updated['max']:.0f} €")

    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Astuce**: Utilisez les filtres de la barre latérale pour explorer vos données !"
    )


if __name__ == "__main__":
    main()

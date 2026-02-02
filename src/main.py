"""Streamlit application for bank operations analysis."""

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
    st.title("💰 Bank Operations Analysis")
    st.markdown("---")

    # Load data
    df = load_data()
    logger.debug(f"Data shape: {df.shape}")

    # Sidebar - Filters
    st.sidebar.header("⚙️ Settings")
    quantile_threshold = (
        st.sidebar.slider(
            "Extreme values exclusion threshold (%)",
            min_value=0,
            max_value=20,
            value=DEFAULT_QUANTILE_THRESHOLD,
            step=1,
            help="Percentage of highest expenses to exclude",
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
    st.subheader("Analysis by Subcategory")

    # Category selection
    categories = sorted(df_negative["CATEGORY"].unique())
    selected_cat = st.selectbox("Choose a category", ["All"] + categories)

    # Filter by selected category
    if selected_cat == "All":
        df_filtered = df_negative
        logger.info("Displaying all categories")
    else:
        df_filtered = df_negative[df_negative["CATEGORY"] == selected_cat]
        logger.info(f"Category filter applied: {selected_cat} ({len(df_filtered)} operations)")

    # Prepare data for chart
    cat_subcat = prepare_chart_data(df_filtered)
    totals_cat = calculate_category_totals(df_filtered)

    # Display stacked bar chart
    fig_stacked = create_stacked_bar_chart(cat_subcat, totals_cat)
    st.plotly_chart(fig_stacked, use_container_width=True)

    # Summary table
    st.subheader("Summary Table")
    summary = prepare_summary_table(df_filtered, df_negative)
    create_aggrid_table(summary)

    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip**: Use the filters in the sidebar to explore your data!")


if __name__ == "__main__":
    main()

"""
Application Streamlit pour l'analyse des opérations bancaires
Utilise AG Grid pour une visualisation interactive des données
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Opérations",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constantes
FICHIER_OPERATIONS = "20260101_20260201_operations.csv"
SEPARATEUR = ";"
DECIMALE = ","
ENCODAGE = "utf-8"

# Titre principal
st.title("💰 Analyse des Opérations Bancaires")
st.markdown("---")


@st.cache_data
def charger_donnees():
    """Charge et traite les données d'opérations"""
    df = (
        pd.read_csv(
            FICHIER_OPERATIONS,
            sep=SEPARATEUR,
            decimal=DECIMALE,
            encoding=ENCODAGE,
        )
        .rename(
            columns={
                "Categorie": "CATEGORIE",
                "Sous categorie": "SOUS_CATEGORIE",
                "Libelle operation": "LIBELLE_OPERATION",
                "Debit": "DEBIT",
                "Credit": "CREDIT",
                "Date operation": "DATE_OPERATION",
            }
        )
        .assign(MONTANT=lambda df_: df_["DEBIT"].fillna(0) + df_["CREDIT"].fillna(0))
        .groupby(
            by=["CATEGORIE", "SOUS_CATEGORIE", "LIBELLE_OPERATION", "DATE_OPERATION"],
            as_index=False,
            dropna=False,
        )
        .agg({"MONTANT": "sum"})
        .sort_values("CATEGORIE", ascending=True)
    )
    return df


@st.cache_data
def filtrer_depenses(df, quantile_seuil=0.10):
    """Filtre les dépenses et exclut les valeurs extrêmes"""
    df_negatif = (
        df[df["MONTANT"] < 0]
        .copy()
        .pipe(lambda df_: df_[df_["MONTANT"] >= df_["MONTANT"].quantile(quantile_seuil)])
        .sort_values("MONTANT", ascending=True)
        .reset_index(drop=True)
    )
    df_negatif["MONTANT_ABS"] = df_negatif["MONTANT"].abs()
    return df_negatif


# Chargement des données
df = charger_donnees()

# Sidebar - Filtres
st.sidebar.header("⚙️ Paramètres")
quantile_seuil = (
    st.sidebar.slider(
        "Seuil d'exclusion des valeurs extrêmes (%)",
        min_value=0,
        max_value=20,
        value=10,
        step=1,
        help="Pourcentage des dépenses les plus élevées à exclure",
    )
    / 100
)

df_negatif = filtrer_depenses(df, quantile_seuil)

# Statistiques générales
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Statistiques")
st.sidebar.metric("Nombre d'opérations", len(df_negatif))
st.sidebar.metric("Total dépenses", f"{df_negatif['MONTANT_ABS'].sum():.0f} €")
st.sidebar.metric("Dépense moyenne", f"{df_negatif['MONTANT_ABS'].mean():.0f} €")
st.sidebar.metric("Dépense min", f"{df_negatif['MONTANT_ABS'].min():.0f} €")
st.sidebar.metric("Dépense max", f"{df_negatif['MONTANT_ABS'].max():.0f} €")

# Analyse détaillée
st.subheader("Analyse par sous-catégorie")

# Sélection de catégorie
categories = sorted(df_negatif["CATEGORIE"].unique())
selected_cat = st.selectbox("Choisir une catégorie", ["Toutes"] + categories)

if selected_cat == "Toutes":
    df_filtered = df_negatif
else:
    df_filtered = df_negatif[df_negatif["CATEGORIE"] == selected_cat]

# Stacked bar
cat_sous_cat = (
    df_filtered.groupby(["CATEGORIE", "SOUS_CATEGORIE"])["MONTANT_ABS"].sum().reset_index()
)

# Calcul des totaux par catégorie pour affichage
totaux_cat = df_filtered.groupby("CATEGORIE")["MONTANT_ABS"].sum().reset_index()
totaux_cat.columns = ["CATEGORIE", "TOTAL"]

fig_stacked = px.bar(
    cat_sous_cat,
    x="CATEGORIE",
    y="MONTANT_ABS",
    color="SOUS_CATEGORIE",
    title="Répartition par sous-catégorie",
    labels={"MONTANT_ABS": "Montant (€)", "CATEGORIE": "Catégorie"},
    text_auto=True,
)
fig_stacked.update_traces(texttemplate="%{y:.0f} €", textposition="inside")
fig_stacked.update_layout(xaxis={"categoryorder": "total descending"}, height=500)

# Ajout des totaux sur les barres
for _, row in totaux_cat.iterrows():
    fig_stacked.add_annotation(
        x=row["CATEGORIE"],
        y=row["TOTAL"],
        text=f"{row['TOTAL']:.0f} €",
        showarrow=False,
        yshift=30,
        font={"size": 12, "color": "black", "family": "Arial Black"},
        bgcolor="rgba(255, 255, 255, 0.8)",
        borderpad=4,
    )

st.plotly_chart(fig_stacked, use_container_width=True)

# Tableau récapitulatif
st.subheader("Tableau récapitulatif")

# Calcul des totaux et ratios
summary = (
    df_filtered.groupby(["CATEGORIE", "SOUS_CATEGORIE", "LIBELLE_OPERATION"])
    .agg({"MONTANT": "sum"})
    .round(2)
)
summary.columns = ["Total (€)"]
summary = summary.reset_index()

# Total par sous-catégorie
total_sous_cat = df_filtered.groupby(["CATEGORIE", "SOUS_CATEGORIE"])["MONTANT"].sum().reset_index()
total_sous_cat.columns = ["CATEGORIE", "SOUS_CATEGORIE", "Total sous-catégorie (€)"]

# Total par catégorie
total_cat = df_filtered.groupby("CATEGORIE")["MONTANT"].sum().reset_index()
total_cat.columns = ["CATEGORIE", "Total catégorie (€)"]

# Total global (calculé sur toutes les dépenses, pas seulement la sélection)
total_global = df_negatif["MONTANT"].sum()

# Fusion des totaux
summary = summary.merge(total_sous_cat, on=["CATEGORIE", "SOUS_CATEGORIE"], how="left")
summary = summary.merge(total_cat, on="CATEGORIE", how="left")
summary["Total global (€)"] = total_global

# Calcul des ratios (en %)
summary["Ratio détail/sous-cat (%)"] = (
    summary["Total (€)"] / summary["Total sous-catégorie (€)"] * 100
).round(1)
summary["Ratio sous-cat/cat (%)"] = (
    summary["Total sous-catégorie (€)"] / summary["Total catégorie (€)"] * 100
).round(1)
summary["Ratio cat/global (%)"] = (
    summary["Total catégorie (€)"] / summary["Total global (€)"] * 100
).round(1)

# Réorganisation des colonnes pour rapprocher montants et ratios
summary = summary[
    [
        "CATEGORIE",
        "SOUS_CATEGORIE",
        "LIBELLE_OPERATION",
        "Total (€)",
        "Ratio détail/sous-cat (%)",
        "Total sous-catégorie (€)",
        "Ratio sous-cat/cat (%)",
        "Total catégorie (€)",
        "Ratio cat/global (%)",
        "Total global (€)",
    ]
]

# Configuration AG Grid pour le tableau récapitulatif
gb_summary = GridOptionsBuilder.from_dataframe(summary)
gb_summary.configure_default_column(filterable=True, sortable=True, resizable=True)
gb_summary.configure_column("CATEGORIE", header_name="Catégorie", pinned="left", width=150)
gb_summary.configure_column("SOUS_CATEGORIE", header_name="Sous-catégorie", width=150)
gb_summary.configure_column("LIBELLE_OPERATION", header_name="Libellé", width=250)
gb_summary.configure_column(
    "Total (€)", width=120, type=["numericColumn"], valueFormatter="value.toFixed(0) + ' €'"
)
gb_summary.configure_column(
    "Total sous-catégorie (€)",
    width=150,
    type=["numericColumn"],
    valueFormatter="value.toFixed(0) + ' €'",
)
gb_summary.configure_column(
    "Total catégorie (€)",
    width=140,
    type=["numericColumn"],
    valueFormatter="value.toFixed(0) + ' €'",
)
gb_summary.configure_column(
    "Total global (€)", width=130, type=["numericColumn"], valueFormatter="value.toFixed(0) + ' €'"
)
gb_summary.configure_column(
    "Ratio détail/sous-cat (%)",
    width=160,
    type=["numericColumn"],
    valueFormatter="value.toFixed(0) + ' %'",
)
gb_summary.configure_column(
    "Ratio sous-cat/cat (%)",
    width=150,
    type=["numericColumn"],
    valueFormatter="value.toFixed(0) + ' %'",
)
gb_summary.configure_column(
    "Ratio cat/global (%)",
    width=140,
    type=["numericColumn"],
    valueFormatter="value.toFixed(0) + ' %'",
)
gb_summary.configure_pagination(paginationAutoPageSize=False, paginationPageSize=25)
gb_summary.configure_side_bar()

grid_options_summary = gb_summary.build()

AgGrid(
    summary,
    gridOptions=grid_options_summary,
    fit_columns_on_grid_load=False,
    theme="streamlit",
    height=500,
    allow_unsafe_jscode=True,
)

# Footer
st.markdown("---")
st.markdown("💡 **Conseil** : Utilisez les filtres dans la sidebar pour explorer vos données !")

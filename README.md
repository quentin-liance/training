# Analyse des Opérations Bancaires

Application Streamlit pour l'analyse des opérations bancaires avec visualisation interactive via AG Grid.

## Fonctionnalités

- 📊 Tableau interactif des opérations avec AG Grid
- 💰 Analyse des dépenses par catégorie
- 📈 Graphiques et visualisations avec Plotly
- 🔍 Filtres personnalisables
- 📉 Exclusion des valeurs extrêmes (configurable)
- 💡 Statistiques en temps réel

## Installation

```bash
pip install -e .
```

## Lancement de l'application

```bash
streamlit run app.py
```

Ou utilisez le script fourni :
```bash
./run_app.sh
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`

## Structure du projet

```
├── app.py                        # Entrypoint (lance src/main.py)
├── src/                          # Code source modulaire
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # Application Streamlit principale
│   ├── config.py                  # Configuration et constantes
│   ├── data_loader.py             # Chargement et traitement des données
│   └── ui_components.py           # Composants d'interface utilisateur
├── data/                         # Données
│   └── 20260101_20260201_operations.csv
├── run_app.sh                    # Script de lancement
├── pyproject.toml                # Configuration et dépendances
└── README.md                     # Ce fichier
```

## Données

L'application analyse les données d'opérations bancaires à partir d'un fichier CSV contenant :
- Catégories et sous-catégories d'opérations
- Libellés détaillés
- Montants (débits et crédits)
- Dates d'opération

## Développement

Installation avec les dépendances de développement :
```bash
pip install -e ".[dev]"
```

### Architecture

Le projet suit une architecture modulaire stricte :
- **app.py** : Entrypoint minimal (convention pour Streamlit)
- **src/main.py** : Point d'entrée de l'application Streamlit
- **src/config.py** : Configuration centralisée (chemins, paramètres)
- **src/data_loader.py** : Fonctions de chargement et transformation des données
- **src/ui_components.py** : Composants réutilisables de l'interface

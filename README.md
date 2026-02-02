# Analyse des Opérations Bancaires

Application Streamlit pour l'analyse des opérations bancaires avec visualisation interactive via AG Grid.

## ✨ Fonctionnalités

- 📊 Tableau interactif des opérations avec AG Grid
- 💰 Analyse des dépenses par catégorie et sous-catégorie
- 📈 Graphiques empilés avec Plotly (design amélioré)
- 📅 Filtres de date personnalisables
- 🔍 Multi-sélection de catégories et sous-catégories
- 📉 Exclusion des valeurs extrêmes (configurable)
- 💡 Statistiques en temps réel
- 📁 Upload de fichiers CSV personnalisés
- 🪵 Logs structurés avec Loguru

## 🚀 Déploiement

### Streamlit Cloud (Recommandé)

1. **Créer un compte** sur [Streamlit Cloud](https://streamlit.io/cloud)

2. **Connecter votre dépôt GitHub**

3. **Configurer l'application** :
   - Main file path: `app.py`
   - Python version: 3.11+
   - Advanced settings: Aucune modification nécessaire

4. **Déployer** : L'application sera automatiquement déployée et accessible via une URL publique

### Autres plateformes

#### Heroku

```bash
# Ajouter un Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Déployer
git push heroku main
```

#### Docker

```bash
# Construire l'image
docker build -t bank-operations-analyzer .

# Lancer le conteneur
docker run -p 8501:8501 bank-operations-analyzer
```

## 📦 Installation locale

### Prérequis

- Python 3.11+
- pip ou uv

### Installation

```bash
# Cloner le dépôt
git clone <votre-repo>
cd bank-operations-analyzer

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Ou avec uv (plus rapide)
pip install uv
uv pip install -r requirements.txt
```

## 🎯 Lancement de l'application

```bash
streamlit run app.py
```

Ou utilisez le script fourni :
```bash
./run_app.sh
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`

## 📂 Structure du projet

```
├── app.py                        # Entrypoint (lance src/main.py)
├── requirements.txt              # Dépendances de production
├── src/                          # Code source modulaire
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Application Streamlit principale
│   ├── config.py                 # Configuration et constantes
│   ├── data_loader.py            # Chargement et traitement des données
│   ├── ui_components.py          # Composants d'interface utilisateur
│   └── logger.py                 # Configuration Loguru
├── data/                         # Données (optionnel avec upload)
│   └── 20260101_20260201_operations.csv
├── logs/                         # Logs de l'application
├── tests/                        # Tests unitaires
│   ├── conftest.py
│   ├── test_config.py
│   └── test_data_loader.py
├── .streamlit/
│   └── config.toml               # Configuration Streamlit
├── run_app.sh                    # Script de lancement
├── pyproject.toml                # Configuration et dépendances
└── README.md                     # Ce fichier
```

## 📊 Format des données

L'application attend un fichier CSV avec les colonnes suivantes :

| Colonne | Description | Format |
|---------|-------------|--------|
| `Date operation` | Date de l'opération | DD/MM/YYYY |
| `Categorie` | Catégorie principale | Texte |
| `Sous categorie` | Sous-catégorie | Texte |
| `Libelle operation` | Libellé détaillé | Texte |
| `Debit` | Montant débit | Décimal (virgule) |
| `Credit` | Montant crédit | Décimal (virgule) |

**Paramètres CSV attendus** :
- Séparateur : `;` (point-virgule)
- Décimale : `,` (virgule)
- Encodage : UTF-8

### Exemple de fichier CSV

```csv
Date operation;Categorie;Sous categorie;Libelle operation;Debit;Credit
31/01/2026;Alimentation;Restaurant;UBER EATS;-28,27;
29/01/2026;Revenus et rentrees d'argent;Salaires;VIR SEPA HACKAJOO;;+2953,15
```

## 🛠️ Développement

Installation avec les dépendances de développement :
```bash
pip install -e ".[dev]"
```

### Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=src --cov-report=html
```

### Linting et formatage

```bash
# Vérifier le code
ruff check .

# Formater automatiquement
ruff format .
```

### Pre-commit hooks

```bash
# Installer les hooks
pre-commit install

# Lancer manuellement
pre-commit run --all-files
```

## 🔒 Sécurité et bonnes pratiques

- ✅ Logs structurés avec rotation automatique
- ✅ Validation des dates et gestion des erreurs
- ✅ Limite d'upload : 200 MB
- ✅ Aucune donnée sensible dans le code
- ✅ Tests unitaires avec 90%+ de couverture

## 📝 License

Voir le fichier [LICENSE](LICENSE)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

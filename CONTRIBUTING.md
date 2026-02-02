# Guide de Contribution

Merci de votre intérêt pour contribuer au projet **Bank Operations Analyzer** ! 🎉

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Soumettre une contribution](#soumettre-une-contribution)

## 🤝 Code de conduite

En participant à ce projet, vous acceptez de respecter un environnement accueillant et inclusif pour tous.

## 💡 Comment contribuer

### Signaler un bug

Si vous trouvez un bug, créez une [issue](../../issues/new) avec :
- **Titre clair** : Description concise du problème
- **Description détaillée** : Étapes pour reproduire le bug
- **Comportement attendu** : Ce qui devrait se passer
- **Comportement actuel** : Ce qui se passe réellement
- **Environnement** : OS, version de Python, version de l'app
- **Logs** : Logs d'erreur pertinents (si disponibles)

### Proposer une fonctionnalité

Pour proposer une nouvelle fonctionnalité :
1. Vérifiez qu'elle n'existe pas déjà dans les [issues](../../issues)
2. Créez une nouvelle issue avec le tag `enhancement`
3. Décrivez clairement le besoin et la solution proposée
4. Discutez avec les mainteneurs avant de commencer le développement

### Améliorer la documentation

La documentation peut toujours être améliorée ! N'hésitez pas à :
- Corriger les fautes de frappe
- Clarifier les explications
- Ajouter des exemples
- Traduire en d'autres langues

## 🛠️ Configuration de l'environnement

### 1. Fork et clone

```bash
# Fork le projet sur GitHub, puis clonez votre fork
git clone https://github.com/VOTRE-USERNAME/bank-operations-analyzer.git
cd bank-operations-analyzer
```

### 2. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-du-bug
```

### 3. Installer les dépendances

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer avec pip
pip install -e ".[dev]"

# Ou avec uv (plus rapide)
pip install uv
uv pip install -e ".[dev]"
```

### 4. Configurer pre-commit

```bash
pre-commit install
```

## 📏 Standards de code

### Style de code

- **Python 3.11+** minimum
- **PEP 8** avec longueur de ligne max 100 caractères
- **Type hints** pour toutes les fonctions publiques
- **Docstrings** au format Google pour tous les modules, classes et fonctions

### Linting et formatage

Le projet utilise **Ruff** pour le linting et le formatage :

```bash
# Vérifier le code
ruff check .

# Formater automatiquement
ruff format .

# Type checking avec mypy
mypy src/
```

### Commits

Suivez les [Conventional Commits](https://www.conventionalcommits.org/) :

```
feat: ajouter filtre de recherche par texte
fix: corriger calcul des totaux
docs: mettre à jour le README
style: formater le code avec ruff
refactor: restructurer data_loader
test: ajouter tests pour ui_components
chore: mettre à jour les dépendances
```

### Structure des fichiers

```
src/
  ├── __init__.py           # Package initialization
  ├── config.py             # Configuration (constantes, chemins)
  ├── data_loader.py        # Logique de chargement/traitement des données
  ├── ui_components.py      # Composants d'interface réutilisables
  ├── main.py               # Application Streamlit principale
  └── logger.py             # Configuration Loguru

tests/
  ├── conftest.py           # Fixtures pytest
  ├── test_config.py        # Tests de configuration
  └── test_data_loader.py   # Tests de chargement de données
```

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests d'un fichier spécifique
pytest tests/test_data_loader.py -v

# Tests d'une fonction spécifique
pytest tests/test_data_loader.py::test_filter_expenses -v
```

### Écrire des tests

- **Couverture** : Visez au moins 80% de couverture
- **Fixtures** : Utilisez les fixtures dans `conftest.py`
- **Nommage** : `test_<fonction>_<scenario>`
- **Assertions** : Claires et spécifiques

Exemple :

```python
def test_filter_expenses_with_threshold(sample_expenses):
    """Test filtering expenses with specific quantile threshold."""
    result = filter_expenses(sample_expenses, quantile_threshold=0.1)

    assert len(result) < len(sample_expenses)
    assert all(result["AMOUNT"] < 0)
```

## 📤 Soumettre une contribution

### 1. Vérifier la qualité

```bash
# Pre-commit hooks
pre-commit run --all-files

# Tests
pytest --cov=src

# Linting
ruff check .
```

### 2. Commit et push

```bash
git add .
git commit -m "feat: description de ma contribution"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 3. Créer une Pull Request

1. Allez sur votre fork GitHub
2. Cliquez sur **"Compare & pull request"**
3. Remplissez le template de PR :
   - **Titre** : Description claire (format conventional commits)
   - **Description** : Détails de la modification
   - **Type** : Feature / Bug fix / Documentation / etc.
   - **Tests** : Comment tester la modification
   - **Checklist** : Cochez les cases appropriées

### Template de Pull Request

```markdown
## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Description
<!-- Décrivez clairement vos changements -->

## Tests
<!-- Comment tester cette modification ? -->

## Checklist
- [ ] Mon code suit les standards du projet
- [ ] J'ai ajouté/mis à jour les tests
- [ ] J'ai ajouté/mis à jour la documentation
- [ ] Tous les tests passent localement
- [ ] Pre-commit hooks passent
```

## 🔍 Revue de code

Les mainteneurs reviendront votre PR et pourront :
- Demander des modifications
- Poser des questions
- Approuver et merger

Soyez patient et réceptif aux commentaires. C'est un processus collaboratif ! 🤝

## 📞 Questions ?

N'hésitez pas à :
- Ouvrir une [issue](../../issues/new) pour poser une question
- Contacter les mainteneurs

Merci de contribuer à rendre ce projet meilleur ! 🚀

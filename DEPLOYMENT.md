# 🚀 Guide de Déploiement et Monitoring

## 📋 Table des matières
- [Déploiement](#deploiement)
- [Monitoring des logs](#monitoring)
- [Métriques et santé de l'application](#health)
- [Dépannage](#troubleshooting)

## 🚀 Déploiement

### Option 1: Streamlit Cloud (Recommandé)

1. **Préparation** ✅
   - Code pushé sur GitHub
   - `requirements.txt` à jour
   - Configuration Streamlit optimisée

2. **Déploiement**
   - Aller sur [share.streamlit.io](https://share.streamlit.io)
   - Se connecter avec GitHub
   - Créer une nouvelle app :
     ```
     Repository: quentin-liance/training
     Branch: master
     Main file path: app.py
     App URL: bank-operations-analyzer
     ```

3. **Configuration en production**
   - Les secrets peuvent être ajoutés via l'interface Streamlit Cloud
   - Les logs sont automatiquement gérés
   - Le monitoring est activé par défaut

### Option 2: Heroku

```bash
# Installer Heroku CLI
# Puis...
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
git add Procfile
git commit -m "Add Procfile for Heroku"
heroku create your-app-name
git push heroku master
```

### Option 3: Docker

```bash
# Créer Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
EOF

# Build et run
docker build -t bank-analyzer .
docker run -p 8501:8501 bank-analyzer
```

## 📊 Monitoring des logs

### Utilisation du script de monitoring

```bash
# Analyser les logs des 7 derniers jours
python scripts/monitor_logs.py analyze

# Monitoring en temps réel
python scripts/monitor_logs.py monitor

# Vérifier la santé de l'application
python scripts/monitor_logs.py health

# Analyser avec sortie JSON
python scripts/monitor_logs.py analyze --format json
```

### Types de logs surveillés

1. **Erreurs** 🔴
   - Erreurs de traitement des données
   - Problèmes de validation de schéma
   - Exceptions non gérées

2. **Avertissements** 🟡
   - Problèmes de performance
   - Fichiers de grande taille
   - Données manquantes

3. **Métriques** 📈
   - Temps de traitement des données
   - Nombre d'uploads de fichiers
   - Démarrages d'application

4. **Activités** 🟢
   - Sessions utilisateur
   - Fichiers traités
   - Opérations réussies

### Configuration des alertes

Pour configurer des alertes automatiques, vous pouvez :

1. **Utiliser un service de monitoring** comme:
   - [Better Stack](https://betterstack.com) (gratuit jusqu'à 10Go/mois)
   - [LogDNA](https://www.logdna.com)
   - [Datadog](https://www.datadoghq.com)

2. **Configuration avec webhooks Slack/Discord**:
   ```python
   # Ajouter dans src/monitoring.py
   import requests

   WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

   def send_alert(message):
       if error_count > threshold:
           requests.post(WEBHOOK_URL, json={"text": message})
   ```

## 🏥 Métriques et santé de l'application

### Métriques collectées automatiquement

```python
# Exemples de métriques disponibles
{
    "app_starts": 150,
    "files_uploaded": 45,
    "avg_processing_time": 2.3,
    "error_count": 2,
    "last_error": "2024-02-07 14:30:00"
}
```

### Health checks

Le système vérifie automatiquement :
- ✅ Utilisation mémoire (< 90%)
- ✅ Espace disque disponible (> 10%)
- ✅ Accessibilité du répertoire logs
- ✅ Performance de traitement des données

### Dashboard de métriques

Pour créer un dashboard personnalisé :

```python
# scripts/dashboard.py
import streamlit as st
from src.monitoring import metrics, HealthChecker

st.title("📊 Dashboard de Monitoring")

# Santé système
health = HealthChecker.check_system_health()
st.metric("Statut", health["status"])

# Métriques performance
perf = metrics.get_performance_summary()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Démarrages", perf["total_app_starts"])
with col2:
    st.metric("Uploads", perf["total_files_uploaded"])
with col3:
    st.metric("Temps moyen", f"{perf['avg_processing_time']:.1f}s")
```

## 🔧 Dépannage

### Problèmes courants

1. **Application lente**
   ```bash
   # Vérifier les temps de traitement
   python scripts/monitor_logs.py analyze | grep "processing_time"

   # Optimiser si nécessaire
   # - Réduire la taille des datasets
   # - Implémenter la mise en cache
   ```

2. **Erreurs fréquentes**
   ```bash
   # Analyser les erreurs
   python scripts/monitor_logs.py analyze | head -20

   # Vérifier les logs détaillés
   tail -f logs/app_$(date +%Y-%m-%d).log
   ```

3. **Problèmes de mémoire**
   ```bash
   # Surveiller l'utilisation
   python scripts/monitor_logs.py health

   # Nettoyer les logs anciens
   find logs/ -name "*.log" -mtime +30 -delete
   ```

### Commandes utiles

```bash
# Monitoring en continu
watch -n 10 "python scripts/monitor_logs.py health"

# Analyser les performances
python scripts/monitor_logs.py analyze --days 1

# Rotation manuelle des logs
gzip logs/app_$(date -d "yesterday" +%Y-%m-%d).log

# Vérifier l'espace disque
df -h logs/
```

### Support et maintenance

1. **Logs de rotation** : Les logs sont automatiquement compressés après 500MB
2. **Rétention** : 10 jours par défaut, configurable dans `src/logger.py`
3. **Alertes** : Configurez des seuils dans `src/monitoring.py`
4. **Backup** : Sauvegardez régulièrement le dossier `logs/`

---

## 📞 Support

- 📧 **Email** : [votre-email@domain.com]
- 🐛 **Issues** : [GitHub Issues](https://github.com/quentin-liance/training/issues)
- 📖 **Documentation** : [README.md](../README.md)

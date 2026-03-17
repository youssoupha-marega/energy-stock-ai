# EnergyStock AI ⚡

> **Pipeline MLOps de bout en bout pour prévoir les rendements à 5 jours des actions du secteur énergétique nord-américain**  
> Construit avec Kedro · MLflow · FastAPI · Evidently AI · Docker · GitHub Actions

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Kedro](https://img.shields.io/badge/Kedro-0.19-FFC900?style=flat&logo=kedro&logoColor=black)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=flat&logo=mlflow&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerisé-2496ED?style=flat&logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat&logo=githubactions&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-green?style=flat)

---

## Problématique métier

Les actions des entreprises énergétiques nord-américaines évoluent ensemble face aux chocs macroéconomiques — décisions de la Fed, prix du gaz naturel, vagues de chaleur, transitions réglementaires — mais **divergent sur les signaux spécifiques à chaque entreprise**.

Un analyste financier qui suit 20+ titres fait aujourd'hui ce travail manuellement : lire des rapports, surveiller les corrélations, sentir les tendances. C'est lent, partial et non reproductible.

**EnergyStock AI automatise cette extraction de signaux.**

> *Comment anticiper à 5 jours ouvrables le rendement d'une action énergétique (ex. NextEra Energy — NEE) en exploitant automatiquement les signaux de marché disponibles publiquement — corrélations sectorielles, indicateurs techniques, dynamique des volumes — pour aider un analyste à prioriser ses décisions d'investissement ?*

### Pourquoi un horizon de 5 jours ?

| Horizon | Problème |
|---|---|
| 1 jour | Bruit pur — l'hypothèse des marchés efficients tient fortement |
| **5 jours** ✅ | **Correspond à la fenêtre de rééquilibrage hebdomadaire des gestionnaires actifs** |
| 3 mois | Trop loin pour qu'un signal technique reste informatif |

### Pourquoi les corrélations sectorielles ?

L'analyse exploratoire démontre empiriquement une **corrélation > 0,6** entre NEE et 8+ actions pairs sur les rendements décalés de 5 jours. Ce signal transversal est l'avantage exploitable sur lequel ce projet se construit.

---

## Architecture de la solution

```
┌──────────────────────────────────────────────────────────────┐
│                        EnergyStock AI                        │
│                                                              │
│  Yahoo Finance ──► Pipelines Kedro ──► MLflow ──► FastAPI   │
│                          │                          │        │
│                    [Catalog Kedro]            [Prédictions]  │
│                          │                          │        │
│                    Evidently AI             Dashboard        │
│                  (Rapports de dérive)        Streamlit       │
└──────────────────────────────────────────────────────────────┘

CI/CD : GitHub Actions  ·  Infrastructure : Docker + AWS  ·  IaC : Terraform
```

### Stack technique — volontairement différenciant

| Couche | Outil | Pourquoi |
|---|---|---|
| Orchestration des pipelines | **Kedro** | Pipelines déclaratifs, catalog versionné, nœuds modulaires |
| Suivi des expériences | **MLflow** | Interface locale, comparaison automatique des runs, registre de modèles |
| Serving | **FastAPI + Docker** | API REST documentée, containerisée, prête pour le cloud |
| Monitoring de dérive | **Evidently AI** | Rapports HTML automatiques — rare dans les portfolios |
| CI/CD | **GitHub Actions** | Tests + lint + build Docker à chaque push |
| Dashboard | **Streamlit** | Démo live déployable sur Streamlit Cloud |

---

## Structure du projet

```
energystock-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml              # pytest + ruff lint sur chaque PR
│       └── docker.yml          # Build Docker à chaque merge sur main
│
├── conf/
│   ├── base/
│   │   ├── catalog.yml         # Toutes les sources de données déclarées ici
│   │   └── parameters.yml      # Hyperparamètres versionnés, jamais codés en dur
│   └── local/                  # Secrets — ignorés par Git
│
├── src/
│   └── energystock_ai/
│       ├── pipelines/
│       │   ├── ingestion/      # yfinance → Parquet (S3 ou local)
│       │   ├── features/       # Lags, SMA, EMA, RSI, volume, calendrier
│       │   └── training/       # Entraînement + MLflow + sélection du meilleur modèle
│       └── api/
│           └── main.py         # Endpoint de prédiction FastAPI
│
├── monitoring/
│   └── drift_report.py         # Evidently AI — détection de dérive des données
│
├── dashboard/
│   └── app.py                  # Dashboard Streamlit
│
├── tests/                      # Tests unitaires pytest
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Pipelines ML (Kedro)

Trois pipelines séquentiels, chacun exécutable et testable indépendamment :

### 1. Pipeline d'ingestion

Récupère les prix ajustés à la clôture de 18 entreprises énergétiques via Yahoo Finance (depuis 2000), détecte et supprime les titres avec trop de données manquantes, sauvegarde en Parquet via le catalog Kedro.

```bash
kedro run --pipeline ingestion
```

### 2. Pipeline de feature engineering

| Groupe de features | Détails |
|---|---|
| **Lags pairs sectoriels** | Rendements décalés de 5 jours des actions corrélées (corr > 0,6 avec NEE) |
| **Indicateurs techniques** | SMA et EMA aux fenêtres 5, 14, 30, 50, 200 — normalisés par le prix |
| **RSI** | Fenêtres 5, 14, 30, 50, 200 |
| **Dynamique des volumes** | Variation en % du volume + moyenne mobile sur 5 jours |
| **Features calendaires** | Variables indicatrices du jour de la semaine (effet lundi) |

```bash
kedro run --pipeline features
```

### 3. Pipeline d'entraînement

| Modèle | Notes |
|---|---|
| Régression linéaire | Référence — interprétable |
| Random Forest | Capture les interactions non linéaires entre pairs |
| LSTM | Apprend les patterns temporels sur la séquence |

```bash
kedro run --pipeline training
```

---

## Suivi des expériences (MLflow)

Chaque run est loggué automatiquement :

```
Run : NEE_RandomForest_2024-03-15
  ├── Paramètres : n_estimators=200, max_depth=10, lag_period=5
  ├── Métriques  : RMSE=0.0142, MAE=0.0098, R²=0.34
  ├── Artefacts  : model.pkl, feature_importance.png
  └── Tags       : stage=staging, ticker=NEE
```

```bash
mlflow ui  # → http://localhost:5000
```

---

## API de prédiction (FastAPI)

```bash
docker-compose up api
# → http://localhost:8000/docs
```

**POST** `/predict`
```json
{
  "ticker": "NEE",
  "as_of_date": "2024-03-15"
}
```
```json
{
  "ticker": "NEE",
  "rendement_predit_5j": 0.023,
  "signal": "haussier",
  "intervalle_confiance": [0.008, 0.038],
  "version_modele": "RandomForest_v3",
  "as_of_date": "2024-03-15"
}
```

---

## Monitoring de dérive (Evidently AI)

Génère un rapport HTML comparant la distribution actuelle des features à la distribution de référence — signale une dégradation potentielle du modèle avant qu'elle n'impacte les prédictions.

```bash
python monitoring/drift_report.py
# → monitoring/reports/drift_2024-03-15.html
```

---

## Démarrage rapide

### Prérequis

- Python 3.10+
- Docker & Docker Compose

### Installation locale

```bash
# Cloner le repo
git clone https://github.com/youssoupha-marega/Series_te.git
cd Series_te

# Installer les dépendances
pip install -r requirements.txt

# Exécuter le pipeline complet
kedro run

# Lancer l'interface MLflow
mlflow ui

# Démarrer l'API
docker-compose up api

# Lancer le dashboard
streamlit run dashboard/app.py
```

### Lancer les tests

```bash
pytest tests/ -v
```

---

## Hypothèses et limites

Ce projet est un **outil d'aide à la décision**, pas un robot de trading. Les limites sont énoncées explicitement :

- **Pas de prédiction du prix absolu** — uniquement des rendements relatifs à 5 jours, plus robuste statistiquement.
- **Pas de données alternatives** — pas de sentiment Twitter, pas d'analyse NLP des conférences de résultats. Périmètre V1 volontairement délimité.
- **Hypothèse des marchés efficients** — ce projet explore dans quelle mesure les corrélations sectorielles créent une inefficience exploitable à court terme.
- **Biais de survie** — la liste de titres reflète les entreprises actuellement cotées ; les sociétés radiées sont exclues.

---

## Feuille de route

- [x] Structure du projet Kedro
- [x] Feature engineering (lags, SMA/EMA/RSI, volume, calendrier)
- [x] Suivi des expériences MLflow
- [x] Endpoint de serving FastAPI
- [x] Containerisation Docker
- [x] CI/CD GitHub Actions
- [x] Monitoring de dérive Evidently AI
- [x] Dashboard Streamlit
- [ ] Support multi-tickers (DUK, SO, AEP)
- [ ] Déploiement AWS (ECR + App Runner)
- [ ] Infrastructure as Code Terraform
- [ ] Optimisation des hyperparamètres avec Optuna

---

## Données

| Source | Yahoo Finance (public) |
|---|---|
| Titres | 18 entreprises énergétiques nord-américaines |
| Historique | 2000-01-01 → présent |
| Fréquence | Quotidienne (clôture ajustée + volume) |
| Mise à jour | Automatisée quotidiennement via le pipeline |

Titres principaux : `NEE` `ETR` `DUK` `SO` `EXC` `AEP` `XEL` `ED` `PEG` `PPL` `FTS` `EIX` `AEE` `ES` `PNW` `CMS` `NRG` `FE`

---

## Auteur

**Youssoupha Marega**  
[GitHub](https://github.com/youssoupha-marega) · [LinkedIn](https://linkedin.com/in/youssoupha-marega)

---

## Licence

MIT — voir [LICENSE](LICENSE)

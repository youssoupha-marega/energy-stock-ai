# Kedro — Guide de démarrage

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Kedro](https://img.shields.io/badge/Kedro-0.19-yellow?logo=kedro)
![Status](https://img.shields.io/badge/status-documentation-lightgrey)

> Guide pas à pas pour créer un projet Kedro vide et configurer l'environnement de développement.

---

## Table des matières

- [Création du projet](#1-création-du-projet)
- [Structure générée](#2-structure-du-projet)
- [Kedro avec Jupyter](#3-kedro-avec-jupyter-notebooks)
- [Données d'exemple](#4-obtenir-les-données-dexemple)
- [Data Catalog](#5-configuration-du-data-catalog)
- [Tester l'environnement](#6-tester-lenvironnement)
- [Résumé des commandes](#7-résumé-des-commandes)

---

## 1. Création du projet

```bash
kedro new
```

Répondre aux questions interactives :

```
[New Kedro Project]: spaceflights

Which tools would you like to include? [none]: none
Would you like to include an example pipeline? [y/N]: n
```

> **Note** : `none` pour les outils et `n` pour le pipeline d'exemple permet de partir d'un projet totalement vide.

---

## 2. Structure du projet

```
spaceflights/
├── conf/
│   ├── base/
│   │   ├── catalog.yml          # définition des datasets
│   │   └── parameters.yml       # paramètres du projet
│   └── local/
│       └── credentials.yml      # secrets (non versionné)
├── data/
│   ├── 01_raw/
│   ├── 02_intermediate/
│   ├── 03_primary/
│   ├── 04_feature/
│   ├── 05_model_input/
│   ├── 06_models/
│   ├── 07_model_output/
│   └── 08_reporting/
├── notebooks/
├── src/
│   └── spaceflights/
│       ├── pipeline_registry.py
│       ├── settings.py
│       └── pipelines/
├── pyproject.toml
└── requirements.txt
```

> **Important** : Toujours se positionner à la racine du projet avant d'exécuter des commandes Kedro.

```bash
cd spaceflights
```

---

## 3. Kedro avec Jupyter Notebooks

### Prérequis

> ⚠️ L'extension `kedro.ipython` est incompatible avec Python 3.13+. Utiliser Python 3.10, 3.11 ou 3.12.

Charger l'extension dans un notebook :

```python
%load_ext kedro.ipython
```

Cela expose trois objets globaux :

| Objet | Description |
|---|---|
| `context` | Accès aux paramètres et à la configuration du projet |
| `catalog` | Chargement / sauvegarde des datasets déclarés dans `catalog.yml` |
| `pipelines` | Pipelines enregistrés dans `pipeline_registry.py` |

---

## 4. Obtenir les données d'exemple

Les fichiers nécessaires pour le projet `spaceflights` sont : `companies.csv`, `reviews.csv`, `shuttles.xlsx`.

Les générer via le starter officiel :

```bash
kedro new --starter=spaceflights-pandas
```

Puis copier les fichiers dans le projet courant :

```
spaceflights-pandas/data/01_raw/companies.csv   →   spaceflights/data/01_raw/
spaceflights-pandas/data/01_raw/reviews.csv     →   spaceflights/data/01_raw/
spaceflights-pandas/data/01_raw/shuttles.xlsx   →   spaceflights/data/01_raw/
```

---

## 5. Configuration du Data Catalog

Modifier `conf/base/catalog.yml` (vide par défaut) :

```yaml
companies:
  type: pandas.CSVDataset
  filepath: data/01_raw/companies.csv

reviews:
  type: pandas.CSVDataset
  filepath: data/01_raw/reviews.csv

shuttles:
  type: pandas.ExcelDataset
  filepath: data/01_raw/shuttles.xlsx
  load_args:
    engine: openpyxl
```

### Types de datasets courants

| Type Kedro | Format | Usage |
|---|---|---|
| `pandas.CSVDataset` | `.csv` | Données tabulaires brutes |
| `pandas.ParquetDataset` | `.parquet` | Données intermédiaires optimisées |
| `pandas.ExcelDataset` | `.xlsx` | Fichiers Excel |
| `pickle.PickleDataset` | `.pkl` | Modèles ML, objets Python |
| `json.JSONDataset` | `.json` | Configurations, métadonnées |

---

## 6. Tester l'environnement

Dans un notebook Kedro :

```python
# Vérifier le contexte
context

# Lister les datasets disponibles
catalog.list()

# Charger un dataset
df = catalog.load("companies")
df.head()

# Afficher les pipelines enregistrés
pipelines
```

Si les trois objets retournent des valeurs valides sans erreur, l'environnement est correctement configuré.

---

## 7. Résumé des commandes

```bash
# Créer le projet
kedro new

# Se positionner dans le projet
cd spaceflights

# Lancer Jupyter avec Kedro
kedro jupyter notebook

# Exécuter le pipeline par défaut
kedro run

# Visualiser le DAG (nécessite kedro-viz)
kedro viz run
```

---

## Références

- [Documentation officielle Kedro](https://docs.kedro.org/en/stable/)
- [Tutoriel YouTube — Playlist Kedro](https://www.youtube.com/watch?v=3YeE_gvDCvw&list=PL-JJgymPjK5LddZXbIzp9LWurkLGgB-nY&index=11)

# Kedro — Création d'un pipeline de données

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Kedro](https://img.shields.io/badge/Kedro-0.19-yellow?logo=kedro)
![Parquet](https://img.shields.io/badge/Format-Parquet-orange)
![Status](https://img.shields.io/badge/status-documentation-lightgrey)

> Création, assemblage, exécution et visualisation d'un pipeline `data_processing` dans le projet `spaceflights`.

---

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Partie 1 — Créer le pipeline](#partie-1--créer-le-pipeline)
- [Partie 2 — Assembler les nodes](#partie-2--assembler-les-nodes)
- [Partie 3 — Persister les résultats](#partie-3--persister-les-résultats)
- [Partie 4 — Visualiser le DAG](#partie-4--visualiser-le-dag)
- [Résumé des commandes](#résumé-des-commandes)

---

## Vue d'ensemble

| Partie | Titre | Commande clé |
|---|---|---|
| 1 | Création du pipeline | `kedro pipeline create data_processing` |
| 2 | Assemblage des nodes | Écrire `pipeline.py` et `nodes.py` |
| 3 | Stockage des résultats | Mettre à jour `catalog.yml` |
| 4 | Visualisation | `kedro viz` |

---

## Partie 1 — Créer le pipeline

### Prérequis

```bash
cd spaceflights
```

### Commande

```bash
kedro pipeline create data_processing
```

### Fichiers générés

```
src/spaceflights/pipelines/
└── data_processing/               ← nouveau dossier
    ├── nodes.py                   ← fonctions de transformation
    ├── pipeline.py                ← assemblage des nodes
    └── __init__.py

conf/base/
└── parameters_data_processing.yml ← paramètres dédiés au pipeline

tests/pipelines/
└── data_processing/
    └── test_pipeline.py           ← tests unitaires générés
```

| Fichier | Rôle |
|---|---|
| `nodes.py` | Contient les fonctions Python de transformation — **ce que je fais aux données** |
| `pipeline.py` | Assemble les fonctions en nodes — **dans quel ordre j'exécute ces traitements** |
| `parameters_data_processing.yml` | Paramètres spécifiques à ce pipeline |
| `test_pipeline.py` | Tests unitaires générés automatiquement |

### Formater le code

```bash
black src\spaceflights
```

```
All done! ✨ 🍰 ✨
4 files reformatted, 4 files left unchanged.
```

---

## Partie 2 — Assembler les nodes

### Concept

Un **node** est un mapping entre une fonction Python et ses inputs/outputs nommés.

```
"companies" (catalog)  →  preprocess_companies()  →  "preprocessed_companies" (catalog)
```

### Modifier `pipeline.py`

`src/spaceflights/pipelines/data_processing/pipeline.py`

```python
from kedro.pipeline import Node, Pipeline, node  # noqa
from .nodes import preprocess_companies, preprocess_shuttles  # noqa


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                func=preprocess_companies,
                inputs="companies",
                outputs="preprocessed_companies",
                name="preprocess_companies_node",
            ),
            Node(
                func=preprocess_shuttles,
                inputs="shuttles",
                outputs="preprocessed_shuttles",
                name="preprocess_shuttles_node",
            ),
        ]
    )
```

| Paramètre | Description |
|---|---|
| `func` | Fonction Python à exécuter (définie dans `nodes.py`) |
| `inputs` | Nom du dataset d'entrée tel que déclaré dans `catalog.yml` |
| `outputs` | Nom du dataset de sortie |
| `name` | Identifiant unique du node — utile pour le débogage et le filtrage |

### Vérifier le registre

```bash
kedro registry list
```

```
- __default__
- data_processing
```

### Exécuter le pipeline

```bash
kedro run --pipeline data_processing
```

```
INFO     Loading data from companies (CSVDataset)...
INFO     Running node: preprocess_companies_node
INFO     Saving data to preprocessed_companies (MemoryDataset)...
INFO     Completed 1 out of 2 tasks
INFO     Loading data from shuttles (ExcelDataset)...
INFO     Running node: preprocess_shuttles_node
INFO     Saving data to preprocessed_shuttles (MemoryDataset)...
INFO     Completed 2 out of 2 tasks
INFO     Pipeline execution completed successfully in 2.5 sec.
```

> **Note** : À cette étape, les outputs sont gérés en `MemoryDataset` — ils existent pendant le run mais **ne sont pas sauvegardés sur disque**. Ils sont perdus à la fin de l'exécution. Cette étape sert à valider la logique de transformation avant de configurer le stockage.

---

## Partie 3 — Persister les résultats

### Mettre à jour `catalog.yml`

Ajouter dans `conf/base/catalog.yml` :

```yaml
preprocessed_companies:
  type: pandas.ParquetDataset
  filepath: data/02_intermediate/preprocessed_companies.pq

preprocessed_shuttles:
  type: pandas.ParquetDataset
  filepath: data/02_intermediate/preprocessed_shuttles.pq
```

### Pourquoi Parquet ?

| Critère | CSV | Parquet |
|---|---|---|
| Performance lecture | Lente | Rapide (colonnes compressées) |
| Taille sur disque | Grande | Petite (compression efficace) |
| Préservation des types | Non (tout est string) | Oui (types natifs conservés) |
| Usage recommandé | `01_raw/` | `02_intermediate/` et au-delà |

### Ré-exécuter avec persistance

```bash
kedro run --pipeline data_processing
```

Le log affiche maintenant `ParquetDataset` au lieu de `MemoryDataset`, confirmant que les fichiers `.pq` sont écrits dans `data/02_intermediate/`.

---

## Partie 4 — Visualiser le DAG

```bash
# Installer Kedro Viz
pip install kedro-viz

# Lancer la visualisation
kedro viz
```

Ouvre automatiquement `http://localhost:4141` avec le graphe interactif du pipeline.

Ce que l'on peut voir :
- Les **nodes** (fonctions) représentés comme des rectangles
- Les **datasets** (inputs/outputs) représentés comme des cercles
- Les **connexions** montrant le flux de données
- Les métadonnées de chaque node au clic

---

## Résumé des commandes

```bash
# 1. Se positionner dans le projet
cd spaceflights

# 2. Créer le pipeline
kedro pipeline create data_processing

# 3. Écrire les fonctions dans nodes.py
#    src/spaceflights/pipelines/data_processing/nodes.py

# 4. Assembler les nodes dans pipeline.py
#    src/spaceflights/pipelines/data_processing/pipeline.py

# 5. Formater le code
black src\spaceflights

# 6. Vérifier l'enregistrement
kedro registry list

# 7. Exécuter (test sans persistence)
kedro run --pipeline data_processing

# 8. Déclarer les outputs dans catalog.yml
#    conf/base/catalog.yml

# 9. Ré-exécuter avec persistence
kedro run --pipeline data_processing

# 10. Visualiser le DAG
kedro viz
```

---

## Références

- [Documentation officielle — Create a pipeline](https://docs.kedro.org/en/stable/tutorials/create_a_pipeline/)
- [Tutoriel YouTube — Partie 2](https://www.youtube.com/watch?v=P__gFG1TmMo&list=PL-JJgymPjK5LddZXbIzp9LWurkLGgB-nY&index=12)

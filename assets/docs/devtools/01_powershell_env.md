# PowerShell — Environnement de développement Python

![OS](https://img.shields.io/badge/OS-Windows-blue?logo=windows&logoColor=white)
![Shell](https://img.shields.io/badge/Shell-PowerShell-5391FE?logo=powershell&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-documentation-lightgrey)

> Commandes PowerShell du quotidien pour gérer les versions Python, les environnements virtuels et les dépendances dans le cadre du projet `energystock-ai`.

---

## Table des matières

- [Versions Python](#1-gestion-des-versions-python)
- [Environnements virtuels](#2-environnements-virtuels)
- [Gestion des paquets](#3-gestion-des-paquets-pip)
- [Navigation et fichiers](#4-navigation-et-exploration-de-fichiers)
- [Tableau récapitulatif](#5-tableau-récapitulatif)
- [Workflow complet](#6-workflow-complet)

---

## 1. Gestion des versions Python

```powershell
# Lister toutes les versions Python installées avec leur chemin
py -0p

# Vérifier la version Python active dans l'environnement courant
python --version
```

> `py` est le Python Launcher Windows — il permet de gérer plusieurs versions côte à côte.

---

## 2. Environnements virtuels

### Créer un environnement virtuel

```powershell
# Avec la version Python par défaut
python -m venv energy-stock-ai-3.12.2.venv

# Avec une version Python spécifique
py -3.12 -m venv energy-stock-ai-3.12.venv
```

> **Astuce** : inclure la version dans le nom du venv (ex: `mon-projet-3.12.venv`) facilite l'identification rapide.

### Activer l'environnement

```powershell
& "C:\Users\ymarega\OneDrive - NORDIKeau\Bureau\Personnel\Data & IA\Projets perso\energystock-ai\energy-stock-ai.venv\Scripts\Activate.ps1"
```

Si PowerShell bloque l'exécution des scripts :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Désactiver l'environnement

```powershell
deactivate
```

---

## 3. Gestion des paquets (pip)

```powershell
# Lister tous les paquets installés
pip list

# Informations détaillées sur un paquet (version, dépendances, chemin)
pip show black
pip show numpy

# Rechercher un paquet dans la liste
pip list | Select-String black

# Installer un paquet
pip install kedro

# Installer depuis un fichier requirements
pip install -r requirements.txt

# Exporter les dépendances actuelles
pip freeze > requirements.txt
```

> `Select-String` est l'équivalent PowerShell de `grep`.

---

## 4. Navigation et exploration de fichiers

```powershell
# Aller dans un dossier
cd energystock-ai

# Revenir au dossier parent
cd ..

# Afficher le répertoire courant
pwd

# Lister les fichiers du dossier courant
ls

# Afficher l'arborescence complète du projet
tree /F /A

# Arborescence d'un sous-dossier spécifique
tree /F /A src

# Exporter la structure dans un fichier texte
tree /F /A > structure.txt

# Lire un fichier texte / Markdown
Get-Content README.md
```

> Pour une lecture confortable du Markdown : `code README.md` (VS Code)

---

## 5. Tableau récapitulatif

| Catégorie | Commande | Description |
|---|---|---|
| Python | `py -0p` | Lister les versions installées |
| Python | `python --version` | Version active |
| Venv | `python -m venv nom.venv` | Créer un env virtuel |
| Venv | `py -3.12 -m venv nom.venv` | Créer avec Python 3.12 |
| Venv | `& .\Scripts\Activate.ps1` | Activer l'env virtuel |
| Venv | `deactivate` | Désactiver l'env virtuel |
| Pip | `pip list` | Lister les paquets |
| Pip | `pip show <paquet>` | Détails d'un paquet |
| Pip | `pip list \| Select-String <nom>` | Rechercher un paquet |
| Pip | `pip freeze > requirements.txt` | Exporter les dépendances |
| Fichiers | `ls` | Lister les fichiers |
| Fichiers | `cd mon_dossier` | Naviguer |
| Fichiers | `tree /F /A` | Arborescence complète |
| Fichiers | `tree /F /A src` | Arborescence de `src/` |
| Fichiers | `Get-Content README.md` | Lire un fichier |

---

## 6. Workflow complet — démarrer un projet

```powershell
# 1. Vérifier les versions Python disponibles
py -0p

# 2. Aller dans le dossier du projet
cd energystock-ai

# 3. Créer l'environnement virtuel avec Python 3.12
py -3.12 -m venv energy-stock-ai-3.12.venv

# 4. Activer l'environnement
& ".\energy-stock-ai-3.12.venv\Scripts\Activate.ps1"

# 5. Vérifier la version Python active
python --version

# 6. Installer les dépendances
pip install -r requirements.txt

# 7. Vérifier les paquets installés
pip list

# 8. Explorer la structure du projet
tree /F /A
```

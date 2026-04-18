# Recettes_app

Application en **Python** pour traiter un fichier **XML de recettes** en style **programmation fonctionnelle** (`map`, `filter`, `reduce`, `Counter`, `defaultdict`, etc.) — projet universitaire (Programmation fonctionnelle).

## Fonctionnalités

- Chargement des recettes depuis `data/recipes.xml`
- Modèle de données **immuable** (`dataclasses` figées)
- Requêtes sur les recettes : titres, œufs, filtres (huile d’olive, calories, beurre…), statistiques, tri, etc.
- **Interface en ligne de commande** : menu numéroté, mode texte ou graphique (Matplotlib)
- Tests de non-régression : `test_project.py`

## Structure du dépôt

```
Recettes_app/
├── data/
│   └── recipes.xml          # Données XML (recettes)
├── docs/
│   └── README.txt           # Notes détaillées (interprétation des données, contraintes)
├── src/
│   └── recettes/            # Paquet Python
│       ├── __init__.py
│       ├── models.py        # Recipe, Ingredient, Nutrition
│       ├── repositories.py  # init_recipes + opérations fonctionnelles
│       └── presentation.py  # Menu interactif, état immuable
├── main.py                  # Point d’entrée
├── test_project.py          # Tests manuels
├── requirements.txt
├── README.md                # Ce fichier (vue GitHub)
└── README.txt               # Renvoi vers la doc dans docs/
```

## Prérequis

- Python 3.10+ recommandé
- Sur Linux (ex. Kali), prévoir un **environnement virtuel** (PEP 668 : pas de `pip install` global).

## Installation

```bash
git clone https://github.com/Skjnior/Recettes_app.git
cd Recettes_app

python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py
```

- **0** ou **q** : quitter  
- **t** / **g** : mode texte ou graphique (histogrammes Matplotlib pour certaines options)

Tests :

```bash
python test_project.py
```

## Dépendances

| Paquet       | Rôle                          |
|-------------|--------------------------------|
| `matplotlib` | Graphiques (mode graphique)   |

Le cœur du projet utilise la bibliothèque standard (`xml.etree`, `collections`, `functools`, etc.).

## Interprétation des données

Les règles détaillées (étapes au niveau recette, ingrédients feuilles, etc.) sont dans [`docs/README.txt`](docs/README.txt).

## Auteur

Projet réalisé dans le cadre d’un cours de **Programmation fonctionnelle**.

## Licence

Usage éducatif — voir le dépôt du cours pour les modalités de rendu.

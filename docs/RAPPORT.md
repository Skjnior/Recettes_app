# Rapport de projet — Application de traitement de recettes (Python)

## 1. Contexte et objectif

Ce projet répond au sujet **« Application de traitement de recettes en programmation fonctionnelle avec Python »**.  
L’objectif est de lire un fichier **XML** de recettes, de représenter les données de façon **structurée et immuable**, puis d’appliquer des **traitements fonctionnels** en s’appuyant sur **`map`**, **`filter`**, **`reduce`**, ainsi que **`Counter`**, **`defaultdict`**, **`sorted`**, **`min`** / **`max`** selon les consignes.

Le fichier de données utilisé est `data/recipes.xml` (format recettes avec espace de noms `rcp`).

---

## 2. Architecture du projet

| Élément | Rôle |
|--------|------|
| `data/recipes.xml` | Données sources (non modifiées par l’application). |
| `src/recettes/models.py` | Modèle **immuable** : `Recipe`, `Ingredient`, `Nutrition` (`dataclass` avec `frozen=True`). |
| `src/recettes/repositories.py` | Chargement XML (`init_recipes`) et **toutes les opérations** sur les collections (titres, filtres, agrégations, etc.). |
| `src/recettes/presentation.py` | **Interface ligne de commande** : menu, état d’affichage immuable, mode texte ou graphique (Matplotlib). |
| `main.py` | Point d’entrée : ajoute `src/` au chemin Python et lance le menu sur `data/recipes.xml`. |
| `test_project.py` | Vérifications automatiques des résultats attendus sur le jeu de données fourni. |

Organisation choisie : séparer **données** (`data/`), **code** (`src/recettes/`) et **documentation** (`docs/`).

---

## 3. Choix d’implémentation

### 3.1 Immuabilité

- Les recettes chargées sont stockées dans un **`tuple`** de `Recipe`.
- Les listes d’étapes et les enfants d’ingrédients sont des **`tuple`**.
- Les structures métier utilisent des **`dataclasses` figées** pour éviter les modifications accidentelles.

### 3.2 Programmation fonctionnelle

- Les traitements du dépôt sont des **fonctions** qui prennent des séquences de recettes et retournent de nouvelles valeurs (tuples, dictionnaires, etc.), sans s’appuyer sur un état global mutable pour la logique métier.
- **`reduce`** est utilisé pour le total d’œufs sur toutes les recettes (avec **`map`** sur le décompte par recette).
- **`filter`** pour les sélections (huile d’olive, calories, beurre, nombre d’étapes, etc.).
- **`Counter`** pour les fréquences (unités, ingrédients).
- **`defaultdict`** pour associer chaque ingrédient aux recettes qui l’emploient.

### 3.3 Lecture XML

- Utilisation de **`xml.etree.ElementTree`** (bibliothèque standard).
- Les balises utilisent un espace de noms ; le code repère les éléments par **nom local** (`recipe`, `ingredient`, `step`, etc.).

---

## 4. Interprétation des données (hypothèses documentées)

Ces règles sont **cohérentes** avec le fichier `recipes.xml` et les tests automatisés.

| Sujet | Règle retenue |
|--------|----------------|
| **Étapes d’une recette** | Uniquement les `<rcp:step>` situés dans un `<rcp:preparation>` **fils direct** de `<rcp:recipe>`. Les préparations imbriquées **dans** un ingrédient (ex. sous-recette dans une sauce) ne comptent pas dans ce nombre d’« étapes ». |
| **Ingrédients feuilles** | Ingrédient sans sous-ingrédients : utilisés pour le nombre d’ingrédients par recette, filtres beurre / huile d’olive, etc. |
| **Œufs** | On additionne les **quantités** (`amount`) des feuilles dont le **nom** contient la sous-chaîne **`egg`** (insensible à la casse pour le filtre sur le nom affiché). Les quantités `*` ou non numériques sont ignorées pour la somme. |
| **Nutrition** | Calories et pourcentages (lipides, etc.) issus de l’élément `<rcp:nutrition>`. |

---

## 5. Fonctionnalités réalisées (rappel du sujet)

1. Module **`models`** avec structures immuables.  
2. Module **`repositories`** avec fonctions sur les collections.  
3. **`init_recipes(chemin)`** : parse le XML → tuple de recettes.  
4. Titres avec **`map`**.  
5. Total d’œufs avec **`map`** + **`reduce`**.  
6. Recettes avec huile d’olive avec **`filter`**.  
7. Dictionnaire œufs par recette avec **`map`**.  
8. Recettes &lt; 500 kcal avec **`filter`**.  
9. Quantité de sucre pour « Zuppa Inglese ».  
10. Affichage des deux premières étapes de « Zuppa Inglese ».  
11. Plus de 5 étapes avec **`filter`**.  
12. Sans beurre avec **`filter`**.  
13. Recettes ayant des ingrédients en commun avec « Zuppa Inglese » (`**filter**` + **`set`**).  
14. Recette la plus calorique avec **`max`**.  
15. Unité la plus fréquente avec **`Counter`**.  
16. Nombre d’ingrédients par recette avec **`map`**.  
17. Recette la plus riche en lipides avec **`max`**.  
18. Ingrédient le plus utilisé avec **`Counter`**.  
19. Tri par nombre d’ingrédients avec **`sorted`**.  
20. Ingrédient → liste de recettes avec **`defaultdict`**.  
21. Répartition des recettes par nombre d’étapes.  
22. Recette la plus « facile » (moins d’étapes) avec **`min`**.  
23. **`presentation`** : menu, mode texte / graphique (Matplotlib), état remplacé à chaque action (pas de mutation d’un objet d’état partagé).

---

## 6. Interface utilisateur

- **Console** : menu numéroté **1–19** pour les traitements, **0** ou **q** pour quitter, **t** / **g** pour basculer texte / graphique.  
- **Mode graphique** : histogrammes Matplotlib pour les options pour lesquelles un graphique est pertinent (présence des recettes, répartitions, etc.) ; les autres options retombent sur l’affichage texte si besoin.

---

## 7. Tests et validation

Le script `test_project.py` vérifie automatiquement un ensemble de propriétés (nombre de recettes, totaux, filtres, extrêmes, menu).  
Commande depuis la **racine du projet** :

```bash
python test_project.py
```

---

## 8. Installation et exécution (rappel)

Sous Linux avec Python « externally managed » (PEP 668), utiliser un **environnement virtuel** :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 9. Conclusion

Le projet regroupe le **parsing XML**, un **modèle de données immuable**, une couche **repositories** alignée sur les exigences de **programmation fonctionnelle**, et une **présentation** interactive en console avec option graphique. Les hypothèses sur les étapes et les ingrédients feuilles sont **fixées et documentées** pour éviter toute ambiguïté lors de la relecture ou de la notation.

---

*Document généré pour le dossier de projet — Programmation fonctionnelle (Python).*

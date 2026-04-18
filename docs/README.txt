Projet : traitement de recettes en programmation fonctionnelle (Python)
========================================================================

Rapport complet (objectifs, architecture, tableau des fonctionnalités, hypothèses) :
  docs/RAPPORT.md

Ce fichier (README.txt) résume le lancement et l’interprétation des données.

Architecture des dossiers
-------------------------
  data/          Fichiers de données (recipes.xml).
  src/recettes/  Code source du paquet : models, repositories, presentation.
  docs/          Documentation (rapport, ce fichier).

Fichiers principaux
---------------------
- src/recettes/models.py       : structures immuables (dataclasses frozen).
- src/recettes/repositories.py : init_recipes() et opérations map / filter / reduce,
                                 Counter, defaultdict, sorted, min, max.
- src/recettes/presentation.py : état PresentationState immuable ; menu texte ou graphique.
- main.py (racine du projet)   : point d'entrée ; charge data/recipes.xml.

Lancement
---------
Sur Kali / Debian récents, Python est « externally managed » (PEP 668) : utiliser un venv.

  cd <dossier_du_projet>
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python main.py

Sans venv : .venv/bin/pip install -r requirements.txt puis .venv/bin/python main.py

Tests : python test_project.py (à lancer depuis la racine du projet).

Menu interactif : taper 0 ou q (ou quitter) pour sortir ; t / g pour le mode texte ou graphique.

Interprétation des données
--------------------------
- Les étapes d'une recette sont les <rcp:step> des <rcp:preparation> directement sous
  <rcp:recipe> (pas les préparations imbriquées dans les groupes d'ingrédients).
- Les ingrédients « feuilles » servent au décompte, aux filtres beurre / huile d'olive,
  aux œufs (nom contenant « egg »), et au dictionnaire ingrédient → recettes.
- Les calories et pourcentages viennent de <rcp:nutrition>.

Contraintes du sujet
--------------------
Structures immuables (tuple, frozenset, dataclasses frozen) ; fonctions pures dans
repositories ; l'UI remplace l'état au lieu de le muter en place.

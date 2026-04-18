"""Interface utilisateur : états immuables et choix texte ou graphique."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, Sequence, Tuple

from .models import Recipe

from .repositories import (
    easiest_recipe,
    egg_count_for_recipe,
    eggs_per_recipe_map,
    ingredient_count_per_recipe,
    ingredient_to_recipes,
    init_recipes,
    leaves,
    most_frequent_unit,
    most_used_ingredient_name,
    recipe_highest_fat,
    recipes_distribution_by_step_count,
    recipes_more_than_five_steps,
    recipes_sharing_ingredient_with_zuppa,
    recipes_under_500_calories,
    recipes_with_olive_oil,
    recipes_without_butter,
    recipe_titles,
    total_eggs_all_recipes,
    zuppa_inglese_sugar_amount,
)


@dataclass(frozen=True)
class PresentationState:
    """Écran courant : chaque interaction renvoie un nouvel état (remplacement)."""

    mode: str  # "text" | "graph"
    menu_index: int  # option sélectionnée (0 = aucune / menu principal)
    message: str


def initial_state(mode: str = "text") -> PresentationState:
    return PresentationState(mode=mode, menu_index=0, message="")


def set_mode(state: PresentationState, mode: str) -> PresentationState:
    if mode not in ("text", "graph"):
        mode = "text"
    return replace(state, mode=mode, menu_index=0, message=f"Mode : {mode}")


def select_menu(state: PresentationState, index: int) -> PresentationState:
    return replace(state, menu_index=index, message="")


def _text_block(lines: Sequence[str]) -> str:
    return "\n".join(lines)


def _run_text(index: int, recipes: Tuple[Recipe, ...]) -> str:
    if index == 1:
        return _text_block(recipe_titles(recipes))
    if index == 2:
        return f"Total œufs (estimation quantités) : {total_eggs_all_recipes(recipes)}"
    if index == 3:
        return _text_block([r.title for r in recipes_with_olive_oil(recipes)])
    if index == 4:
        return _text_block([f"{k}: {v}" for k, v in eggs_per_recipe_map(recipes).items()])
    if index == 5:
        return _text_block([r.title for r in recipes_under_500_calories(recipes)])
    if index == 6:
        return zuppa_inglese_sugar_amount(recipes) or "(non trouvé)"
    if index == 7:
        lines: list[str] = []
        for s in (
            _find_recipe(recipes, "Zuppa Inglese").steps[:2]
            if _find_recipe(recipes, "Zuppa Inglese")
            else ()
        ):
            lines.append(s)
        return _text_block(lines) if lines else "(recette absente)"
    if index == 8:
        return _text_block([r.title for r in recipes_more_than_five_steps(recipes)])
    if index == 9:
        return _text_block([r.title for r in recipes_without_butter(recipes)])
    if index == 10:
        return _text_block([r.title for r in recipes_sharing_ingredient_with_zuppa(recipes)])
    if index == 11:
        with_cal = [r for r in recipes if r.nutrition and r.nutrition.calories is not None]
        if not with_cal:
            return "Aucune donnée calorique."
        best = max(with_cal, key=lambda r: r.nutrition.calories if r.nutrition else 0)
        return f"{best.title} ({best.nutrition.calories} kcal)"
    if index == 12:
        return most_frequent_unit(recipes) or "(aucune unité)"
    if index == 13:
        return _text_block([f"{t}: {n}" for t, n in ingredient_count_per_recipe(recipes)])
    if index == 14:
        rf = recipe_highest_fat(recipes)
        return (
            f"{rf.title} ({rf.nutrition.fat_pct}% lipides)"
            if rf and rf.nutrition
            else "(inconnu)"
        )
    if index == 15:
        return most_used_ingredient_name(recipes) or "(aucun)"
    if index == 16:
        pairs = [(r.title, len(leaves(r))) for r in recipes]
        lines = [f"{n:3d} ingrédients — {title}" for title, n in sorted(pairs, key=lambda x: x[1])]
        return _text_block(lines)
    if index == 17:
        d = ingredient_to_recipes(recipes)
        parts = [f"{ing}: {', '.join(titles)}" for ing, titles in sorted(d.items())]
        return _text_block(parts)
    if index == 18:
        return _text_block(
            [f"{k} étapes: {v} recette(s)" for k, v in recipes_distribution_by_step_count(recipes).items()]
        )
    if index == 19:
        er = easiest_recipe(recipes)
        return f"{er.title} ({len(er.steps)} étapes)" if er else "(aucune)"
    return "(option inconnue)"


def _find_recipe(recipes: Sequence[Recipe], title: str) -> Optional[Recipe]:
    t = title.strip().lower()
    for r in recipes:
        if r.title.strip().lower() == t:
            return r
    return None


def apply_selection(
    state: PresentationState, recipes: Tuple[Recipe, ...]
) -> PresentationState:
    """Calcule le résultat pour menu_index courant et met à jour le message."""
    idx = state.menu_index
    if idx <= 0:
        return replace(state, message="Choisissez une option (1–19).")
    if state.mode == "text":
        msg = _run_text(idx, recipes)
        return replace(state, message=msg)
    graph_out = _run_graph(idx, recipes)
    if graph_out is not None:
        return replace(state, message=graph_out)
    return replace(state, message="Graphique affiché (fermez la fenêtre pour continuer).")


def _run_graph(index: int, recipes: Tuple[Recipe, ...]) -> Optional[str]:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return (
            "Matplotlib n'est pas installé. Utilisez: pip install matplotlib\n"
            + _run_text(index, recipes)
        )

    if index in (1, 2, 4, 13, 15, 18):
        if index == 1:
            titles = list(recipe_titles(recipes))
            plt.bar(range(len(titles)), [1] * len(titles))
            plt.xticks(range(len(titles)), titles, rotation=45, ha="right")
            plt.title("Recettes (présence)")
        elif index == 2:
            vals = [egg_count_for_recipe(r) for r in recipes]
            plt.bar([r.title for r in recipes], vals)
            plt.title("Œufs par recette")
            plt.xticks(rotation=45, ha="right")
        elif index == 4:
            m = eggs_per_recipe_map(recipes)
            plt.bar(list(m.keys()), list(m.values()))
            plt.title("Œufs par recette")
            plt.xticks(rotation=45, ha="right")
        elif index == 13:
            pairs = ingredient_count_per_recipe(recipes)
            plt.bar([p[0] for p in pairs], [p[1] for p in pairs])
            plt.title("Nombre d'ingrédients")
            plt.xticks(rotation=45, ha="right")
        elif index == 15:
            from collections import Counter

            names = [li.name.strip().lower() for r in recipes for li in leaves(r)]
            top = Counter(names).most_common(8)
            plt.bar([t[0][:20] for t in top], [t[1] for t in top])
            plt.title("Ingrédients les plus fréquents")
            plt.xticks(rotation=45, ha="right")
        elif index == 18:
            dist = recipes_distribution_by_step_count(recipes)
            plt.bar([str(k) for k in dist.keys()], list(dist.values()))
            plt.title("Répartition par nombre d'étapes")
        plt.tight_layout()
        plt.show()
        return None

    return _run_text(index, recipes)


def menu_labels() -> Tuple[str, ...]:
    return (
        "Titres des recettes (map)",
        "Total œufs (map + reduce)",
        "Recettes avec huile d'olive (filter)",
        "Œufs par recette (map → dict)",
        "Recettes < 500 kcal (filter)",
        "Quantité de sucre — Zuppa Inglese",
        "Deux premières étapes — Zuppa Inglese",
        "> 5 étapes (filter)",
        "Sans beurre (filter)",
        "Ingrédients communs avec Zuppa Inglese (filter + set)",
        "Recette la plus calorique (max)",
        "Unité la plus fréquente (Counter)",
        "Nombre d'ingrédients par recette (map)",
        "Plus de matières grasses (max)",
        "Ingrédient le plus utilisé (Counter)",
        "Tri par nombre d'ingrédients (sorted)",
        "Ingrédient → recettes (defaultdict)",
        "Répartition par nombre d'étapes",
        "Recette la plus facile — min étapes (min)",
    )


def run_interactive(xml_path: str) -> None:
    """Boucle menu : chaque choix produit un nouvel état affiché."""
    recipes = init_recipes(xml_path)
    state = initial_state("text")
    labels = menu_labels()

    while True:
        print("\n--- Menu ---")
        print(
            f"Mode actuel : {state.mode} (t=texte, g=graphique) — "
            "0 ou q pour quitter"
        )
        print("   0. Quitter")
        for i, lab in enumerate(labels, start=1):
            print(f"  {i:2d}. {lab}")
        raw = input("Votre choix : ").strip().lower()
        if raw in ("q", "quitter", "exit"):
            print("Au revoir.")
            break
        if raw == "t":
            state = set_mode(state, "text")
            print(state.message)
            continue
        if raw == "g":
            state = set_mode(state, "graph")
            print(state.message)
            continue
        try:
            choice = int(raw)
        except ValueError:
            print("Entrez 0–19 (0 = quitter), ou t / g / q.")
            continue
        if choice == 0:
            print("Au revoir.")
            break
        if not 1 <= choice <= len(labels):
            print("Numéro invalide (0–19 ou q).")
            continue
        state = select_menu(state, choice)
        state = apply_selection(state, recipes)
        print("\n--- Résultat ---\n")
        print(state.message)



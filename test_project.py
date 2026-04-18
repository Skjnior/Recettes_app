"""Tests manuels du projet (lancer : python test_project.py)."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from recettes.presentation import apply_selection, initial_state, menu_labels, select_menu
from recettes.repositories import (
    easiest_recipe,
    eggs_per_recipe_map,
    init_recipes,
    ingredient_count_per_recipe,
    ingredient_to_recipes,
    most_frequent_unit,
    most_used_ingredient_name,
    print_most_caloric_recipe,
    print_recipes_sorted_by_ingredient_count,
    print_zuppa_inglese_first_two_steps,
    recipe_highest_fat,
    recipe_titles,
    recipes_distribution_by_step_count,
    recipes_more_than_five_steps,
    recipes_sharing_ingredient_with_zuppa,
    recipes_under_500_calories,
    recipes_with_olive_oil,
    recipes_without_butter,
    total_eggs_all_recipes,
    zuppa_inglese_sugar_amount,
)

XML = str(_ROOT / "data" / "recipes.xml")


def main() -> int:
    r = init_recipes(XML)

    def ok(name: str, cond: bool, detail: str = "") -> None:
        line = f"[OK] {name}"
        if detail:
            line += f"  ({detail})"
        print(line)
        assert cond, f"ÉCHEC: {name}"

    ok("init_recipes: 5 recettes", len(r) == 5)
    ok("titres (map)", recipe_titles(r)[0].startswith("Beef"), str(recipe_titles(r)[:2]))
    ok(
        "total œufs (map+reduce)",
        abs(total_eggs_all_recipes(r) - 23.0) < 1e-5,
        str(total_eggs_all_recipes(r)),
    )
    ok("recettes huile d'olive (filter)", len(recipes_with_olive_oil(r)) >= 2)
    ok("œufs par recette (map→dict)", "Zuppa Inglese" in eggs_per_recipe_map(r))
    ok(
        "< 500 kcal (filter)",
        all(x.nutrition.calories < 500 for x in recipes_under_500_calories(r)),
    )
    ok("sucre Zuppa", zuppa_inglese_sugar_amount(r) == "0.75 cup")

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_zuppa_inglese_first_two_steps(r)
    out = buf.getvalue()
    ok("affichage 2 étapes Zuppa", "Warm" in out or "milk" in out.lower())

    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        print_most_caloric_recipe(r)
    ok(
        "plus calorique (max)",
        "Cailles" in buf2.getvalue() and "8892" in buf2.getvalue(),
        buf2.getvalue().strip(),
    )

    ok(
        "> 5 étapes (filter)",
        [x.title for x in recipes_more_than_five_steps(r)] == ["Zuppa Inglese"],
    )
    ok("sans beurre (filter)", "Ricotta Pie" in [x.title for x in recipes_without_butter(r)])
    ok(
        "communs avec Zuppa (filter+set)",
        len(recipes_sharing_ingredient_with_zuppa(r)) == 3,
    )
    ok("unité fréquente (Counter)", most_frequent_unit(r) == "cup")
    rf = recipe_highest_fat(r)
    ok(
        "max lipides (max)",
        rf is not None and rf.title == "Zuppa Inglese" and rf.nutrition.fat_pct == 49,
    )
    ok("ingrédient le plus utilisé (Counter)", most_used_ingredient_name(r) == "flour")

    buf3 = io.StringIO()
    with redirect_stdout(buf3):
        print_recipes_sorted_by_ingredient_count(r)
    ok(
        "tri par nb ingrédients (sorted)",
        "ingrédients" in buf3.getvalue() or "ingredients" in buf3.getvalue().lower(),
    )

    er = easiest_recipe(r)
    ok(
        "plus facile (min étapes)",
        er is not None and er.title == "Linguine Pescadoro" and len(er.steps) == 2,
    )

    dist = recipes_distribution_by_step_count(r)
    ok(
        "répartition par étapes",
        dist.get(2) == 1 and dist.get(7) == 1,
        str(dist),
    )

    d = ingredient_to_recipes(r)
    ok("defaultdict ingrédient→recettes", "Ricotta Pie" in d["flour"])

    pairs = ingredient_count_per_recipe(r)
    ok("nb ingrédients par recette (map)", len(pairs) == 5 and all(p[1] > 0 for p in pairs))

    st = initial_state("text")
    st2 = select_menu(st, 1)
    st3 = apply_selection(st2, r)
    ok("UI immuable + message", "Beef" in st3.message and st3.mode == "text")
    ok("menu 19 entrées", len(menu_labels()) == 19)

    print()
    print("=== Tous les tests sont passés ===")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"\n=== ÉCHEC ===\n{e}", file=sys.stderr)
        raise SystemExit(1)

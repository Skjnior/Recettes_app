"""Accès aux recettes : chargement XML et opérations fonctionnelles."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from functools import reduce
from typing import (
    Callable,
    DefaultDict,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)

from .models import Ingredient, Nutrition, Recipe


def _local_tag(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _parse_int_pct(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    m = re.search(r"(\d+)", value)
    return int(m.group(1)) if m else None


def _parse_nutrition(el: ET.Element) -> Optional[Nutrition]:
    if _local_tag(el.tag) != "nutrition":
        return None
    cal = el.attrib.get("calories")
    return Nutrition(
        calories=int(cal) if cal and cal.isdigit() else None,
        fat_pct=_parse_int_pct(el.attrib.get("fat")),
        carbohydrates_pct=_parse_int_pct(el.attrib.get("carbohydrates")),
        protein_pct=_parse_int_pct(el.attrib.get("protein")),
    )


def _parse_ingredient(el: ET.Element) -> Ingredient:
    children: List[Ingredient] = []
    for child in el:
        if _local_tag(child.tag) == "ingredient":
            children.append(_parse_ingredient(child))
    return Ingredient(
        name=(el.attrib.get("name") or "").strip(),
        amount=el.attrib.get("amount"),
        unit=el.attrib.get("unit"),
        children=tuple(children),
    )


def _parse_steps_from_recipe(recipe_el: ET.Element) -> Tuple[str, ...]:
    steps: List[str] = []
    for child in recipe_el:
        if _local_tag(child.tag) != "preparation":
            continue
        for step_el in child:
            if _local_tag(step_el.tag) != "step":
                continue
            text = (step_el.text or "").strip()
            if text:
                steps.append(text)
    return tuple(steps)


def _parse_recipe(el: ET.Element) -> Recipe:
    rid = el.attrib.get("id", "")
    title = ""
    date = ""
    ingredients: List[Ingredient] = []
    nutrition: Optional[Nutrition] = None

    for child in el:
        tag = _local_tag(child.tag)
        if tag == "title":
            title = (child.text or "").strip()
        elif tag == "date":
            date = (child.text or "").strip()
        elif tag == "ingredient":
            ingredients.append(_parse_ingredient(child))
        elif tag == "nutrition":
            nutrition = _parse_nutrition(child)

    return Recipe(
        id=rid,
        title=title,
        date=date,
        ingredients=tuple(ingredients),
        steps=_parse_steps_from_recipe(el),
        nutrition=nutrition,
    )


def init_recipes(path: str) -> Tuple[Recipe, ...]:
    """Charge le fichier XML et retourne un tuple immuable de recettes."""
    tree = ET.parse(path)
    root = tree.getroot()
    recipes: List[Recipe] = []
    for child in root:
        if _local_tag(child.tag) == "recipe":
            recipes.append(_parse_recipe(child))
    return tuple(recipes)


def _iter_leaves(ing: Ingredient) -> Iterator[Ingredient]:
    if not ing.children:
        yield ing
        return
    for c in ing.children:
        yield from _iter_leaves(c)


def leaves(recipe: Recipe) -> Tuple[Ingredient, ...]:
    return tuple(li for ing in recipe.ingredients for li in _iter_leaves(ing))


def _parse_amount(amount: Optional[str]) -> float:
    if not amount or amount.strip() == "*":
        return 0.0
    try:
        return float(amount)
    except ValueError:
        return 0.0


def _is_egg_ingredient(name: str) -> bool:
    n = name.lower()
    return "egg" in n


def egg_count_for_recipe(recipe: Recipe) -> float:
    return sum(
        _parse_amount(li.amount)
        for li in leaves(recipe)
        if _is_egg_ingredient(li.name)
    )


def _has_named_ingredient(
    recipe: Recipe, predicate: Callable[[str], bool]
) -> bool:
    return any(predicate(li.name.lower()) for li in leaves(recipe))


def _has_olive_oil(recipe: Recipe) -> bool:
    return _has_named_ingredient(recipe, lambda n: "olive oil" in n)


def _has_butter(recipe: Recipe) -> bool:
    return _has_named_ingredient(recipe, lambda n: "butter" in n)


def recipe_titles(recipes: Sequence[Recipe]) -> Tuple[str, ...]:
    """4. Titres des recettes avec map()."""
    return tuple(map(lambda r: r.title, recipes))


def total_eggs_all_recipes(recipes: Sequence[Recipe]) -> float:
    """5. Total d'œufs avec map() et reduce()."""
    counts = map(egg_count_for_recipe, recipes)
    return reduce(lambda a, b: a + b, counts, 0.0)


def recipes_with_olive_oil(recipes: Sequence[Recipe]) -> Tuple[Recipe, ...]:
    """6. Recettes avec huile d'olive avec filter()."""
    return tuple(filter(_has_olive_oil, recipes))


def eggs_per_recipe_map(recipes: Sequence[Recipe]) -> Dict[str, float]:
    """7. Dictionnaire {titre: nombre d'œufs} via map()."""
    pairs = map(lambda r: (r.title, egg_count_for_recipe(r)), recipes)
    return dict(pairs)


def recipes_under_500_calories(recipes: Sequence[Recipe]) -> Tuple[Recipe, ...]:
    """8. Recettes à moins de 500 calories avec filter()."""

    def under(r: Recipe) -> bool:
        if r.nutrition is None or r.nutrition.calories is None:
            return False
        return r.nutrition.calories < 500

    return tuple(filter(under, recipes))


def _find_recipe_by_title(recipes: Sequence[Recipe], title: str) -> Optional[Recipe]:
    t = title.strip().lower()
    for r in recipes:
        if r.title.strip().lower() == t:
            return r
    return None


def zuppa_inglese_sugar_amount(recipes: Sequence[Recipe]) -> str:
    """9. Quantité de sucre pour « Zuppa Inglese »."""
    r = _find_recipe_by_title(recipes, "Zuppa Inglese")
    if r is None:
        return ""
    for li in leaves(r):
        if li.name.strip().lower() == "sugar":
            amt = li.amount or ""
            unit = li.unit or ""
            return f"{amt} {unit}".strip()
    return ""


def print_zuppa_inglese_first_two_steps(recipes: Sequence[Recipe]) -> None:
    """10. Affiche les deux premières étapes de « Zuppa Inglese »."""
    r = _find_recipe_by_title(recipes, "Zuppa Inglese")
    if r is None:
        print("Recette introuvable.")
        return
    for step in r.steps[:2]:
        print(step)


def recipes_more_than_five_steps(recipes: Sequence[Recipe]) -> Tuple[Recipe, ...]:
    """11. Plus de 5 étapes avec filter()."""
    return tuple(filter(lambda r: len(r.steps) > 5, recipes))


def recipes_without_butter(recipes: Sequence[Recipe]) -> Tuple[Recipe, ...]:
    """12. Sans beurre avec filter()."""
    return tuple(filter(lambda r: not _has_butter(r), recipes))


def _ingredient_name_set(recipe: Recipe) -> frozenset[str]:
    return frozenset(li.name.strip().lower() for li in leaves(recipe))


def recipes_sharing_ingredient_with_zuppa(
    recipes: Sequence[Recipe],
) -> Tuple[Recipe, ...]:
    """13. Recettes ayant un ingrédient en commun avec « Zuppa Inglese »."""
    z = _find_recipe_by_title(recipes, "Zuppa Inglese")
    if z is None:
        return tuple()
    zset = _ingredient_name_set(z)

    def shares(r: Recipe) -> bool:
        if r.title.strip().lower() == "zuppa inglese":
            return False
        return bool(zset & _ingredient_name_set(r))

    return tuple(filter(shares, recipes))


def print_most_caloric_recipe(recipes: Sequence[Recipe]) -> None:
    """14. Affiche la recette la plus calorique avec max()."""
    with_cal = [r for r in recipes if r.nutrition and r.nutrition.calories is not None]
    if not with_cal:
        print("Aucune donnée calorique.")
        return
    best = max(with_cal, key=lambda r: r.nutrition.calories if r.nutrition else 0)
    print(f"{best.title} ({best.nutrition.calories} kcal)")


def most_frequent_unit(recipes: Sequence[Recipe]) -> Optional[str]:
    """15. Unité la plus fréquente avec Counter()."""
    units: List[str] = []
    for r in recipes:
        for li in leaves(r):
            u = (li.unit or "").strip()
            if u:
                units.append(u)
    if not units:
        return None
    return Counter(units).most_common(1)[0][0]


def ingredient_count_per_recipe(recipes: Sequence[Recipe]) -> Tuple[Tuple[str, int], ...]:
    """16. Nombre d'ingrédients (feuilles) par recette avec map()."""
    return tuple(map(lambda r: (r.title, len(leaves(r))), recipes))


def recipe_highest_fat(recipes: Sequence[Recipe]) -> Optional[Recipe]:
    """17. Recette la plus riche en matières grasses avec max()."""
    with_fat = [r for r in recipes if r.nutrition and r.nutrition.fat_pct is not None]
    if not with_fat:
        return None
    return max(with_fat, key=lambda r: r.nutrition.fat_pct if r.nutrition else 0)


def most_used_ingredient_name(recipes: Sequence[Recipe]) -> Optional[str]:
    """18. Ingrédient le plus cité avec Counter()."""
    names: List[str] = []
    for r in recipes:
        for li in leaves(r):
            names.append(li.name.strip().lower())
    if not names:
        return None
    return Counter(names).most_common(1)[0][0]


def print_recipes_sorted_by_ingredient_count(recipes: Sequence[Recipe]) -> None:
    """19. Affiche les recettes triées par nombre d'ingrédients avec sorted()."""
    pairs = [(r.title, len(leaves(r))) for r in recipes]
    for title, n in sorted(pairs, key=lambda x: x[1]):
        print(f"{n:3d} ingrédients — {title}")


def ingredient_to_recipes(
    recipes: Sequence[Recipe],
) -> DefaultDict[str, List[str]]:
    """20. Pour chaque ingrédient, recettes qui l'utilisent avec defaultdict()."""
    d: DefaultDict[str, List[str]] = defaultdict(list)
    for r in recipes:
        seen: set[str] = set()
        for li in leaves(r):
            key = li.name.strip().lower()
            if key not in seen:
                seen.add(key)
                d[key].append(r.title)
    return d


def recipes_distribution_by_step_count(
    recipes: Sequence[Recipe],
) -> Dict[int, int]:
    """21. Répartition des recettes par nombre d'étapes."""
    c: Counter[int] = Counter()
    for r in recipes:
        c[len(r.steps)] += 1
    return dict(sorted(c.items()))


def easiest_recipe(recipes: Sequence[Recipe]) -> Optional[Recipe]:
    """22. Recette avec le moins d'étapes avec min()."""
    if not recipes:
        return None
    return min(recipes, key=lambda r: len(r.steps))

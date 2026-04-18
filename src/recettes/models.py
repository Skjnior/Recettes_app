"""Structures de données immuables pour les recettes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Nutrition:
    """Valeurs nutritionnelles optionnelles."""

    calories: Optional[int]
    fat_pct: Optional[int]
    carbohydrates_pct: Optional[int]
    protein_pct: Optional[int]


@dataclass(frozen=True)
class Ingredient:
    """Ingrédient éventuellement imbriqué (groupes « filling », « sauce », etc.)."""

    name: str
    amount: Optional[str]
    unit: Optional[str]
    children: Tuple[Ingredient, ...] = ()


@dataclass(frozen=True)
class Recipe:
    """Recette complète."""

    id: str
    title: str
    date: str
    ingredients: Tuple[Ingredient, ...]
    steps: Tuple[str, ...]
    nutrition: Optional[Nutrition]

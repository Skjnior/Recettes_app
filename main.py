"""Point d'entrée : ajoute src/ au chemin Python puis lance le menu."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from recettes.presentation import run_interactive

if __name__ == "__main__":
    run_interactive(str(_ROOT / "data" / "recipes.xml"))

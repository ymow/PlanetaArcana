"""Load card visual atom data used by AIGC prompt composition."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "card_visual"
PILOT_CARD_SLUGS = {
    "major_fool",
    "major_magician",
    "major_high_priestess",
    "major_lovers",
    "major_death",
    "major_tower",
    "major_star",
    "wands_ace",
    "cups_two",
    "swords_ten",
}


def _load_json(filename: str) -> list[dict[str, Any]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{filename} must contain a JSON array")
    return data


@lru_cache(maxsize=1)
def load_card_visual_data() -> dict[str, list[dict[str, Any]]]:
    """Load all visual atom files."""
    return {
        "facets": _load_json("facets.json"),
        "symbols": _load_json("symbols.json"),
        "compositions": _load_json("compositions.json"),
        "style_scaffolds": _load_json("style_scaffolds.json"),
    }


@lru_cache(maxsize=1)
def load_card_visual_knowledge() -> dict[str, list[dict[str, Any]]]:
    """Load the bottom knowledge layer that informs visual atom design."""
    return {
        "meaning_axes": _load_json("meaning_axes.json"),
        "reference_decks": _load_json("reference_decks.json"),
        "transformation_rules": _load_json("transformation_rules.json"),
    }


def visual_data_for_card(card_slug: str) -> dict[str, list[dict[str, Any]]]:
    """Return the visual atoms available for one card."""
    data = load_card_visual_data()
    return {
        "facets": [item for item in data["facets"] if item["card_slug"] == card_slug],
        "symbols": [item for item in data["symbols"] if item["card_slug"] == card_slug],
        "compositions": [
            item for item in data["compositions"] if item["card_slug"] == card_slug
        ],
    }

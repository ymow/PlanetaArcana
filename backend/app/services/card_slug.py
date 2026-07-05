"""Stable tarot card slug helpers."""

from __future__ import annotations

import re
from typing import Mapping


RANK_SLUGS = {
    "ace": "ace",
    "1": "ace",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
    "page": "page",
    "knight": "knight",
    "queen": "queen",
    "king": "king",
}


def _normalize_major_name(name_en: str) -> str:
    name = name_en.strip().lower()
    if name.startswith("the "):
        name = name[4:]
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def build_card_slug(
    card_type: str,
    name_en: str,
    suit: str | None = None,
    rank: str | None = None,
) -> str:
    """Build a stable card slug used by visual assets and prompt metadata."""
    if card_type == "major":
        return f"major_{_normalize_major_name(name_en)}"

    if not suit or not rank:
        raise ValueError("minor cards require suit and rank for slug generation")

    rank_slug = RANK_SLUGS.get(str(rank).lower())
    if not rank_slug:
        raise ValueError(f"unsupported card rank for slug generation: {rank}")
    return f"{suit}_{rank_slug}"


def build_card_slug_from_mapping(card_data: Mapping[str, object]) -> str:
    """Build a slug from a seed/API dictionary."""
    return build_card_slug(
        card_type=str(card_data.get("type") or ""),
        name_en=str(card_data.get("name_en") or ""),
        suit=str(card_data["suit"]) if card_data.get("suit") else None,
        rank=str(card_data["rank"]) if card_data.get("rank") else None,
    )

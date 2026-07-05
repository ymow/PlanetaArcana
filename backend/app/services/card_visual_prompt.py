"""Compose structured AIGC prompts from tarot visual atoms."""

from __future__ import annotations

import re
from typing import Any, Optional

from app.models.card import Card
from app.services.card_visual_data import load_card_visual_data, visual_data_for_card


def _find_style_scaffold(style_scaffold_id: str) -> dict[str, Any]:
    data = load_card_visual_data()
    for scaffold in data["style_scaffolds"]:
        if scaffold["id"] == style_scaffold_id:
            return scaffold
    raise ValueError(f"unknown style scaffold: {style_scaffold_id}")


def _question_tokens(question_context: Optional[str]) -> set[str]:
    if not question_context:
        return set()
    return set(re.findall(r"[a-zA-Z]+|[\u4e00-\u9fff]+", question_context.lower()))


def _facet_score(
    facet: dict[str, Any],
    orientation: Optional[str],
    context: Optional[str],
    question_context: Optional[str],
) -> tuple[int, str]:
    score = 0
    if orientation:
        if facet["orientation"] == orientation:
            score += 40
        elif facet["orientation"] == "both":
            score += 20

    if context and facet["context"] == context:
        score += 30

    tokens = _question_tokens(question_context)
    if tokens:
        bias = facet.get("question_bias", "").lower()
        score += min(15, sum(1 for token in tokens if token and token in bias) * 5)

    # Stable tie-breaker: prefer upright/both before reversed unless explicitly asked.
    orientation_bias = {"upright": "2", "both": "1", "reversed": "0"}.get(
        facet["orientation"], "0"
    )
    return score, orientation_bias


def _select_facet(
    card_slug: str,
    facet_id: Optional[str],
    orientation: Optional[str],
    context: Optional[str],
    question_context: Optional[str],
) -> dict[str, Any]:
    facets = visual_data_for_card(card_slug)["facets"]
    if not facets:
        raise ValueError(f"no visual facets available for card: {card_slug}")

    if facet_id:
        for facet in facets:
            if facet["id"] == facet_id:
                return facet
        raise ValueError(f"unknown facet for card {card_slug}: {facet_id}")

    return max(
        facets,
        key=lambda facet: (
            _facet_score(facet, orientation, context, question_context),
            facet["id"],
        ),
    )


def _symbols_for_prompt(card_slug: str) -> tuple[list[str], list[str]]:
    symbols = visual_data_for_card(card_slug)["symbols"]
    anchors = [
        f"{item['symbol']} ({item['meaning_link']})"
        for item in symbols
        if item["role"] == "anchor"
    ]
    transformed = [
        (
            f"{item['symbol']} as {'/'.join(item['abstraction_modes'])}; "
            f"alternatives: {', '.join(item['replacement_ideas'])}"
        )
        for item in symbols
        if item["role"] != "anchor"
    ]
    return anchors, transformed


def _composition_terms(card_slug: str) -> list[str]:
    compositions = visual_data_for_card(card_slug)["compositions"]
    if not compositions:
        raise ValueError(f"no composition atoms available for card: {card_slug}")
    item = compositions[0]
    return [
        f"relation: {item['relation_type']}",
        item["spatial_rule"],
        item["camera_rule"],
        item["rhythm_rule"],
    ]


def _style_terms(scaffold: dict[str, Any]) -> list[str]:
    return [
        f"medium: {scaffold['medium']}",
        f"line language: {scaffold['line_language']}",
        f"palette logic: {scaffold['palette_logic']}",
        f"figure treatment: {scaffold['figure_treatment']}",
        f"symbol treatment: {scaffold['symbol_treatment']}",
        f"composition bias: {scaffold['composition_bias']}",
        f"texture: {scaffold['texture_language']}",
        f"border: {scaffold['border_system']}",
        f"typography: {scaffold['typography_system']}",
    ]


def _final_prompt(prompt: dict[str, Any]) -> str:
    sections = [
        ("Subject", prompt["subject_terms"]),
        ("Meaning", prompt["meaning_terms"]),
        ("Required symbols", prompt["required_symbols"]),
        ("Transformable symbols", prompt["transformed_symbols"]),
        ("Composition", prompt["composition_terms"]),
        ("Style", prompt["style_modifiers"]),
        ("Quality", prompt["quality_modifiers"]),
        ("Negative", prompt["negative_constraints"]),
    ]
    return "\n".join(
        f"{title}: " + "; ".join(items)
        for title, items in sections
        if items
    )


def compose_card_visual_prompt(
    card: Card,
    *,
    style_scaffold_id: str = "canonical_echo",
    facet_id: Optional[str] = None,
    orientation: Optional[str] = None,
    context: Optional[str] = None,
    question_context: Optional[str] = None,
) -> dict[str, Any]:
    """Compose a structured prompt for one card visual variant."""
    if not card.slug:
        raise ValueError("card has no slug")

    scaffold = _find_style_scaffold(style_scaffold_id)
    facet = _select_facet(card.slug, facet_id, orientation, context, question_context)
    required_symbols, transformed_symbols = _symbols_for_prompt(card.slug)

    prompt = {
        "subject_terms": [
            "tarot card",
            card.name_en,
            card.name,
            card.slug,
            f"arcana: {card.type}",
        ],
        "meaning_terms": [
            facet["facet_name"],
            facet["core_meaning"],
            f"tone: {', '.join(facet['emotional_tone'])}",
            f"motion: {facet['motion']}",
            f"polarity: {facet['polarity']}",
        ],
        "required_symbols": required_symbols,
        "transformed_symbols": transformed_symbols,
        "composition_terms": _composition_terms(card.slug),
        "style_modifiers": _style_terms(scaffold),
        "quality_modifiers": [
            "vertical tarot card image",
            "coherent deck system",
            "print-ready composition",
            "symbolically readable at card size",
        ],
        "negative_constraints": [
            *scaffold["negative_constraints"],
            "no long explanatory text inside the artwork",
            "no unrelated zodiac or astrology symbols unless required by atoms",
        ],
        "title_text": card.name_en,
    }

    return {
        "card_slug": card.slug,
        "card_name": card.name,
        "card_name_en": card.name_en,
        "facet": facet,
        "style_scaffold": scaffold,
        "prompt": prompt,
        "final_prompt": _final_prompt(prompt),
    }

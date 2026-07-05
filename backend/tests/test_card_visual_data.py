"""AIGC card visual atom data tests."""

from collections import Counter, defaultdict

from app.services.card_visual_data import (
    PILOT_CARD_SLUGS,
    load_card_visual_data,
    load_card_visual_knowledge,
)


def test_visual_atom_data_loads():
    data = load_card_visual_data()

    assert set(data) == {"facets", "symbols", "compositions", "style_scaffolds"}
    assert data["facets"]
    assert data["symbols"]
    assert data["compositions"]
    assert data["style_scaffolds"]


def test_pilot_cards_have_required_visual_atoms():
    data = load_card_visual_data()
    facets_by_card = Counter(item["card_slug"] for item in data["facets"])
    symbols_by_card = Counter(item["card_slug"] for item in data["symbols"])
    compositions_by_card = Counter(item["card_slug"] for item in data["compositions"])

    assert set(facets_by_card) == PILOT_CARD_SLUGS
    assert set(symbols_by_card) == PILOT_CARD_SLUGS
    assert set(compositions_by_card) == PILOT_CARD_SLUGS

    for slug in PILOT_CARD_SLUGS:
        assert facets_by_card[slug] >= 3
        assert symbols_by_card[slug] >= 3
        assert compositions_by_card[slug] >= 1


def test_each_pilot_card_has_anchor_symbol():
    data = load_card_visual_data()
    roles_by_card = defaultdict(set)
    for item in data["symbols"]:
        roles_by_card[item["card_slug"]].add(item["role"])

    for slug in PILOT_CARD_SLUGS:
        assert "anchor" in roles_by_card[slug]


def test_style_scaffolds_have_prompt_controls():
    data = load_card_visual_data()
    scaffolds = {item["id"]: item for item in data["style_scaffolds"]}

    assert set(scaffolds) == {
        "canonical_echo",
        "archetype_abstract",
        "ritual_object",
        "emotional_weather",
    }

    for scaffold in scaffolds.values():
        assert scaffold["medium"]
        assert scaffold["palette_logic"]
        assert scaffold["symbol_treatment"]
        assert scaffold["composition_bias"]
        assert scaffold["negative_constraints"]


def test_visual_knowledge_layer_loads():
    knowledge = load_card_visual_knowledge()

    assert set(knowledge) == {
        "meaning_axes",
        "reference_decks",
        "transformation_rules",
    }
    assert knowledge["meaning_axes"]
    assert knowledge["reference_decks"]
    assert knowledge["transformation_rules"]


def test_reference_decks_are_study_sources_not_copy_targets():
    knowledge = load_card_visual_knowledge()
    deck_ids = {item["id"] for item in knowledge["reference_decks"]}

    assert {
        "rider_waite_smith",
        "tarot_de_marseille",
        "crowley_thoth",
        "wild_unknown",
        "modern_witch",
        "light_seers",
    }.issubset(deck_ids)

    for deck in knowledge["reference_decks"]:
        assert deck["market_role"]
        assert deck["visual_grammar"]
        assert deck["semantic_lesson"]
        assert deck["variation_lesson"]
        assert deck["do_not_copy"]
        assert deck["source_urls"]


def test_transformation_rules_have_operational_checks():
    knowledge = load_card_visual_knowledge()

    rule_ids = {item["id"] for item in knowledge["transformation_rules"]}
    assert {
        "meaning_before_style",
        "preserve_anchor_contract",
        "learn_from_decks_without_imitation",
        "curation_closes_the_loop",
    }.issubset(rule_ids)

    for rule in knowledge["transformation_rules"]:
        assert rule["stage"]
        assert rule["rule"]
        assert rule["rationale"]
        assert rule["checks"]
        assert rule["prompt_effect"]

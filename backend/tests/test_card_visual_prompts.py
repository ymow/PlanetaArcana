"""AIGC card visual prompt API tests."""

import pytest

from app.models.card import Card


@pytest.fixture
def pilot_cards(db_session):
    cards = [
        Card(
            slug="major_fool",
            name="愚者",
            name_en="The Fool",
            type="major",
            number=0,
            upright_meaning="新開始、純真、自發性、自由精神",
            upright_keywords='["新開始", "冒險"]',
            reversed_meaning="魯莽、冒險過度",
            reversed_keywords='["魯莽", "風險"]',
        ),
        Card(
            slug="cups_two",
            name="聖杯二",
            name_en="Two of Cups",
            type="minor",
            suit="cups",
            rank="2",
            number=2,
            upright_meaning="互相吸引、合作、情感交換",
            upright_keywords='["合作", "連結"]',
            reversed_meaning="失衡、自愛、分裂",
            reversed_keywords='["失衡", "分離"]',
        ),
        Card(
            slug="cups_three",
            name="聖杯三",
            name_en="Three of Cups",
            type="minor",
            suit="cups",
            rank="3",
            number=3,
            upright_meaning="慶祝、友誼、合作",
            upright_keywords='["慶祝", "友誼"]',
            reversed_meaning="獨處、過度放縱",
            reversed_keywords='["獨處", "失衡"]',
        ),
    ]
    db_session.add_all(cards)
    db_session.commit()
    for card in cards:
        db_session.refresh(card)
    return cards


def test_card_visual_prompt_default_composes_structured_prompt(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts",
        json={"card_slug": "major_fool"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["card_slug"] == "major_fool"
    assert body["card_name_en"] == "The Fool"
    assert body["style_scaffold"]["id"] == "canonical_echo"
    assert body["facet"]["card_slug"] == "major_fool"
    assert "edge" in " ".join(body["prompt"]["required_symbols"])
    assert "vertical tarot card image" in body["prompt"]["quality_modifiers"]
    assert "Subject:" in body["final_prompt"]
    assert "Negative:" in body["final_prompt"]


def test_card_visual_prompt_can_select_style_and_facet(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts",
        json={
            "card_slug": "cups_two",
            "style_scaffold_id": "ritual_object",
            "facet_id": "cups_two.unequal_bond",
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["facet"]["id"] == "cups_two.unequal_bond"
    assert body["style_scaffold"]["id"] == "ritual_object"
    assert "two cups" in " ".join(body["prompt"]["required_symbols"])
    assert "no generic candle aesthetic" in body["prompt"]["negative_constraints"]


def test_card_visual_prompt_selects_reversed_facet(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts",
        json={"card_slug": "major_fool", "orientation": "reversed"},
    )
    assert response.status_code == 200

    assert response.json()["facet"]["id"] == "major_fool.naive_risk"


def test_card_visual_prompt_rejects_unknown_card_slug(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts", json={"card_slug": "major_unknown"}
    )
    assert response.status_code == 404


def test_card_visual_prompt_rejects_card_without_visual_atoms(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts", json={"card_slug": "cups_three"}
    )
    assert response.status_code == 422
    assert "no visual facets" in response.json()["detail"]


def test_card_visual_prompt_rejects_unknown_style(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/prompts",
        json={"card_slug": "major_fool", "style_scaffold_id": "unknown_style"},
    )
    assert response.status_code == 422
    assert "unknown style scaffold" in response.json()["detail"]


def test_card_visual_knowledge_endpoint_returns_bottom_layer(client):
    response = client.get("/api/card-visuals/knowledge")
    assert response.status_code == 200

    body = response.json()
    assert "meaning_axes" in body
    assert "reference_decks" in body
    assert "transformation_rules" in body
    assert any(
        deck["id"] == "rider_waite_smith" for deck in body["reference_decks"]
    )


def test_create_card_visual_variant_stores_prompt_metadata(client, pilot_cards):
    response = client.post(
        "/api/card-visuals/variants",
        json={
            "card_slug": "major_fool",
            "style_scaffold_id": "archetype_abstract",
            "facet_id": "major_fool.zero_point",
            "model": "test-image-model",
            "seed": 42,
        },
    )
    assert response.status_code == 201

    body = response.json()
    assert body["id"]
    assert body["card_slug"] == "major_fool"
    assert body["facet_id"] == "major_fool.zero_point"
    assert body["style_scaffold_id"] == "archetype_abstract"
    assert body["model"] == "test-image-model"
    assert body["seed"] == 42
    assert body["status"] == "draft"
    assert body["prompt_json"]["title_text"] == "The Fool"
    assert "Subject:" in body["final_prompt"]


def test_list_card_visual_variants_filters_by_card_and_status(client, pilot_cards):
    first = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool", "status": "draft"},
    ).json()
    client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "cups_two", "status": "approved"},
    )

    response = client.get("/api/card-visuals/variants?card_slug=major_fool&status=draft")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == first["id"]


def test_update_card_visual_variant_curation_metadata(client, pilot_cards):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.patch(
        f"/api/card-visuals/variants/{created['id']}",
        json={
            "image_url": "/cards/generated/major_fool.webp",
            "status": "approved",
            "curation_scores": {
                "tarot_recognizability": 4,
                "semantic_accuracy": 5,
                "deck_coherence": 4,
                "originality_safety": 5,
            },
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["image_url"] == "/cards/generated/major_fool.webp"
    assert body["status"] == "approved"
    assert body["curation_scores"]["semantic_accuracy"] == 5


def test_update_card_visual_variant_returns_404(client, pilot_cards):
    response = client.patch(
        "/api/card-visuals/variants/no-such-id", json={"status": "approved"}
    )
    assert response.status_code == 404


def test_curate_card_visual_variant_approves_high_score(client, pilot_cards):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 4,
                "semantic_accuracy": 5,
                "transform_discipline": 4,
                "deck_coherence": 4,
                "originality_safety": 5,
            },
            "reviewer_notes": "Readable and coherent.",
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "approved"
    assert body["curation_scores"]["average_score"] == 4.4
    assert body["curation_scores"]["recommended_status"] == "approved"
    assert body["curation_scores"]["reviewer_notes"] == "Readable and coherent."


def test_curate_card_visual_variant_allows_general_recognizability_three(
    client, pilot_cards
):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 3,
                "semantic_accuracy": 5,
                "transform_discipline": 4,
                "deck_coherence": 4,
                "originality_safety": 5,
            },
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "approved"
    assert body["curation_scores"]["recommended_status"] == "approved"


def test_curate_card_visual_variant_blocks_missing_approval_gates(
    client, pilot_cards
):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 5,
                "semantic_accuracy": 5,
                "transform_discipline": 5,
                "deck_coherence": 3,
                "originality_safety": 4,
            },
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "needs_revision"
    assert body["curation_scores"]["average_score"] == 4.4
    assert "deck coherence" in body["curation_scores"]["gate_notes"][0]
    assert "originality/safety" in body["curation_scores"]["gate_notes"][0]


def test_curate_card_visual_variant_allows_abstract_recognizability_two(
    client, pilot_cards
):
    created = client.post(
        "/api/card-visuals/variants",
        json={
            "card_slug": "major_fool",
            "style_scaffold_id": "archetype_abstract",
        },
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 2,
                "semantic_accuracy": 5,
                "transform_discipline": 5,
                "deck_coherence": 4,
                "originality_safety": 5,
            },
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "approved"
    assert body["curation_scores"]["recommended_status"] == "approved"


def test_curate_card_visual_variant_marks_needs_revision(client, pilot_cards):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 4,
                "semantic_accuracy": 3,
                "transform_discipline": 3,
                "deck_coherence": 3,
                "originality_safety": 4,
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "needs_revision"


def test_curate_card_visual_variant_rejects_safety_failure(client, pilot_cards):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 5,
                "semantic_accuracy": 5,
                "transform_discipline": 5,
                "deck_coherence": 5,
                "originality_safety": 2,
            },
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "rejected"
    assert "safety" in body["curation_scores"]["gate_notes"][0]


def test_curate_card_visual_variant_validates_score_range(client, pilot_cards):
    created = client.post(
        "/api/card-visuals/variants",
        json={"card_slug": "major_fool"},
    ).json()

    response = client.post(
        f"/api/card-visuals/variants/{created['id']}/curation",
        json={
            "scores": {
                "tarot_recognizability": 6,
                "semantic_accuracy": 5,
                "transform_discipline": 5,
                "deck_coherence": 5,
                "originality_safety": 5,
            },
        },
    )
    assert response.status_code == 422

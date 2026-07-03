"""牌陣測試 — 目錄 API、單張與二選一流程、建立驗證"""

from app.services.ai.prompts import SPREADS


def _make_payload(seeded_card, spread_type, position_keys, options=None):
    spread_data = {
        "type": spread_type,
        "cards": [
            {
                "position": key,
                "position_order": i,
                "card_id": seeded_card.id,
                "card_name": seeded_card.name,
                "card_name_en": seeded_card.name_en,
                "is_reversed": False,
            }
            for i, key in enumerate(position_keys)
        ],
    }
    if options:
        spread_data["options"] = options
    return {
        "question_text": "我該怎麼做?",
        "spread_type": spread_type,
        "spread_data": spread_data,
    }


def test_spreads_catalog(client):
    response = client.get("/api/spreads")
    assert response.status_code == 200

    spreads = response.json()
    assert {s["id"] for s in spreads} == set(SPREADS)

    by_id = {s["id"]: s for s in spreads}
    assert by_id["past_present_future"]["card_count"] == 3
    assert by_id["single"]["card_count"] == 1
    assert by_id["two_choice"]["card_count"] == 2
    assert by_id["two_choice"]["requires_options"] is True
    assert by_id["single"]["positions"][0]["name"] == "核心指引"
    # prompt 細節不外洩
    assert "reading_focus" not in by_id["single"]


def test_single_spread_full_flow(client, seeded_card, mock_claude):
    payload = _make_payload(seeded_card, "single", ["guidance"])
    created = client.post("/api/divines", json=payload)
    assert created.status_code == 201

    result = client.post(
        f"/api/divines/{created.json()['id']}/interpret",
        json={"interpretation_type": "initial"},
    )
    assert result.status_code == 200
    assert "單張指引" in mock_claude["generate_user_prompt"]
    assert "核心指引" in mock_claude["generate_user_prompt"]


def test_two_choice_includes_options_in_prompt(client, seeded_card, mock_claude):
    payload = _make_payload(
        seeded_card,
        "two_choice",
        ["option_a", "option_b"],
        options={"a": "留在現在的公司", "b": "接受新工作機會"},
    )
    created = client.post("/api/divines", json=payload)
    assert created.status_code == 201

    result = client.post(
        f"/api/divines/{created.json()['id']}/interpret",
        json={"interpretation_type": "initial"},
    )
    assert result.status_code == 200

    prompt = mock_claude["generate_user_prompt"]
    assert "留在現在的公司" in prompt
    assert "接受新工作機會" in prompt
    assert "選項 A" in prompt


def test_create_rejects_unknown_spread(client, seeded_card):
    payload = _make_payload(seeded_card, "celtic_cross", ["p1"])
    response = client.post("/api/divines", json=payload)
    assert response.status_code == 422
    assert "牌陣" in response.json()["detail"]


def test_create_rejects_wrong_card_count(client, seeded_card):
    # 單張牌陣塞三張牌
    payload = _make_payload(seeded_card, "single", ["guidance", "extra", "more"])
    response = client.post("/api/divines", json=payload)
    assert response.status_code == 422
    assert "1 張牌" in response.json()["detail"]


def test_two_choice_requires_both_options(client, seeded_card):
    payload = _make_payload(
        seeded_card, "two_choice", ["option_a", "option_b"], options={"a": "只有一個"}
    )
    response = client.post("/api/divines", json=payload)
    assert response.status_code == 422
    assert "選項" in response.json()["detail"]

    no_options = _make_payload(seeded_card, "two_choice", ["option_a", "option_b"])
    assert client.post("/api/divines", json=no_options).status_code == 422

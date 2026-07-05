"""塔羅牌 API 與 slug 基礎資料測試"""

from app.db.seed_cards import get_tarot_cards_data


def test_seed_cards_have_unique_stable_slugs():
    cards = get_tarot_cards_data()
    slugs = [card["slug"] for card in cards]

    assert len(cards) == 78
    assert len(slugs) == len(set(slugs))
    assert "major_fool" in slugs
    assert "major_high_priestess" in slugs
    assert "wands_ace" in slugs
    assert "cups_two" in slugs
    assert "swords_ten" in slugs
    assert "pentacles_king" in slugs


def test_cards_api_returns_slug(client, seeded_card):
    response = client.get("/api/cards")
    assert response.status_code == 200

    cards = response.json()
    assert cards[0]["id"] == seeded_card.id
    assert cards[0]["slug"] == "major_fool"


def test_create_card_generates_slug_when_missing(client):
    payload = {
        "name": "魔術師",
        "name_en": "The Magician",
        "type": "major",
        "number": 1,
        "upright_meaning": "顯化、資源、行動",
        "upright_keywords": '["顯化", "創造"]',
        "reversed_meaning": "操控、浪費天賦",
        "reversed_keywords": '["操控", "欺騙"]',
    }

    response = client.post("/api/cards", json=payload)
    assert response.status_code == 201
    assert response.json()["slug"] == "major_magician"


def test_create_minor_card_generates_rank_word_slug(client):
    payload = {
        "name": "聖杯二",
        "name_en": "Two of Cups",
        "type": "minor",
        "suit": "cups",
        "rank": "2",
        "number": 2,
        "upright_meaning": "互相吸引、合作、情感交換",
        "upright_keywords": '["合作", "連結"]',
        "reversed_meaning": "失衡、自愛、分裂",
        "reversed_keywords": '["失衡", "分離"]',
    }

    response = client.post("/api/cards", json=payload)
    assert response.status_code == 201
    assert response.json()["slug"] == "cups_two"

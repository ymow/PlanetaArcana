"""每日一牌測試"""

import json

from app.models.api_usage import ApiUsage
from app.models.daily_draw import DailyDraw
from app.services.ai.claude_client import ClaudeClient


FAKE_DAILY_DRAW = {
    "key_theme": "穩定前進",
    "summary": "今天適合把注意力放回你能控制的小步行動，讓節奏慢下來但不要停下。",
    "advice": "先完成一件最重要的小事，再回頭整理其他安排。",
    "reflection_prompt": "今天哪一件事最值得你投入穩定的注意力？",
}


def test_daily_draw_requires_login(client):
    response = client.get("/api/daily-draws/today")
    assert response.status_code == 401


def test_create_daily_draw_once_per_day(
    client, db_session, seeded_card, auth_headers, test_user, monkeypatch
):
    def fake_generate(self, system_prompt, user_prompt, output_schema=None):
        return {
            "content": json.dumps(FAKE_DAILY_DRAW, ensure_ascii=False),
            "tokens": {"input": 20, "output": 40, "total": 60},
        }

    monkeypatch.setattr(ClaudeClient, "generate_interpretation", fake_generate)

    first = client.post("/api/daily-draws/today", headers=auth_headers)
    assert first.status_code == 201
    first_body = first.json()
    assert first_body["user_id"] == test_user.id
    assert first_body["card_id"] == seeded_card.id
    assert first_body["interpretation"]["key_theme"] == FAKE_DAILY_DRAW["key_theme"]

    second = client.post("/api/daily-draws/today", headers=auth_headers)
    assert second.status_code == 200
    assert second.json()["id"] == first_body["id"]

    saved = db_session.query(DailyDraw).all()
    assert len(saved) == 1

    usage = (
        db_session.query(ApiUsage)
        .filter(ApiUsage.client_ip == f"user:{test_user.id}")
        .first()
    )
    assert usage.count == 1


def test_get_today_daily_draw(client, seeded_card, auth_headers, monkeypatch):
    def fake_generate(self, system_prompt, user_prompt, output_schema=None):
        return {
            "content": json.dumps(FAKE_DAILY_DRAW, ensure_ascii=False),
            "tokens": {"input": 20, "output": 40, "total": 60},
        }

    monkeypatch.setattr(ClaudeClient, "generate_interpretation", fake_generate)

    created = client.post("/api/daily-draws/today", headers=auth_headers).json()
    fetched = client.get("/api/daily-draws/today", headers=auth_headers)

    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]

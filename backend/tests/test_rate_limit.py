"""AI 端點限流測試 — 每日配額與突發限制"""

import pytest

from app.core.auth import create_access_token
from app.core.config import settings
from app.models.user import User


@pytest.fixture
def tight_daily_limit(monkeypatch):
    monkeypatch.setattr(settings, "AI_DAILY_LIMIT", 2)


@pytest.fixture
def tight_burst_limit(monkeypatch):
    monkeypatch.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 3)


def _interpret(client, divine_id):
    return client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    )


def test_daily_quota_blocks_after_limit(
    client, divine_payload, mock_claude, tight_daily_limit
):
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    assert _interpret(client, divine_id).status_code == 200
    assert _interpret(client, divine_id).status_code == 200

    third = _interpret(client, divine_id)
    assert third.status_code == 429
    assert "每日" in third.json()["detail"]
    assert third.headers.get("retry-after") == "86400"


def test_quota_shared_across_ai_endpoints(
    client, divine_payload, mock_claude, tight_daily_limit
):
    """解讀與追問共用同一組每日配額"""
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]
    result = _interpret(client, divine_id)
    assert result.status_code == 200
    conversation_id = result.json()["conversation_id"]

    # 第二次呼叫（追問）用掉配額
    assert (
        client.post(
            f"/api/conversations/{conversation_id}/message", json={"message": "追問"}
        ).status_code
        == 200
    )

    # 第三次呼叫超限
    assert (
        client.post(
            f"/api/conversations/{conversation_id}/message", json={"message": "再追問"}
        ).status_code
        == 429
    )


def test_burst_limit_blocks_rapid_calls(
    client, divine_payload, mock_claude, tight_burst_limit
):
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    for _ in range(3):
        assert _interpret(client, divine_id).status_code == 200

    burst = _interpret(client, divine_id)
    assert burst.status_code == 429
    assert "頻繁" in burst.json()["detail"]


def test_non_ai_endpoints_not_limited(client, divine_payload, tight_daily_limit):
    """一般 CRUD 不受 AI 配額限制"""
    for _ in range(5):
        assert client.get("/api/divines").status_code == 200
    assert client.post("/api/divines", json=divine_payload).status_code == 201


def test_authenticated_quota_is_per_user(
    client, db_session, divine_payload, mock_claude, monkeypatch
):
    monkeypatch.setattr(settings, "AI_DAILY_LIMIT", 1)

    user_one = User(email="one@example.com", name="One")
    user_two = User(email="two@example.com", name="Two")
    db_session.add_all([user_one, user_two])
    db_session.commit()
    db_session.refresh(user_one)
    db_session.refresh(user_two)

    headers_one = {"Authorization": f"Bearer {create_access_token(user_one)}"}
    headers_two = {"Authorization": f"Bearer {create_access_token(user_two)}"}

    divine_one = client.post(
        "/api/divines", json=divine_payload, headers=headers_one
    ).json()["id"]
    divine_two = client.post(
        "/api/divines", json=divine_payload, headers=headers_two
    ).json()["id"]

    assert _interpret(client, divine_one).status_code == 404
    assert client.post(
        f"/api/divines/{divine_one}/interpret",
        json={"interpretation_type": "initial"},
        headers=headers_one,
    ).status_code == 200
    assert client.post(
        f"/api/divines/{divine_one}/interpret",
        json={"interpretation_type": "initial"},
        headers=headers_one,
    ).status_code == 429
    assert client.post(
        f"/api/divines/{divine_two}/interpret",
        json={"interpretation_type": "initial"},
        headers=headers_two,
    ).status_code == 200

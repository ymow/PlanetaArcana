"""分享 +1 配額測試 — 加額生效、防重複領取、每日加額上限、配額狀態"""

import pytest

from app.core.config import settings


@pytest.fixture
def tight_daily_limit(monkeypatch):
    monkeypatch.setattr(settings, "AI_DAILY_LIMIT", 1)


def _interpret(client, divine_id):
    return client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    )


def _create_divine(client, divine_payload):
    return client.post("/api/divines", json=divine_payload).json()["id"]


def test_share_bonus_extends_daily_quota(
    client, divine_payload, mock_claude, tight_daily_limit
):
    divine_id = _create_divine(client, divine_payload)

    assert _interpret(client, divine_id).status_code == 200
    assert _interpret(client, divine_id).status_code == 429

    share = client.post(f"/api/divines/{divine_id}/share")
    assert share.status_code == 200
    body = share.json()
    assert body["granted"] is True
    assert body["quota"]["share_bonus"] == 1
    assert body["quota"]["remaining"] == 1

    assert _interpret(client, divine_id).status_code == 200
    assert _interpret(client, divine_id).status_code == 429


def test_duplicate_share_claim_not_granted(client, divine_payload):
    divine_id = _create_divine(client, divine_payload)

    first = client.post(f"/api/divines/{divine_id}/share").json()
    assert first["granted"] is True

    second = client.post(f"/api/divines/{divine_id}/share").json()
    assert second["granted"] is False
    assert "已領取" in second["reason"]
    assert second["quota"]["share_bonus"] == 1


def test_daily_share_bonus_cap(client, divine_payload, monkeypatch):
    monkeypatch.setattr(settings, "AI_SHARE_BONUS_DAILY_MAX", 2)

    ids = [_create_divine(client, divine_payload) for _ in range(3)]
    assert client.post(f"/api/divines/{ids[0]}/share").json()["granted"] is True
    assert client.post(f"/api/divines/{ids[1]}/share").json()["granted"] is True

    capped = client.post(f"/api/divines/{ids[2]}/share").json()
    assert capped["granted"] is False
    assert "上限" in capped["reason"]
    assert capped["quota"]["share_bonus"] == 2


def test_share_nonexistent_divine_returns_404(client):
    assert client.post("/api/divines/no-such-id/share").status_code == 404


def test_share_other_users_divine_returns_404(
    client, divine_payload, auth_headers
):
    """匿名者不能用他人（登入者）的占卜領取加額"""
    divine_id = client.post(
        "/api/divines", json=divine_payload, headers=auth_headers
    ).json()["id"]

    assert client.post(f"/api/divines/{divine_id}/share").status_code == 404


def test_quota_status_endpoint_reflects_usage_and_bonus(
    client, divine_payload, mock_claude, tight_daily_limit
):
    divine_id = _create_divine(client, divine_payload)

    initial = client.get("/api/quota").json()
    assert initial == {"daily_limit": 1, "share_bonus": 0, "used": 0, "remaining": 1}

    _interpret(client, divine_id)
    client.post(f"/api/divines/{divine_id}/share")

    status = client.get("/api/quota").json()
    assert status == {"daily_limit": 1, "share_bonus": 1, "used": 1, "remaining": 1}


def test_share_bonus_is_per_quota_key(
    client, divine_payload, mock_claude, tight_daily_limit, auth_headers
):
    """登入者領的加額不影響匿名 IP 的配額"""
    divine_id = _create_divine(client, divine_payload)
    client.post(f"/api/divines/{divine_id}/claim", headers=auth_headers)

    share = client.post(f"/api/divines/{divine_id}/share", headers=auth_headers)
    assert share.json()["granted"] is True

    anonymous = client.get("/api/quota").json()
    assert anonymous["share_bonus"] == 0
    logged_in = client.get("/api/quota", headers=auth_headers).json()
    assert logged_in["share_bonus"] == 1

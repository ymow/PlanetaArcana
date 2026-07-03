"""人格化解讀角色測試 — 目錄 API、持久化、角色貫穿解讀與追問、舊資料 fallback"""

from app.db.database import SessionLocal
from app.models.divine import Divine
from app.services.ai.prompts import DEFAULT_PERSONA_ID, PERSONAS


def test_personas_catalog_has_display_fields_without_prompts(client):
    response = client.get("/api/personas")
    assert response.status_code == 200

    personas = response.json()
    assert len(personas) == 4
    assert {p["id"] for p in personas} == set(PERSONAS)

    for persona in personas:
        assert persona.keys() == {
            "id", "name", "name_en", "emoji", "tagline", "description", "is_premium",
        }
        # prompt 內容不得外洩
        assert "voice" not in persona


def test_create_divine_persists_persona(client, divine_payload):
    created = client.post(
        "/api/divines", json={**divine_payload, "persona_id": "raven"}
    ).json()
    assert created["persona_id"] == "raven"

    fetched = client.get(f"/api/divines/{created['id']}").json()
    assert fetched["persona_id"] == "raven"


def test_create_divine_defaults_to_default_persona(client, divine_payload):
    created = client.post("/api/divines", json=divine_payload).json()
    assert created["persona_id"] == DEFAULT_PERSONA_ID


def test_create_divine_rejects_unknown_persona(client, divine_payload):
    response = client.post(
        "/api/divines", json={**divine_payload, "persona_id": "cthulhu"}
    )
    assert response.status_code == 422
    assert "角色" in response.json()["detail"]


def test_interpretation_uses_persona_voice(client, divine_payload, mock_claude):
    divine_id = client.post(
        "/api/divines", json={**divine_payload, "persona_id": "raven"}
    ).json()["id"]

    assert (
        client.post(
            f"/api/divines/{divine_id}/interpret",
            json={"interpretation_type": "initial"},
        ).status_code
        == 200
    )
    assert "渡鴉" in mock_claude["generate_system_prompt"]
    assert "月見" not in mock_claude["generate_system_prompt"]


def test_stream_interpretation_uses_persona_voice(
    client, divine_payload, mock_claude
):
    divine_id = client.post(
        "/api/divines", json={**divine_payload, "persona_id": "luna"}
    ).json()["id"]

    response = client.post(f"/api/divines/{divine_id}/interpret/stream")
    assert response.status_code == 200
    assert "event: complete" in response.text
    assert "月見" in mock_claude["stream_system_prompt"]


def test_follow_up_keeps_same_persona(client, divine_payload, mock_claude):
    """追問必須沿用初始解讀的角色,不能「變聲」回預設角色"""
    divine_id = client.post(
        "/api/divines", json={**divine_payload, "persona_id": "sage"}
    ).json()["id"]

    conversation_id = client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    ).json()["conversation_id"]

    assert (
        client.post(
            f"/api/conversations/{conversation_id}/message", json={"message": "為什麼?"}
        ).status_code
        == 200
    )
    assert "奧術學者" in mock_claude["follow_up_system_prompt"]
    assert "星野老師" not in mock_claude["follow_up_system_prompt"]


def test_legacy_divine_without_persona_falls_back_to_default(
    client, divine_payload, mock_claude
):
    """persona_id 為 NULL 的舊資料:解讀與追問都用預設角色,不炸"""
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    # 模擬 Phase 3 之前建立的舊資料
    db = SessionLocal()
    db.query(Divine).filter(Divine.id == divine_id).update({"persona_id": None})
    db.commit()
    db.close()

    result = client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    )
    assert result.status_code == 200
    assert "星野老師" in mock_claude["generate_system_prompt"]

    conversation_id = result.json()["conversation_id"]
    assert (
        client.post(
            f"/api/conversations/{conversation_id}/message", json={"message": "追問"}
        ).status_code
        == 200
    )
    assert "星野老師" in mock_claude["follow_up_system_prompt"]

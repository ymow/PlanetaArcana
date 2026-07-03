"""占卜 CRUD 與 AI 解讀流程測試"""

from tests.conftest import FAKE_INTERPRETATION


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_divine_crud(client, divine_payload):
    # Create
    created = client.post("/api/divines", json=divine_payload)
    assert created.status_code == 201
    divine_id = created.json()["id"]

    # Read
    fetched = client.get(f"/api/divines/{divine_id}")
    assert fetched.status_code == 200
    assert fetched.json()["question_text"] == divine_payload["question_text"]

    # List
    listed = client.get("/api/divines")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    # Update
    updated = client.put(
        f"/api/divines/{divine_id}", json={"question_text": "更新後的問題"}
    )
    assert updated.status_code == 200
    assert updated.json()["question_text"] == "更新後的問題"

    # Delete
    assert client.delete(f"/api/divines/{divine_id}").status_code == 204
    assert client.get(f"/api/divines/{divine_id}").status_code == 404


def test_get_missing_divine_returns_404(client):
    assert client.get("/api/divines/nonexistent-id").status_code == 404


def test_interpret_flow(client, divine_payload, mock_claude):
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    response = client.post(
        f"/api/divines/{divine_id}/interpret",
        json={"interpretation_type": "initial"},
    )
    assert response.status_code == 200
    body = response.json()

    assert body["divine_id"] == divine_id
    assert body["interpretation"]["overall_summary"] == FAKE_INTERPRETATION["overall_summary"]
    assert len(body["interpretation"]["card_interpretations"]) == 3
    assert body["conversation_id"]
    assert body["metadata"]["tokens_used"] == 300

    # 解讀結果應寫回占卜記錄
    divine = client.get(f"/api/divines/{divine_id}").json()
    assert divine["is_ai_interpreted"] is True
    assert divine["interpretation"]["advice"] == FAKE_INTERPRETATION["advice"]


def test_reinterpret_reuses_conversation(client, divine_payload, mock_claude):
    """同一占卜重複解讀不得因 divine_id unique 約束而 500"""
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    first = client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    )
    second = client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    )

    assert first.status_code == 200
    assert second.status_code == 200
    # 沿用同一筆對話記錄
    assert first.json()["conversation_id"] == second.json()["conversation_id"]


def test_interpret_missing_divine_returns_404(client, mock_claude):
    response = client.post(
        "/api/divines/nonexistent-id/interpret",
        json={"interpretation_type": "initial"},
    )
    assert response.status_code == 404

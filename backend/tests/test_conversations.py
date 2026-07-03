"""追問對話流程測試 — 持久化與脈絡完整性"""


def _interpret(client, divine_payload):
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]
    result = client.post(
        f"/api/divines/{divine_id}/interpret", json={"interpretation_type": "initial"}
    ).json()
    return divine_id, result["conversation_id"]


def test_follow_up_message_persists(client, divine_payload, mock_claude):
    """追問訊息必須確實寫入資料庫（MutableList 修復的回歸測試）"""
    _, conversation_id = _interpret(client, divine_payload)

    response = client.post(
        f"/api/conversations/{conversation_id}/message",
        json={"message": "可以再多說一點現在這張牌嗎？"},
    )
    assert response.status_code == 200
    assert response.json()["message"]["content"] == "這是追問的回覆"

    # 重新讀取對話 — 初始解讀 + 追問 + 回覆 = 3 則
    conversation = client.get(f"/api/conversations/{conversation_id}").json()
    assert len(conversation["messages"]) == 3
    assert conversation["messages"][1]["role"] == "user"
    assert conversation["messages"][2]["role"] == "assistant"
    assert conversation["total_tokens"] == 600  # 初始 300 + 追問 300


def test_follow_up_includes_divination_context(client, divine_payload, mock_claude):
    """送給 Claude 的追問請求必須包含原始占卜脈絡與初始解讀"""
    _, conversation_id = _interpret(client, divine_payload)

    client.post(
        f"/api/conversations/{conversation_id}/message",
        json={"message": "牌面代表什麼？"},
    )

    sent = mock_claude["conversation_messages"]
    assert sent is not None
    # 第一則：重建的原始占卜 prompt（含問題與牌面）
    assert sent[0]["role"] == "user"
    assert divine_payload["question_text"] in sent[0]["content"]
    assert "愚者" in sent[0]["content"]
    # 第二則：初始解讀
    assert sent[1]["role"] == "assistant"
    # 最後一則：新的追問
    assert sent[-1] == {"role": "user", "content": "牌面代表什麼？"}


def test_message_to_missing_conversation_returns_404(client, mock_claude):
    response = client.post(
        "/api/conversations/nonexistent-id/message", json={"message": "hello"}
    )
    assert response.status_code == 404

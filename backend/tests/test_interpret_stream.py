"""SSE 串流解讀測試 — 串流事件、持久化、配額、錯誤行為"""

import json

import pytest

from app.core.config import settings
from app.services.ai.claude_client import ClaudeClient


def _parse_sse(body: str) -> list[tuple[str, dict]]:
    """把 SSE 回應解析為 (event, data) 列表"""
    events = []
    for block in body.split("\n\n"):
        if not block.strip():
            continue
        event, data = None, None
        for line in block.split("\n"):
            if line.startswith("event: "):
                event = line[len("event: ") :]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: ") :])
        events.append((event, data))
    return events


def _stream(client, divine_id):
    return client.post(f"/api/divines/{divine_id}/interpret/stream")


def test_stream_emits_deltas_then_complete_and_persists(
    client, divine_payload, mock_claude
):
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    response = _stream(client, divine_id)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = _parse_sse(response.text)
    deltas = [d for e, d in events if e == "delta"]
    completes = [d for e, d in events if e == "complete"]

    assert len(deltas) >= 2
    assert len(completes) == 1

    # delta 串起來就是完整的 JSON 回應
    joined = "".join(d["text"] for d in deltas)
    assert json.loads(joined)["advice"] == "測試建議"

    complete = completes[0]
    assert complete["divine_id"] == divine_id
    assert complete["interpretation"]["advice"] == "測試建議"
    assert complete["conversation_id"]

    # 持久化：divine 已標記解讀完成，追問對話已建立
    divine = client.get(f"/api/divines/{divine_id}").json()
    assert divine["is_ai_interpreted"] is True
    assert divine["interpretation"]["advice"] == "測試建議"

    conversation = client.get(
        f"/api/conversations/{complete['conversation_id']}"
    ).json()
    assert len(conversation["messages"]) == 1


def test_stream_consumes_daily_quota(
    client, divine_payload, mock_claude, monkeypatch
):
    monkeypatch.setattr(settings, "AI_DAILY_LIMIT", 1)
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    assert _stream(client, divine_id).status_code == 200
    assert _stream(client, divine_id).status_code == 429


def test_stream_failure_emits_error_and_persists_nothing(
    client, divine_payload, monkeypatch
):
    def broken_stream(self, system_prompt, user_prompt, output_schema=None):
        yield {"type": "delta", "text": '{"overall'}
        raise Exception("connection lost")

    monkeypatch.setattr(ClaudeClient, "stream_interpretation", broken_stream)
    divine_id = client.post("/api/divines", json=divine_payload).json()["id"]

    response = _stream(client, divine_id)
    assert response.status_code == 200  # SSE 已開始，錯誤以事件回報

    events = _parse_sse(response.text)
    assert events[-1][0] == "error"
    assert "AI 解讀失敗" in events[-1][1]["detail"]

    divine = client.get(f"/api/divines/{divine_id}").json()
    assert divine["is_ai_interpreted"] is False


def test_stream_respects_divine_ownership(
    client, divine_payload, mock_claude, auth_headers
):
    divine_id = client.post(
        "/api/divines", json=divine_payload, headers=auth_headers
    ).json()["id"]

    # 匿名者無法串流他人占卜
    assert _stream(client, divine_id).status_code == 404

    owned = client.post(
        f"/api/divines/{divine_id}/interpret/stream", headers=auth_headers
    )
    assert owned.status_code == 200
    assert _parse_sse(owned.text)[-1][0] == "complete"

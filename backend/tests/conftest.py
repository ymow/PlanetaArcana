"""測試共用 fixtures — 隔離的 SQLite 測試資料庫 + mock Claude API"""

import json
import os
import tempfile

# 必須在 import app 之前設定：環境變數優先於 .env 檔
_TEST_DB_DIR = tempfile.mkdtemp(prefix="planeta_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_DIR}/test.db"
os.environ["ANTHROPIC_API_KEY"] = "test-key-not-used"
os.environ["DEBUG"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.main import app  # noqa: E402 — 觸發 create_all
from app.core.auth import create_access_token
from app.core import rate_limit
from app.core.config import settings
from app.db.database import Base, SessionLocal, engine
from app.models.card import Card
from app.models.user import User
from app.services.ai.claude_client import ClaudeClient

FAKE_INTERPRETATION = {
    "overall_summary": "這是一段測試用的整體解讀內容。" * 10,  # 超過 50 字的驗證門檻
    "card_interpretations": [
        {"position": "past", "card_name": "愚者(正位)", "interpretation": "過去的解讀"},
        {"position": "present", "card_name": "愚者(正位)", "interpretation": "現在的解讀"},
        {"position": "future", "card_name": "愚者(正位)", "interpretation": "未來的解讀"},
    ],
    "advice": "測試建議",
    "key_insights": ["洞察一", "洞察二", "洞察三"],
}

FAKE_TOKENS = {"input": 100, "output": 200, "total": 300}


@pytest.fixture(autouse=True)
def clean_db():
    """每個測試用乾淨的資料表與限流視窗"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    rate_limit.reset_burst_window()
    yield


@pytest.fixture(autouse=True)
def relaxed_burst_limit(monkeypatch):
    """預設放寬突發限制，避免一般測試誤觸；限流測試自行覆寫"""
    monkeypatch.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 1000)


@pytest.fixture
def mock_claude(monkeypatch):
    """把 Claude API 呼叫替換成固定回應；記錄收到的 messages 與 system prompts"""
    captured = {
        "conversation_messages": None,
        "generate_system_prompt": None,
        "generate_user_prompt": None,
        "stream_system_prompt": None,
        "follow_up_system_prompt": None,
    }

    def fake_generate(self, system_prompt, user_prompt, output_schema=None):
        captured["generate_system_prompt"] = system_prompt
        captured["generate_user_prompt"] = user_prompt
        return {
            "content": json.dumps(FAKE_INTERPRETATION, ensure_ascii=False),
            "tokens": dict(FAKE_TOKENS),
        }

    def fake_continue(self, system_prompt, messages):
        captured["conversation_messages"] = messages
        captured["follow_up_system_prompt"] = system_prompt
        return {"content": "這是追問的回覆", "tokens": dict(FAKE_TOKENS)}

    def fake_stream(self, system_prompt, user_prompt, output_schema=None):
        captured["stream_system_prompt"] = system_prompt
        content = json.dumps(FAKE_INTERPRETATION, ensure_ascii=False)
        chunk_size = max(1, len(content) // 5)
        for i in range(0, len(content), chunk_size):
            yield {"type": "delta", "text": content[i : i + chunk_size]}
        yield {"type": "final", "content": content, "tokens": dict(FAKE_TOKENS)}

    monkeypatch.setattr(ClaudeClient, "generate_interpretation", fake_generate)
    monkeypatch.setattr(ClaudeClient, "continue_conversation", fake_continue)
    monkeypatch.setattr(ClaudeClient, "stream_interpretation", fake_stream)
    return captured


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def seeded_card(db_session):
    card = Card(
        name="愚者",
        name_en="The Fool",
        type="major",
        number=0,
        upright_meaning="新的開始、冒險精神",
        upright_keywords='["開始", "冒險", "自由"]',
        reversed_meaning="魯莽、缺乏計畫",
        reversed_keywords='["魯莽", "停滯"]',
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card


@pytest.fixture
def test_user(db_session):
    user = User(email="reader@example.com", name="Reader")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    return {"Authorization": f"Bearer {create_access_token(test_user)}"}


@pytest.fixture
def divine_payload(seeded_card):
    return {
        "question_text": "我最近的工作運勢如何？",
        "question_type": "career",
        "spread_type": "past_present_future",
        "spread_data": {
            "type": "past_present_future",
            "cards": [
                {
                    "position": pos,
                    "position_order": i,
                    "card_id": seeded_card.id,
                    "card_name": seeded_card.name,
                    "card_name_en": seeded_card.name_en,
                    "is_reversed": False,
                }
                for i, pos in enumerate(["past", "present", "future"])
            ],
        },
    }

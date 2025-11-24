"""AI 解讀服務"""

import json
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.ai.claude_client import ClaudeClient
from app.services.ai.prompts import (
    SYSTEM_PROMPT,
    FOLLOW_UP_SYSTEM_PROMPT,
    build_interpretation_prompt,
)
from app.models.divine import Divine
from app.models.card import Card
from app.models.conversation import Conversation


class AIService:
    """AI 解讀服務"""

    def __init__(self, db: Session):
        self.db = db
        self.claude = ClaudeClient()

    def generate_interpretation(self, divine_id: str) -> Dict[str, Any]:
        """
        生成占卜解讀

        Args:
            divine_id: 占卜記錄 ID

        Returns:
            解讀結果
        """
        # 取得占卜記錄
        divine = self.db.query(Divine).filter(Divine.id == divine_id).first()
        if not divine:
            raise Exception(f"找不到占卜記錄: {divine_id}")

        # 準備卡片資料
        cards_data = self._prepare_cards_data(divine.spread_data)

        # 組裝 Prompt
        user_prompt = build_interpretation_prompt(
            question=divine.question_text,
            spread_type=divine.spread_type,
            cards_data=cards_data,
        )

        # 調用 Claude API
        response = self.claude.generate_interpretation(SYSTEM_PROMPT, user_prompt)

        # 解析 JSON 回應
        interpretation_data = self.claude.parse_json_response(response["content"])

        # 驗證回應結構
        self._validate_interpretation(interpretation_data)

        # 更新占卜記錄
        divine.interpretation = interpretation_data
        divine.is_ai_interpreted = True
        divine.ai_model = self.claude.model
        divine.interpretation_tokens = response["tokens"]["total"]
        divine.interpreted_at = datetime.utcnow()
        self.db.commit()

        # 建立對話記錄
        conversation = Conversation(
            divine_id=divine_id,
            messages=[
                {
                    "role": "system",
                    "content": response["content"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "tokens": response["tokens"]["total"],
                }
            ],
            total_tokens=response["tokens"]["total"],
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return {
            "divine_id": divine_id,
            "interpretation": interpretation_data,
            "conversation_id": conversation.id,
            "metadata": {
                "model": self.claude.model,
                "generated_at": divine.interpreted_at,
                "tokens_used": response["tokens"]["total"],
            },
        }

    def _prepare_cards_data(self, spread_data: Dict[str, Any]) -> list:
        """
        準備卡片資料用於 Prompt

        Args:
            spread_data: 牌陣資料

        Returns:
            卡片資料列表
        """
        cards_data = []

        for card_info in spread_data.get("cards", []):
            # 取得卡片詳細資訊
            card = (
                self.db.query(Card).filter(Card.id == card_info["card_id"]).first()
            )

            if not card:
                continue

            orientation = "正位" if not card_info["is_reversed"] else "逆位"

            # 取得牌義和關鍵字
            if card_info["is_reversed"]:
                meaning = card.reversed_meaning
                keywords_str = card.reversed_keywords
            else:
                meaning = card.upright_meaning
                keywords_str = card.upright_keywords

            # 解析關鍵字（假設儲存為 JSON 陣列字串）
            try:
                keywords = json.loads(keywords_str)
            except:
                keywords = []

            cards_data.append(
                {
                    "position": card_info["position"],
                    "card_name": card.name,
                    "card_name_en": card.name_en,
                    "orientation": orientation,
                    "meaning": meaning,
                    "keywords": keywords,
                }
            )

        return cards_data

    def _validate_interpretation(self, data: Dict[str, Any]) -> None:
        """
        驗證解讀資料結構

        Args:
            data: 解讀資料

        Raises:
            Exception: 如果資料結構不完整
        """
        required_fields = ["overall_summary", "card_interpretations", "advice"]

        for field in required_fields:
            if field not in data:
                raise Exception(f"解讀資料缺少必要欄位: {field}")

        # 驗證 overall_summary 長度
        summary = data["overall_summary"]
        if len(summary) < 50:
            raise Exception("整體解讀內容過短")

        # 驗證 card_interpretations
        if not isinstance(data["card_interpretations"], list):
            raise Exception("card_interpretations 必須是陣列")

    def send_message(self, conversation_id: str, user_message: str) -> Dict[str, Any]:
        """
        發送追問訊息

        Args:
            conversation_id: 對話 ID
            user_message: 用戶訊息

        Returns:
            AI 回應
        """
        # 取得對話記錄
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            raise Exception(f"找不到對話記錄: {conversation_id}")

        # 取得占卜記錄（用於上下文）
        divine = (
            self.db.query(Divine)
            .filter(Divine.id == conversation.divine_id)
            .first()
        )

        # 準備對話歷史
        messages = self._prepare_conversation_messages(conversation, user_message)

        # 調用 Claude API
        response = self.claude.continue_conversation(
            FOLLOW_UP_SYSTEM_PROMPT, messages
        )

        # 更新對話記錄
        conversation.messages.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens": 0,
            }
        )

        conversation.messages.append(
            {
                "role": "assistant",
                "content": response["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "tokens": response["tokens"]["total"],
            }
        )

        conversation.total_tokens += response["tokens"]["total"]
        self.db.commit()

        return {
            "conversation_id": conversation_id,
            "message": {
                "role": "assistant",
                "content": response["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "tokens": response["tokens"]["total"],
            },
            "tokens_used": response["tokens"]["total"],
        }

    def _prepare_conversation_messages(
        self, conversation: Conversation, user_message: str
    ) -> list:
        """
        準備對話訊息列表

        Args:
            conversation: 對話記錄
            user_message: 新的用戶訊息

        Returns:
            訊息列表（Claude API 格式）
        """
        messages = []

        # 跳過第一條 system 訊息（初始解讀）
        for msg in conversation.messages[1:]:
            if msg["role"] in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # 加入新訊息
        messages.append({"role": "user", "content": user_message})

        return messages

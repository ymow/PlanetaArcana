"""AI 解讀服務"""

import json
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.ai.claude_client import ClaudeClient
from app.services.ai.prompts import (
    DAILY_DRAW_SCHEMA,
    DAILY_DRAW_SYSTEM_PROMPT,
    INTERPRETATION_SCHEMA,
    build_daily_draw_prompt,
    build_follow_up_system_prompt,
    build_interpretation_prompt,
    build_system_prompt,
)
from app.models.divine import Divine
from app.models.card import Card
from app.models.conversation import Conversation
from app.models.daily_draw import DailyDraw


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
            options=(divine.spread_data or {}).get("options"),
        )

        # 調用 Claude API（結構化輸出保證回應為合法 JSON）
        response = self.claude.generate_interpretation(
            build_system_prompt(divine.persona_id),
            user_prompt,
            output_schema=INTERPRETATION_SCHEMA,
        )

        return self._finalize_interpretation(
            divine, response["content"], response["tokens"]
        )

    def stream_interpretation(self, divine_id: str):
        """
        以串流方式生成占卜解讀。

        Yields:
            {"event": "delta", "data": {"text": "..."}} — 生成中的逐段文字
            {"event": "complete", "data": {...}} — 驗證與持久化完成後的完整解讀

        中斷或驗證失敗時不會持久化任何內容（與非串流路徑行為一致）。
        """
        divine = self.db.query(Divine).filter(Divine.id == divine_id).first()
        if not divine:
            raise Exception(f"找不到占卜記錄: {divine_id}")

        cards_data = self._prepare_cards_data(divine.spread_data)
        user_prompt = build_interpretation_prompt(
            question=divine.question_text,
            spread_type=divine.spread_type,
            cards_data=cards_data,
            options=(divine.spread_data or {}).get("options"),
        )

        final = None
        for chunk in self.claude.stream_interpretation(
            build_system_prompt(divine.persona_id),
            user_prompt,
            output_schema=INTERPRETATION_SCHEMA,
        ):
            if chunk["type"] == "delta":
                yield {"event": "delta", "data": {"text": chunk["text"]}}
            else:
                final = chunk

        if not final:
            raise Exception("串流未回傳完整解讀")

        result = self._finalize_interpretation(
            divine, final["content"], final["tokens"]
        )
        yield {"event": "complete", "data": result}

    def _finalize_interpretation(
        self, divine: Divine, content: str, tokens: Dict[str, int]
    ) -> Dict[str, Any]:
        """解析、驗證並持久化解讀結果（串流與非串流共用）。"""
        interpretation_data = self.claude.parse_json_response(content)
        self._validate_interpretation(interpretation_data)

        # 更新占卜記錄
        divine.interpretation = interpretation_data
        divine.is_ai_interpreted = True
        divine.ai_model = self.claude.model
        divine.interpretation_tokens = tokens["total"]
        divine.interpreted_at = datetime.utcnow()
        self.db.commit()

        # 建立或重設對話記錄（divine_id 有 unique 約束，重新解讀時必須沿用同一筆）
        initial_message = {
            "role": "assistant",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "tokens": tokens["total"],
        }

        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.divine_id == divine.id)
            .first()
        )

        if conversation:
            conversation.messages = [initial_message]
            conversation.total_tokens = tokens["total"]
        else:
            conversation = Conversation(
                divine_id=divine.id,
                messages=[initial_message],
                total_tokens=tokens["total"],
                user_id=divine.user_id,
            )
            self.db.add(conversation)

        conversation.user_id = divine.user_id
        self.db.commit()
        self.db.refresh(conversation)

        return {
            "divine_id": divine.id,
            "interpretation": interpretation_data,
            "conversation_id": conversation.id,
            "metadata": {
                "model": self.claude.model,
                "generated_at": divine.interpreted_at,
                "tokens_used": tokens["total"],
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
            except (json.JSONDecodeError, TypeError):
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

        # 準備對話歷史（包含原始占卜脈絡與初始解讀）
        messages = self._prepare_conversation_messages(
            conversation, divine, user_message
        )

        # 調用 Claude API（沿用該占卜的角色,避免追問「變聲」）
        response = self.claude.continue_conversation(
            build_follow_up_system_prompt(divine.persona_id if divine else None),
            messages,
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
        self, conversation: Conversation, divine: Divine, user_message: str
    ) -> list:
        """
        準備對話訊息列表

        追問時必須讓模型看到完整脈絡：
        原始占卜資訊（user）→ 初始解讀（assistant）→ 後續追問往返 → 新訊息

        Args:
            conversation: 對話記錄
            divine: 占卜記錄（用於重建原始占卜脈絡）
            user_message: 新的用戶訊息

        Returns:
            訊息列表（Claude API 格式）
        """
        messages = []

        # 重建原始占卜的 user prompt，讓追問擁有牌陣與問題脈絡
        if divine:
            cards_data = self._prepare_cards_data(divine.spread_data)
            original_prompt = build_interpretation_prompt(
                question=divine.question_text,
                spread_type=divine.spread_type,
                cards_data=cards_data,
                options=(divine.spread_data or {}).get("options"),
            )
            messages.append({"role": "user", "content": original_prompt})

        stored = conversation.messages or []

        # 第一條是初始解讀（新資料為 assistant；舊資料曾以 system 儲存）
        if stored:
            messages.append({"role": "assistant", "content": stored[0]["content"]})

        # 後續的追問往返
        for msg in stored[1:]:
            if msg["role"] in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # 加入新訊息
        messages.append({"role": "user", "content": user_message})

        return messages

    def generate_daily_draw(
        self, user_id: str, draw_date: str, card: Card, is_reversed: bool
    ) -> DailyDraw:
        """生成並儲存登入使用者的每日一牌。"""
        card_data = self._prepare_single_card_data(card, is_reversed)
        user_prompt = build_daily_draw_prompt(card_data)

        response = self.claude.generate_interpretation(
            DAILY_DRAW_SYSTEM_PROMPT, user_prompt, output_schema=DAILY_DRAW_SCHEMA
        )
        interpretation_data = self.claude.parse_json_response(response["content"])
        self._validate_daily_draw(interpretation_data)

        draw = DailyDraw(
            user_id=user_id,
            draw_date=draw_date,
            card_id=card.id,
            card_name=card.name,
            card_name_en=card.name_en,
            is_reversed=is_reversed,
            interpretation=interpretation_data,
            ai_model=self.claude.model,
            interpretation_tokens=response["tokens"]["total"],
        )
        self.db.add(draw)
        self.db.commit()
        self.db.refresh(draw)
        return draw

    def _prepare_single_card_data(self, card: Card, is_reversed: bool) -> Dict[str, Any]:
        orientation = "正位" if not is_reversed else "逆位"
        meaning = card.upright_meaning if not is_reversed else card.reversed_meaning
        keywords_str = card.upright_keywords if not is_reversed else card.reversed_keywords

        try:
            keywords = json.loads(keywords_str)
        except (json.JSONDecodeError, TypeError):
            keywords = []

        return {
            "card_name": card.name,
            "card_name_en": card.name_en,
            "orientation": orientation,
            "meaning": meaning,
            "keywords": keywords,
        }

    def _validate_daily_draw(self, data: Dict[str, Any]) -> None:
        required_fields = ["key_theme", "summary", "advice", "reflection_prompt"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"每日一牌資料缺少必要欄位: {field}")
        if len(data["summary"]) < 20:
            raise Exception("每日一牌內容過短")

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QuestionData(BaseModel):
    """問題資料"""

    text: str = Field(..., description="問題內容")
    type: Optional[str] = Field(None, description="問題類型")
    category: Optional[str] = Field(None, description="問題分類")


class CardInSpread(BaseModel):
    """牌陣中的卡片"""

    position: str = Field(..., description="位置名稱（如 past, present, future）")
    position_order: int = Field(..., description="位置順序")
    card_id: str = Field(..., description="卡片 ID")
    card_name: str = Field(..., description="卡片名稱")
    card_name_en: str = Field(..., description="卡片英文名稱")
    is_reversed: bool = Field(False, description="是否逆位")


class SpreadData(BaseModel):
    """牌陣資料"""

    type: str = Field("past_present_future", description="牌陣類型")
    cards: List[CardInSpread] = Field(..., description="卡片列表")


class DivineBase(BaseModel):
    """Divine 基礎 Schema"""

    question_text: str = Field(..., description="問題內容")
    question_type: Optional[str] = Field(None, description="問題類型")
    question_category: Optional[str] = Field(None, description="問題分類")
    spread_type: str = Field("past_present_future", description="牌陣類型")
    spread_data: Dict[str, Any] = Field(..., description="牌陣資料（JSON）")
    persona_id: Optional[str] = Field(None, description="解讀角色 ID（未提供時使用預設角色）")


class DivineCreate(DivineBase):
    """建立 Divine 的 Schema"""

    pass


class DivineUpdate(BaseModel):
    """更新 Divine 的 Schema"""

    question_text: Optional[str] = None
    question_type: Optional[str] = None
    question_category: Optional[str] = None
    interpretation: Optional[Dict[str, Any]] = None


class Divine(DivineBase):
    """Divine 完整 Schema"""

    id: str
    interpretation: Optional[Dict[str, Any]] = None
    is_ai_interpreted: bool = False
    ai_model: Optional[str] = None
    interpretation_tokens: Optional[int] = None
    interpreted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


# AI 解讀相關 Schemas


class CardInterpretation(BaseModel):
    """單張卡片解讀"""

    position: str = Field(..., description="位置")
    card_name: str = Field(..., description="卡片名稱（含正逆位）")
    interpretation: str = Field(..., description="解讀內容")


class InterpretationData(BaseModel):
    """解讀資料"""

    overall_summary: str = Field(..., description="整體解讀")
    card_interpretations: List[CardInterpretation] = Field(..., description="單卡解讀")
    advice: str = Field(..., description="建議")
    key_insights: Optional[List[str]] = Field(None, description="關鍵洞察")


class InterpretationRequest(BaseModel):
    """請求 AI 解讀"""

    interpretation_type: str = Field("initial", description="解讀類型：initial 或 follow_up")
    user_message: Optional[str] = Field(None, description="追問訊息（follow_up 時使用）")


class InterpretationMetadata(BaseModel):
    """解讀元數據"""

    model: str = Field(..., description="使用的 AI 模型")
    generated_at: datetime = Field(..., description="生成時間")
    tokens_used: int = Field(..., description="使用的 token 數")
    conversation_id: Optional[str] = Field(None, description="對話 ID")


class InterpretationResponse(BaseModel):
    """AI 解讀回應"""

    divine_id: str
    interpretation: InterpretationData
    conversation_id: Optional[str] = None
    metadata: InterpretationMetadata

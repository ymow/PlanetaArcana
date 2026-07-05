"""牌陣 Schema"""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class SpreadPosition(BaseModel):
    """牌陣中的一個位置"""

    key: str
    name: str
    description: str


class SpreadInfo(BaseModel):
    """牌陣展示資訊"""

    id: str
    name: str
    description: str
    card_count: int
    requires_options: bool = False
    positions: List[SpreadPosition]


class SpreadRecommendationRequest(BaseModel):
    """牌陣推薦請求"""

    question_text: str = Field(..., min_length=1, max_length=500)
    options: Optional[Dict[str, str]] = None

    @field_validator("question_text")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("question_text must not be blank")
        return question


class SpreadRecommendation(BaseModel):
    """自動選牌陣結果"""

    spread_id: str
    spread_name: str
    description: str
    card_count: int
    requires_options: bool
    positions: List[SpreadPosition]
    reason: str
    confidence: Literal["high", "medium", "fallback"]
    matched_rule: str

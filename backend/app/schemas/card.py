from pydantic import BaseModel, Field
from typing import Optional, List


class CardBase(BaseModel):
    """Card 基礎 Schema"""

    name: str = Field(..., description="中文名稱")
    name_en: str = Field(..., description="英文名稱")
    type: str = Field(..., description="卡片類型：major 或 minor")
    suit: Optional[str] = Field(None, description="花色（小阿爾克那）")
    rank: Optional[str] = Field(None, description="等級")
    number: Optional[int] = Field(None, description="編號")

    upright_meaning: str = Field(..., description="正位牌義")
    upright_keywords: str = Field(..., description="正位關鍵字（JSON 陣列字串）")

    reversed_meaning: str = Field(..., description="逆位牌義")
    reversed_keywords: str = Field(..., description="逆位關鍵字（JSON 陣列字串）")

    symbolism: Optional[str] = Field(None, description="象徵意義")
    description: Optional[str] = Field(None, description="卡片描述")
    image_url: Optional[str] = Field(None, description="圖片 URL")


class CardCreate(CardBase):
    """建立 Card 的 Schema"""

    pass


class CardUpdate(BaseModel):
    """更新 Card 的 Schema（所有欄位可選）"""

    name: Optional[str] = None
    name_en: Optional[str] = None
    type: Optional[str] = None
    suit: Optional[str] = None
    rank: Optional[str] = None
    number: Optional[int] = None
    upright_meaning: Optional[str] = None
    upright_keywords: Optional[str] = None
    reversed_meaning: Optional[str] = None
    reversed_keywords: Optional[str] = None
    symbolism: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class Card(CardBase):
    """Card 完整 Schema（含 ID）"""

    id: str

    class Config:
        from_attributes = True

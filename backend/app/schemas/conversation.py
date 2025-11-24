from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class Message(BaseModel):
    """對話訊息"""

    role: str = Field(..., description="角色：system, user, assistant")
    content: str = Field(..., description="訊息內容")
    timestamp: datetime = Field(..., description="時間戳記")
    tokens: int = Field(0, description="使用的 token 數")


class ConversationBase(BaseModel):
    """Conversation 基礎 Schema"""

    divine_id: str = Field(..., description="關聯的占卜 ID")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="訊息列表")
    total_tokens: int = Field(0, description="總 token 數")


class Conversation(ConversationBase):
    """Conversation 完整 Schema"""

    id: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """發送訊息請求"""

    message: str = Field(..., description="用戶訊息")


class MessageResponse(BaseModel):
    """訊息回應"""

    conversation_id: str
    message: Message
    tokens_used: int


from typing import Optional

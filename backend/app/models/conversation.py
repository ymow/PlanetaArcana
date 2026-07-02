from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
import uuid
from app.db.database import Base


class Conversation(Base):
    """對話記錄 Model - 用於 AI 解讀追問"""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 關聯的占卜記錄（一個占卜對應一個對話）
    divine_id = Column(String(36), ForeignKey("divines.id"), unique=True, nullable=False)

    # 對話訊息（JSON 陣列）
    # MutableList 讓 SQLAlchemy 能偵測 append 等就地修改，否則 commit 不會寫入
    messages = Column(MutableList.as_mutable(JSON), nullable=False, default=list)
    # 格式：[{"role": "system/user/assistant", "content": "...", "timestamp": "...", "tokens": 123}]

    # Token 使用統計
    total_tokens = Column(Integer, default=0)

    # 時間戳記
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 用戶 ID (Phase 2)
    user_id = Column(String(36), nullable=True)

    def __repr__(self):
        return f"<Conversation {self.id} for Divine {self.divine_id}>"

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON
from datetime import datetime
import uuid
from app.db.database import Base


class Divine(Base):
    """占卜記錄 Model"""

    __tablename__ = "divines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 問題資訊
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True)  # personal, relationship, career, etc.
    question_category = Column(String(50), nullable=True)

    # 牌陣資訊
    spread_type = Column(String(50), nullable=False, default="past_present_future")
    spread_data = Column(JSON, nullable=False)  # 完整的牌陣資料（包含卡片、位置等）

    # AI 解讀
    interpretation = Column(JSON, nullable=True)  # AI 生成的解讀結果
    is_ai_interpreted = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    interpretation_tokens = Column(Integer, nullable=True)
    interpreted_at = Column(DateTime, nullable=True)

    # 時間戳記
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 用戶 ID (Phase 2 - 身份驗證)
    user_id = Column(String(36), nullable=True)

    def __repr__(self):
        return f"<Divine {self.id}: {self.question_text[:30]}...>"

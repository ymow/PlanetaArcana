from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Boolean, UniqueConstraint

from app.db.database import Base


class DailyDraw(Base):
    """每日一牌 Model"""

    __tablename__ = "daily_draws"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    draw_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD, app timezone

    card_id = Column(String(36), ForeignKey("cards.id"), nullable=False)
    card_name = Column(String(100), nullable=False)
    card_name_en = Column(String(100), nullable=False)
    is_reversed = Column(Boolean, default=False, nullable=False)

    interpretation = Column(JSON, nullable=False)
    ai_model = Column(String(100), nullable=True)
    interpretation_tokens = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "draw_date", name="uq_daily_draw_user_date"),
    )

    def __repr__(self):
        return f"<DailyDraw {self.user_id} {self.draw_date}: {self.card_name}>"

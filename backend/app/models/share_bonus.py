from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.db.database import Base


class ShareBonus(Base):
    """分享加額稽核記錄 — 每筆代表一次「分享占卜 +1 當日配額」的領取

    quota_key 與 ApiUsage.client_ip 同格式（ip:<ip> 或 user:<user_id>）。
    同一 quota_key 對同一占卜只能領取一次（防重複領取）。
    """

    __tablename__ = "share_bonus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quota_key = Column(String(64), nullable=False, index=True)
    bonus_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD (UTC)
    divine_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("quota_key", "divine_id", name="uq_share_bonus_key_divine"),
    )

    def __repr__(self):
        return f"<ShareBonus {self.quota_key} {self.bonus_date} divine={self.divine_id}>"

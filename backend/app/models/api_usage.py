from sqlalchemy import Column, String, Integer, UniqueConstraint
from app.db.database import Base


class ApiUsage(Base):
    """AI 端點每日用量記錄 — client_ip 儲存 ip:<ip> 或 user:<user_id> quota key"""

    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_ip = Column(String(64), nullable=False, index=True)
    usage_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD (UTC)
    count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("client_ip", "usage_date", name="uq_api_usage_ip_date"),
    )

    def __repr__(self):
        return f"<ApiUsage {self.client_ip} {self.usage_date}: {self.count}>"

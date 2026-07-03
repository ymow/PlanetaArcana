"""配額狀態與分享加額 Schemas"""

from typing import Optional

from pydantic import BaseModel


class QuotaStatus(BaseModel):
    """當日 AI 配額狀態"""

    daily_limit: int
    share_bonus: int
    used: int
    remaining: int


class ShareBonusResult(BaseModel):
    """分享加額領取結果"""

    granted: bool
    reason: Optional[str] = None
    quota: QuotaStatus

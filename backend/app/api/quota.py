"""AI 配額狀態 API"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth import get_optional_user
from app.core.rate_limit import get_quota_status
from app.db.database import get_db
from app.models.user import User
from app.schemas.quota import QuotaStatus

router = APIRouter(prefix="/quota", tags=["Quota"])


@router.get("", response_model=QuotaStatus)
def read_quota_status(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """取得今日 AI 配額狀態（登入者依帳號計，匿名依 IP 計）。"""
    return get_quota_status(request, db, current_user)

"""AI 端點限流 — 每分鐘突發保護 + 每日用量上限（成本保護）"""

import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.auth import get_optional_user
from app.core.config import settings
from app.db.database import get_db
from app.models.api_usage import ApiUsage
from app.models.share_bonus import ShareBonus
from app.models.user import User

# 每 IP 最近呼叫時間的滑動視窗（單 process 內有效；多 worker 部署時每 worker 各自計算，
# 屬突發緩衝而非精確上限 — 精確的成本保護由資料庫每日配額負責）
_recent_calls: dict = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def reset_burst_window() -> None:
    """清空滑動視窗（測試用）"""
    _recent_calls.clear()


def _quota_key(request: Request, current_user: User | None) -> str:
    if current_user:
        return f"user:{current_user.id}"
    return f"ip:{_client_ip(request)}"


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _share_bonus_count(db: Session, key: str, today: str) -> int:
    return (
        db.query(ShareBonus)
        .filter(ShareBonus.quota_key == key, ShareBonus.bonus_date == today)
        .count()
    )


def get_quota_status(request: Request, db: Session, current_user: User | None) -> dict:
    """目前配額狀態：基本上限 + 今日分享加額 - 已用次數。"""
    key = _quota_key(request, current_user)
    today = _today_utc()
    usage = (
        db.query(ApiUsage)
        .filter(ApiUsage.client_ip == key, ApiUsage.usage_date == today)
        .first()
    )
    used = usage.count if usage else 0
    bonus = _share_bonus_count(db, key, today)
    return {
        "daily_limit": settings.AI_DAILY_LIMIT,
        "share_bonus": bonus,
        "used": used,
        "remaining": max(0, settings.AI_DAILY_LIMIT + bonus - used),
    }


def grant_share_bonus(
    request: Request, db: Session, current_user: User | None, divine_id: str
) -> tuple[bool, str | None]:
    """
    領取「分享 +1 當日配額」。

    防重複領取：同一 quota key 對同一占卜只能領取一次（DB unique constraint 稽核），
    且每日加額不得超過 AI_SHARE_BONUS_DAILY_MAX。
    回傳 (granted, 未發放原因)。
    """
    key = _quota_key(request, current_user)
    today = _today_utc()

    already = (
        db.query(ShareBonus)
        .filter(ShareBonus.quota_key == key, ShareBonus.divine_id == divine_id)
        .first()
    )
    if already:
        return False, "此占卜已領取過分享加額"

    if _share_bonus_count(db, key, today) >= settings.AI_SHARE_BONUS_DAILY_MAX:
        return False, f"已達每日分享加額上限（{settings.AI_SHARE_BONUS_DAILY_MAX} 次）"

    db.add(ShareBonus(quota_key=key, bonus_date=today, divine_id=divine_id))
    db.commit()
    return True, None


def consume_ai_quota(
    request: Request, db: Session, current_user: User | None = None
) -> None:
    """
    消耗一次 AI 配額。

    兩層保護：
    1. 每分鐘突發限制（in-memory 滑動視窗;登入者依 user_id,匿名依 IP）
    2. 每日用量上限（資料庫計數，重啟不歸零）

    超限回傳 429。用量在請求進入時即計數（計「嘗試」而非「成功」，
    避免故意觸發錯誤來繞過配額）。
    """
    key = _quota_key(request, current_user)

    # 第一層：每分鐘突發限制
    now = time.monotonic()
    window = _recent_calls[key]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.AI_RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="請求過於頻繁，請稍後再試",
            headers={"Retry-After": "60"},
        )

    # 第二層：每日用量上限（基本上限 + 今日分享加額）
    today = _today_utc()
    usage = (
        db.query(ApiUsage)
        .filter(ApiUsage.client_ip == key, ApiUsage.usage_date == today)
        .first()
    )

    daily_limit = settings.AI_DAILY_LIMIT + _share_bonus_count(db, key, today)
    if usage and usage.count >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"已達每日解讀次數上限（{daily_limit} 次），分享占卜可獲得額外次數，或明天再來",
            headers={"Retry-After": "86400"},
        )

    if usage:
        usage.count += 1
    else:
        db.add(ApiUsage(client_ip=key, usage_date=today, count=1))
    db.commit()

    window.append(now)


def enforce_ai_quota(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> None:
    """AI 端點共用的限流 dependency。"""
    consume_ai_quota(request, db, current_user)

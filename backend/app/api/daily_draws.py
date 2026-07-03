"""每日一牌 API"""

import random
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.rate_limit import consume_ai_quota
from app.db.database import get_db
from app.models.card import Card
from app.models.daily_draw import DailyDraw
from app.models.user import User
from app.schemas.daily_draw import DailyDraw as DailyDrawSchema
from app.services.ai import AIService

router = APIRouter(prefix="/daily-draws", tags=["Daily Draws"])


def _today() -> str:
    return datetime.now(ZoneInfo(settings.APP_TIMEZONE)).strftime("%Y-%m-%d")


def _get_today_draw(db: Session, user_id: str) -> DailyDraw | None:
    return (
        db.query(DailyDraw)
        .filter(DailyDraw.user_id == user_id, DailyDraw.draw_date == _today())
        .first()
    )


@router.get("/today", response_model=DailyDrawSchema)
def get_today_draw(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draw = _get_today_draw(db, current_user.id)
    if not draw:
        raise HTTPException(status_code=404, detail="今日尚未抽牌")
    return draw


@router.post("/today", response_model=DailyDrawSchema, status_code=201)
def create_today_draw(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = _get_today_draw(db, current_user.id)
    if existing:
        response.status_code = 200
        return existing

    consume_ai_quota(request, db, current_user)

    cards = db.query(Card).all()
    if not cards:
        raise HTTPException(status_code=503, detail="尚未初始化塔羅牌資料")

    card = random.choice(cards)
    is_reversed = random.random() > 0.5

    try:
        return AIService(db).generate_daily_draw(current_user.id, _today(), card, is_reversed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"每日一牌生成失敗: {str(e)}")

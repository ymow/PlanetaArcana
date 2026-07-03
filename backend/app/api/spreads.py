"""牌陣目錄 API"""

from typing import List

from fastapi import APIRouter

from app.schemas.spread import SpreadInfo
from app.services.ai.prompts import SPREADS

router = APIRouter(prefix="/spreads", tags=["Spreads"])


@router.get("", response_model=List[SpreadInfo])
def get_spreads():
    """取得所有牌陣的展示資訊（response_model 過濾掉 reading_focus 等 prompt 細節）。"""
    return [
        {**spread, "card_count": len(spread["positions"])}
        for spread in SPREADS.values()
    ]

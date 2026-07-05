"""牌陣目錄 API"""

from typing import List

from fastapi import APIRouter

from app.schemas.spread import (
    SpreadInfo,
    SpreadRecommendation,
    SpreadRecommendationRequest,
)
from app.services.spread_recommender import recommend_spread
from app.services.ai.prompts import SPREADS

router = APIRouter(prefix="/spreads", tags=["Spreads"])


@router.get("", response_model=List[SpreadInfo])
def get_spreads():
    """取得所有牌陣的展示資訊（response_model 過濾掉 reading_focus 等 prompt 細節）。"""
    return [
        {**spread, "card_count": len(spread["positions"])}
        for spread in SPREADS.values()
    ]


@router.post("/recommend", response_model=SpreadRecommendation)
def recommend_spread_for_question(request: SpreadRecommendationRequest):
    """依問題內容推薦最適合的已上線牌陣。"""
    return recommend_spread(request.question_text, request.options)

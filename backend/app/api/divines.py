"""占卜記錄 CRUD API"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.auth import get_current_user, get_optional_user
from app.core.rate_limit import enforce_ai_quota, get_quota_status, grant_share_bonus
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.divine import Divine
from app.models.user import User
from app.schemas.divine import (
    Divine as DivineSchema,
    DivineCreate,
    DivineUpdate,
    InterpretationRequest,
    InterpretationResponse,
)
from app.schemas.quota import ShareBonusResult
from app.services.ai import AIService
from app.services.ai.prompts import DEFAULT_PERSONA_ID, PERSONAS

router = APIRouter(prefix="/divines", tags=["Divines"])


def _ensure_divine_access(divine: Divine, current_user: Optional[User]) -> None:
    if divine.user_id and (not current_user or divine.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")


@router.get("", response_model=List[DivineSchema])
def get_divines(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    取得占卜列表

    - **skip**: 略過筆數（分頁用）
    - **limit**: 限制筆數
    - **user_id**: 過濾特定用戶（Phase 2）
    """
    query = db.query(Divine)

    if current_user:
        query = query.filter(Divine.user_id == current_user.id)
    elif user_id:
        raise HTTPException(status_code=401, detail="請先登入")
    else:
        query = query.filter(Divine.user_id.is_(None))

    # 依建立時間降序排列
    divines = query.order_by(Divine.created_at.desc()).offset(skip).limit(limit).all()
    return divines


@router.get("/{divine_id}", response_model=DivineSchema)
def get_divine(
    divine_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    取得特定占卜記錄

    - **divine_id**: 占卜 ID
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    return divine


@router.post("", response_model=DivineSchema, status_code=201)
def create_divine(
    divine_data: DivineCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    建立新占卜記錄

    - **divine_data**: 占卜資料（persona_id 未提供時使用預設角色）
    """
    if divine_data.persona_id is None:
        divine_data.persona_id = DEFAULT_PERSONA_ID
    elif divine_data.persona_id not in PERSONAS:
        raise HTTPException(status_code=422, detail="未知的解讀角色")

    divine = Divine(**divine_data.model_dump(), user_id=current_user.id if current_user else None)
    db.add(divine)
    db.commit()
    db.refresh(divine)

    return divine


@router.put("/{divine_id}", response_model=DivineSchema)
def update_divine(
    divine_id: str,
    divine_data: DivineUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    更新占卜記錄

    - **divine_id**: 占卜 ID
    - **divine_data**: 更新的資料
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    # 更新欄位
    update_data = divine_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(divine, field, value)

    db.commit()
    db.refresh(divine)

    return divine


@router.delete("/{divine_id}", status_code=204)
def delete_divine(
    divine_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    刪除占卜記錄

    - **divine_id**: 占卜 ID
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    db.delete(divine)
    db.commit()

    return None


@router.post("/{divine_id}/claim", response_model=DivineSchema)
def claim_divine(
    divine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """將匿名占卜綁定到目前登入使用者。"""
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    if divine.user_id and divine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")

    divine.user_id = current_user.id
    conversation = (
        db.query(Conversation).filter(Conversation.divine_id == divine_id).first()
    )
    if conversation:
        conversation.user_id = current_user.id

    db.commit()
    db.refresh(divine)
    return divine


@router.post("/{divine_id}/share", response_model=ShareBonusResult)
def share_divine(
    divine_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    記錄一次占卜分享並領取「+1 當日解讀配額」。

    同一使用者（或匿名 IP）對同一占卜只能領取一次，
    且每日加額有上限（AI_SHARE_BONUS_DAILY_MAX）。
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    granted, reason = grant_share_bonus(request, db, current_user, divine_id)
    return {
        "granted": granted,
        "reason": reason,
        "quota": get_quota_status(request, db, current_user),
    }


@router.post(
    "/{divine_id}/interpret",
    response_model=InterpretationResponse,
    dependencies=[Depends(enforce_ai_quota)],
)
def interpret_divine(
    divine_id: str,
    request: InterpretationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    生成 AI 解讀

    - **divine_id**: 占卜 ID
    - **interpretation_type**: 解讀類型（initial/follow_up）
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    # 初始化 AI 服務
    ai_service = AIService(db)

    try:
        # 生成解讀
        result = ai_service.generate_interpretation(divine_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 解讀失敗: {str(e)}")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


@router.post(
    "/{divine_id}/interpret/stream",
    dependencies=[Depends(enforce_ai_quota)],
)
def interpret_divine_stream(
    divine_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    以 SSE 串流生成 AI 解讀。

    事件：`delta`（逐段文字）→ `complete`（驗證與持久化後的完整解讀）；
    失敗時發出 `error`。中斷或失敗不會持久化任何內容，重試即重新生成。
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")
    _ensure_divine_access(divine, current_user)

    ai_service = AIService(db)

    def event_stream():
        try:
            for event in ai_service.stream_interpretation(divine_id):
                yield _sse(event["event"], event["data"])
        except Exception as e:
            yield _sse("error", {"detail": f"AI 解讀失敗: {str(e)}"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

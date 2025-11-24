"""占卜記錄 CRUD API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.divine import Divine
from app.schemas.divine import (
    Divine as DivineSchema,
    DivineCreate,
    DivineUpdate,
    InterpretationRequest,
    InterpretationResponse,
)
from app.services.ai import AIService

router = APIRouter(prefix="/divines", tags=["Divines"])


@router.get("", response_model=List[DivineSchema])
def get_divines(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    取得占卜列表

    - **skip**: 略過筆數（分頁用）
    - **limit**: 限制筆數
    - **user_id**: 過濾特定用戶（Phase 2）
    """
    query = db.query(Divine)

    if user_id:
        query = query.filter(Divine.user_id == user_id)

    # 依建立時間降序排列
    divines = query.order_by(Divine.created_at.desc()).offset(skip).limit(limit).all()
    return divines


@router.get("/{divine_id}", response_model=DivineSchema)
def get_divine(divine_id: str, db: Session = Depends(get_db)):
    """
    取得特定占卜記錄

    - **divine_id**: 占卜 ID
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")

    return divine


@router.post("", response_model=DivineSchema, status_code=201)
def create_divine(divine_data: DivineCreate, db: Session = Depends(get_db)):
    """
    建立新占卜記錄

    - **divine_data**: 占卜資料
    """
    divine = Divine(**divine_data.model_dump())
    db.add(divine)
    db.commit()
    db.refresh(divine)

    return divine


@router.put("/{divine_id}", response_model=DivineSchema)
def update_divine(
    divine_id: str, divine_data: DivineUpdate, db: Session = Depends(get_db)
):
    """
    更新占卜記錄

    - **divine_id**: 占卜 ID
    - **divine_data**: 更新的資料
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")

    # 更新欄位
    update_data = divine_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(divine, field, value)

    db.commit()
    db.refresh(divine)

    return divine


@router.delete("/{divine_id}", status_code=204)
def delete_divine(divine_id: str, db: Session = Depends(get_db)):
    """
    刪除占卜記錄

    - **divine_id**: 占卜 ID
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")

    db.delete(divine)
    db.commit()

    return None


@router.post("/{divine_id}/interpret", response_model=InterpretationResponse)
def interpret_divine(
    divine_id: str,
    request: InterpretationRequest,
    db: Session = Depends(get_db),
):
    """
    生成 AI 解讀

    - **divine_id**: 占卜 ID
    - **interpretation_type**: 解讀類型（initial/follow_up）
    """
    divine = db.query(Divine).filter(Divine.id == divine_id).first()

    if not divine:
        raise HTTPException(status_code=404, detail="找不到該占卜記錄")

    # 初始化 AI 服務
    ai_service = AIService(db)

    try:
        # 生成解讀
        result = ai_service.generate_interpretation(divine_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 解讀失敗: {str(e)}")

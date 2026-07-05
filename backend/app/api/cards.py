"""塔羅牌 CRUD API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.card import Card
from app.schemas.card import Card as CardSchema, CardCreate, CardUpdate
from app.services.card_slug import build_card_slug_from_mapping

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("", response_model=List[CardSchema])
def get_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = None,
    suit: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    取得塔羅牌列表

    - **skip**: 略過筆數（分頁用）
    - **limit**: 限制筆數
    - **type**: 過濾類型（major/minor）
    - **suit**: 過濾花色（wands/cups/swords/pentacles）
    """
    query = db.query(Card)

    if type:
        query = query.filter(Card.type == type)

    if suit:
        query = query.filter(Card.suit == suit)

    cards = query.offset(skip).limit(limit).all()
    return cards


@router.get("/{card_id}", response_model=CardSchema)
def get_card(card_id: str, db: Session = Depends(get_db)):
    """
    取得特定塔羅牌

    - **card_id**: 卡片 ID
    """
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="找不到該卡片")

    return card


@router.post("", response_model=CardSchema, status_code=201)
def create_card(card_data: CardCreate, db: Session = Depends(get_db)):
    """
    建立新塔羅牌（管理用）

    - **card_data**: 卡片資料
    """
    # 檢查是否已存在
    data = card_data.model_dump()
    if not data.get("slug"):
        data["slug"] = build_card_slug_from_mapping(data)

    existing = (
        db.query(Card)
        .filter(
            (Card.name == data["name"])
            | (Card.name_en == data["name_en"])
            | (Card.slug == data["slug"])
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="該卡片已存在")

    # 建立新卡片
    card = Card(**data)
    db.add(card)
    db.commit()
    db.refresh(card)

    return card


@router.put("/{card_id}", response_model=CardSchema)
def update_card(card_id: str, card_data: CardUpdate, db: Session = Depends(get_db)):
    """
    更新塔羅牌（管理用）

    - **card_id**: 卡片 ID
    - **card_data**: 更新的資料
    """
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="找不到該卡片")

    # 更新欄位
    update_data = card_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)

    db.commit()
    db.refresh(card)

    return card


@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: str, db: Session = Depends(get_db)):
    """
    刪除塔羅牌（管理用）

    - **card_id**: 卡片 ID
    """
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="找不到該卡片")

    db.delete(card)
    db.commit()

    return None

"""對話記錄 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversation import Conversation
from app.schemas.conversation import (
    Conversation as ConversationSchema,
    MessageRequest,
    MessageResponse,
)
from app.services.ai import AIService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/{conversation_id}", response_model=ConversationSchema)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    取得對話歷史

    - **conversation_id**: 對話 ID
    """
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="找不到該對話記錄")

    return conversation


@router.post("/{conversation_id}/message", response_model=MessageResponse)
def send_message(
    conversation_id: str,
    request: MessageRequest,
    db: Session = Depends(get_db),
):
    """
    發送追問訊息

    - **conversation_id**: 對話 ID
    - **message**: 用戶訊息
    """
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="找不到該對話記錄")

    # 初始化 AI 服務
    ai_service = AIService(db)

    try:
        # 發送訊息
        result = ai_service.send_message(conversation_id, request.message)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"訊息發送失敗: {str(e)}")


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    刪除對話記錄

    - **conversation_id**: 對話 ID
    """
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="找不到該對話記錄")

    db.delete(conversation)
    db.commit()

    return None

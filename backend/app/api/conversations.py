"""對話記錄 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_optional_user
from app.core.rate_limit import enforce_ai_quota
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.conversation import (
    Conversation as ConversationSchema,
    MessageRequest,
    MessageResponse,
)
from app.services.ai import AIService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _ensure_conversation_access(
    conversation: Conversation, current_user: User | None
) -> None:
    if conversation.user_id and (
        not current_user or conversation.user_id != current_user.id
    ):
        raise HTTPException(status_code=404, detail="找不到該對話記錄")


@router.get("/{conversation_id}", response_model=ConversationSchema)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """
    取得對話歷史

    - **conversation_id**: 對話 ID
    """
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="找不到該對話記錄")
    _ensure_conversation_access(conversation, current_user)

    return conversation


@router.post(
    "/{conversation_id}/message",
    response_model=MessageResponse,
    dependencies=[Depends(enforce_ai_quota)],
)
def send_message(
    conversation_id: str,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
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
    _ensure_conversation_access(conversation, current_user)

    # 初始化 AI 服務
    ai_service = AIService(db)

    try:
        # 發送訊息
        result = ai_service.send_message(conversation_id, request.message)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"訊息發送失敗: {str(e)}")


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """
    刪除對話記錄

    - **conversation_id**: 對話 ID
    """
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="找不到該對話記錄")
    _ensure_conversation_access(conversation, current_user)

    db.delete(conversation)
    db.commit()

    return None

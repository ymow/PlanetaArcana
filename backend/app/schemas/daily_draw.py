from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel


class DailyDraw(BaseModel):
    id: str
    user_id: str
    draw_date: str
    card_id: str
    card_name: str
    card_name_en: str
    is_reversed: bool
    interpretation: Dict[str, Any]
    ai_model: Optional[str] = None
    interpretation_tokens: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

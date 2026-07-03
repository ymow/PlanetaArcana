"""解讀角色目錄 API"""

from typing import List

from fastapi import APIRouter

from app.schemas.persona import Persona
from app.services.ai.prompts import PERSONAS

router = APIRouter(prefix="/personas", tags=["Personas"])


@router.get("", response_model=List[Persona])
def get_personas():
    """取得所有解讀角色的展示資訊（response_model 過濾掉 voice 等 prompt 內容）。"""
    return list(PERSONAS.values())

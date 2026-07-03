"""解讀角色 Schema — 只含展示 metadata,不含 prompt 內容"""

from pydantic import BaseModel


class Persona(BaseModel):
    """解讀角色展示資訊"""

    id: str
    name: str
    name_en: str
    emoji: str
    tagline: str
    description: str
    is_premium: bool

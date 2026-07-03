"""牌陣 Schema"""

from typing import List

from pydantic import BaseModel


class SpreadPosition(BaseModel):
    """牌陣中的一個位置"""

    key: str
    name: str
    description: str


class SpreadInfo(BaseModel):
    """牌陣展示資訊"""

    id: str
    name: str
    description: str
    card_count: int
    requires_options: bool = False
    positions: List[SpreadPosition]

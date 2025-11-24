from sqlalchemy import Column, String, Text, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
import enum
from app.db.database import Base


class CardType(str, enum.Enum):
    """卡片類型"""
    MAJOR = "major"  # 大阿爾克那
    MINOR = "minor"  # 小阿爾克那


class Suit(str, enum.Enum):
    """花色（小阿爾克那）"""
    WANDS = "wands"  # 權杖
    CUPS = "cups"  # 聖杯
    SWORDS = "swords"  # 寶劍
    PENTACLES = "pentacles"  # 錢幣


class Card(Base):
    """塔羅牌 Model"""

    __tablename__ = "cards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)  # 中文名稱
    name_en = Column(String(100), nullable=False, unique=True)  # 英文名稱
    type = Column(String(20), nullable=False)  # major / minor
    suit = Column(String(20), nullable=True)  # wands, cups, swords, pentacles (minor only)
    rank = Column(String(20), nullable=True)  # ace, 2-10, page, knight, queen, king
    number = Column(Integer, nullable=True)  # 0-21 for major, 1-14 for minor

    # 正位牌義
    upright_meaning = Column(Text, nullable=False)
    upright_keywords = Column(Text, nullable=False)  # JSON array stored as text

    # 逆位牌義
    reversed_meaning = Column(Text, nullable=False)
    reversed_keywords = Column(Text, nullable=False)  # JSON array stored as text

    # 象徵與描述
    symbolism = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # 圖片 URL (Phase 2)
    image_url = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Card {self.name} ({self.name_en})>"

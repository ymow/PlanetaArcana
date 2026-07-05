from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.db.database import Base


class GeneratedCardVariant(Base):
    """AIGC card visual variant metadata.

    This stores prompt and curation metadata. Image generation can be attached
    later via image_url/model/seed without changing the prompt contract.
    """

    __tablename__ = "generated_card_variants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    card_id = Column(String(36), ForeignKey("cards.id"), nullable=False, index=True)
    card_slug = Column(String(100), nullable=False, index=True)
    facet_id = Column(String(120), nullable=False, index=True)
    style_scaffold_id = Column(String(100), nullable=False, index=True)

    prompt_json = Column(JSON, nullable=False)
    final_prompt = Column(Text, nullable=False)

    image_url = Column(String(500), nullable=True)
    model = Column(String(100), nullable=True)
    seed = Column(Integer, nullable=True)
    curation_scores = Column(JSON, nullable=True)
    status = Column(String(30), nullable=False, default="draft", index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<GeneratedCardVariant {self.card_slug} {self.style_scaffold_id} {self.status}>"

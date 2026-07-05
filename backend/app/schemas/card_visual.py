"""AIGC card visual prompt schemas."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class CardVisualPromptRequest(BaseModel):
    """Request for composing a card image-generation prompt."""

    card_slug: str = Field(..., min_length=1)
    style_scaffold_id: str = Field("canonical_echo", min_length=1)
    facet_id: Optional[str] = None
    orientation: Optional[Literal["upright", "reversed"]] = None
    context: Optional[Literal["general", "love", "career", "self", "decision", "spiritual"]] = None
    question_context: Optional[str] = Field(None, max_length=500)


class GeneratedVisualPrompt(BaseModel):
    """Structured prompt ingredients."""

    subject_terms: List[str]
    meaning_terms: List[str]
    required_symbols: List[str]
    transformed_symbols: List[str]
    composition_terms: List[str]
    style_modifiers: List[str]
    quality_modifiers: List[str]
    negative_constraints: List[str]
    title_text: Optional[str] = None


class CardVisualPromptResponse(BaseModel):
    """Composed visual prompt response."""

    card_slug: str
    card_name: str
    card_name_en: str
    facet: Dict
    style_scaffold: Dict
    prompt: GeneratedVisualPrompt
    final_prompt: str


VariantStatus = Literal["draft", "generated", "approved", "rejected", "needs_revision"]
CurationStatus = Literal["approved", "rejected", "needs_revision"]


class CardVisualCurationScores(BaseModel):
    """Required curation dimensions for a generated card visual variant."""

    tarot_recognizability: int = Field(..., ge=1, le=5)
    semantic_accuracy: int = Field(..., ge=1, le=5)
    transform_discipline: int = Field(..., ge=1, le=5)
    deck_coherence: int = Field(..., ge=1, le=5)
    originality_safety: int = Field(..., ge=1, le=5)


class CardVisualCurationRequest(BaseModel):
    """Submit a curation scorecard for a generated card visual variant."""

    scores: CardVisualCurationScores
    reviewer_notes: Optional[str] = Field(None, max_length=1000)


class CardVisualVariantCreate(CardVisualPromptRequest):
    """Create and store generated card variant metadata."""

    image_url: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[int] = None
    curation_scores: Optional[Dict[str, Any]] = None
    status: VariantStatus = "draft"


class CardVisualVariantUpdate(BaseModel):
    """Update generated variant metadata after generation or curation."""

    image_url: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[int] = None
    curation_scores: Optional[Dict[str, Any]] = None
    status: Optional[VariantStatus] = None


class CardVisualVariant(BaseModel):
    """Stored generated card variant metadata."""

    id: str
    card_id: str
    card_slug: str
    facet_id: str
    style_scaffold_id: str
    prompt_json: Dict
    final_prompt: str
    image_url: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[int] = None
    curation_scores: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

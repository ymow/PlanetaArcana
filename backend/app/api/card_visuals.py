"""AIGC card visual prompt API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.card import Card
from app.models.generated_card_variant import GeneratedCardVariant
from app.schemas.card_visual import (
    CardVisualCurationRequest,
    CardVisualPromptRequest,
    CardVisualPromptResponse,
    CardVisualVariant,
    CardVisualVariantCreate,
    CardVisualVariantUpdate,
)
from app.services.card_visual_curation import build_curation_result
from app.services.card_visual_data import load_card_visual_data, load_card_visual_knowledge
from app.services.card_visual_prompt import compose_card_visual_prompt

router = APIRouter(prefix="/card-visuals", tags=["Card Visuals"])


@router.get("/catalog")
def get_card_visual_catalog():
    """Return available visual atom data for internal prompt tooling."""
    return load_card_visual_data()


@router.get("/knowledge")
def get_card_visual_knowledge():
    """Return the bottom tarot meaning and market-reference knowledge layer."""
    return load_card_visual_knowledge()


@router.post("/prompts", response_model=CardVisualPromptResponse)
def create_card_visual_prompt(
    request: CardVisualPromptRequest, db: Session = Depends(get_db)
):
    """Compose a structured AIGC prompt from card visual atoms."""
    card = db.query(Card).filter(Card.slug == request.card_slug).first()
    if not card:
        raise HTTPException(status_code=404, detail="找不到該卡牌 slug")

    try:
        return compose_card_visual_prompt(
            card,
            style_scaffold_id=request.style_scaffold_id,
            facet_id=request.facet_id,
            orientation=request.orientation,
            context=request.context,
            question_context=request.question_context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/variants", response_model=CardVisualVariant, status_code=201)
def create_card_visual_variant(
    request: CardVisualVariantCreate, db: Session = Depends(get_db)
):
    """Compose and store a generated card variant metadata record."""
    card = db.query(Card).filter(Card.slug == request.card_slug).first()
    if not card:
        raise HTTPException(status_code=404, detail="找不到該卡牌 slug")

    try:
        composed = compose_card_visual_prompt(
            card,
            style_scaffold_id=request.style_scaffold_id,
            facet_id=request.facet_id,
            orientation=request.orientation,
            context=request.context,
            question_context=request.question_context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    variant = GeneratedCardVariant(
        card_id=card.id,
        card_slug=card.slug,
        facet_id=composed["facet"]["id"],
        style_scaffold_id=composed["style_scaffold"]["id"],
        prompt_json=composed["prompt"],
        final_prompt=composed["final_prompt"],
        image_url=request.image_url,
        model=request.model,
        seed=request.seed,
        curation_scores=request.curation_scores,
        status=request.status,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


@router.get("/variants", response_model=List[CardVisualVariant])
def get_card_visual_variants(
    card_slug: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List generated card variant metadata records."""
    query = db.query(GeneratedCardVariant)
    if card_slug:
        query = query.filter(GeneratedCardVariant.card_slug == card_slug)
    if status:
        query = query.filter(GeneratedCardVariant.status == status)
    return query.order_by(GeneratedCardVariant.created_at.desc()).all()


@router.patch("/variants/{variant_id}", response_model=CardVisualVariant)
def update_card_visual_variant(
    variant_id: str,
    request: CardVisualVariantUpdate,
    db: Session = Depends(get_db),
):
    """Update generation/curation metadata for a stored variant."""
    variant = (
        db.query(GeneratedCardVariant)
        .filter(GeneratedCardVariant.id == variant_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="找不到該卡牌變體")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variant, field, value)

    db.commit()
    db.refresh(variant)
    return variant


@router.post("/variants/{variant_id}/curation", response_model=CardVisualVariant)
def curate_card_visual_variant(
    variant_id: str,
    request: CardVisualCurationRequest,
    db: Session = Depends(get_db),
):
    """Submit a fixed scorecard and update the variant curation status."""
    variant = (
        db.query(GeneratedCardVariant)
        .filter(GeneratedCardVariant.id == variant_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="找不到該卡牌變體")

    curation_scores, recommended_status = build_curation_result(
        request.scores.model_dump(),
        request.reviewer_notes,
        style_scaffold_id=variant.style_scaffold_id,
        prompt_json=variant.prompt_json,
    )
    variant.curation_scores = curation_scores
    variant.status = recommended_status

    db.commit()
    db.refresh(variant)
    return variant

"""Curation scoring rules for generated card visual variants."""

from __future__ import annotations

from typing import Any


REQUIRED_SCORE_KEYS = [
    "tarot_recognizability",
    "semantic_accuracy",
    "transform_discipline",
    "deck_coherence",
    "originality_safety",
]

ABSTRACT_STYLE_SCAFFOLDS = {"archetype_abstract"}


def build_curation_result(
    scores: dict[str, int],
    reviewer_notes: str | None = None,
    style_scaffold_id: str | None = None,
    prompt_json: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    """Return stored score metadata and recommended variant status."""
    values = [scores[key] for key in REQUIRED_SCORE_KEYS]
    average = round(sum(values) / len(values), 2)
    is_abstract_route = style_scaffold_id in ABSTRACT_STYLE_SCAFFOLDS
    has_abstract_usability_support = bool(
        prompt_json
        and prompt_json.get("title_text")
        and prompt_json.get("required_symbols")
        and any(
            "border:" in item.lower()
            for item in prompt_json.get("style_modifiers", [])
            if isinstance(item, str)
        )
    )
    recognizability_threshold = (
        2 if is_abstract_route and has_abstract_usability_support else 3
    )
    has_core_dimension_failure = (
        scores["tarot_recognizability"] < recognizability_threshold
        or any(
            scores[key] <= 2
            for key in REQUIRED_SCORE_KEYS
            if key != "tarot_recognizability"
        )
    )
    gate_notes: list[str] = []
    approval_failures: list[str] = []

    if scores["originality_safety"] <= 2:
        status = "rejected"
        gate_notes.append("originality/safety score is below publishable threshold")
    elif has_core_dimension_failure or average < 3:
        status = "rejected"
        gate_notes.append("one or more core dimensions failed the minimum quality gate")
    elif (
        average >= 4
        and scores["tarot_recognizability"] >= recognizability_threshold
        and scores["semantic_accuracy"] >= 4
        and scores["deck_coherence"] >= 4
        and scores["originality_safety"] >= 5
    ):
        status = "approved"
        gate_notes.append("variant passes semantic and deck-readiness gates")
    else:
        status = "needs_revision"
        if scores["tarot_recognizability"] < recognizability_threshold:
            approval_failures.append("tarot recognizability")
        if scores["semantic_accuracy"] < 4:
            approval_failures.append("semantic accuracy")
        if scores["deck_coherence"] < 4:
            approval_failures.append("deck coherence")
        if scores["originality_safety"] < 5:
            approval_failures.append("originality/safety")
        if average < 4:
            approval_failures.append("average score")
        if approval_failures:
            gate_notes.append(
                "approval gate not met: " + ", ".join(approval_failures)
            )
        gate_notes.append("variant is promising but needs revision before approval")

    result: dict[str, Any] = {
        **scores,
        "average_score": average,
        "recommended_status": status,
        "gate_notes": gate_notes,
    }
    if reviewer_notes:
        result["reviewer_notes"] = reviewer_notes

    return result, status

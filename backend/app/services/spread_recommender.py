"""Deterministic spread recommendation.

The API contract is intentionally stable and cheap: it does not call an AI model
or consume interpretation quota. A model-backed classifier can replace this
internally later without changing the frontend flow.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from app.services.ai.prompts import SPREADS


_TWO_CHOICE_PATTERNS = [
    r"二選一",
    r"兩個選項",
    r"選項\s*[AaＡａ]",
    r"選項\s*[BbＢｂ]",
    r"還是",
    r"或是",
    r"或者",
    r"哪一個",
    r"哪個",
    r"哪邊",
    r"哪種",
    r"\bvs\.?\b",
    r"\bversus\b",
    r"\bor\b",
    r"\bbetween\b.+\band\b",
]

_SINGLE_GUIDANCE_PATTERNS = [
    r"今日",
    r"今天",
    r"現在",
    r"此刻",
    r"當下",
    r"一張",
    r"單張",
    r"一句",
    r"提醒",
    r"指引",
    r"建議",
    r"我需要知道",
    r"會不會",
    r"能不能",
    r"要不要",
    r"是不是",
    r"有沒有",
    r"可不可以",
    r"嗎[？?]?$",
]


def _normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _has_complete_options(options: Optional[Dict[str, str]]) -> bool:
    if not options:
        return False
    return bool((options.get("a") or "").strip() and (options.get("b") or "").strip())


def _matches_any(patterns: list[str], question: str) -> bool:
    return any(re.search(pattern, question, re.IGNORECASE) for pattern in patterns)


def _response(spread_id: str, reason: str, confidence: str, matched_rule: str) -> dict:
    spread = SPREADS[spread_id]
    return {
        "spread_id": spread["id"],
        "spread_name": spread["name"],
        "description": spread["description"],
        "card_count": len(spread["positions"]),
        "requires_options": spread["requires_options"],
        "positions": spread["positions"],
        "reason": reason,
        "confidence": confidence,
        "matched_rule": matched_rule,
    }


def recommend_spread(question_text: str, options: Optional[Dict[str, str]] = None) -> dict:
    """Recommend one of the currently production-ready spreads."""
    question = _normalize_question(question_text)

    if _has_complete_options(options):
        return _response(
            "two_choice",
            "你提供了兩個明確選項,適合用兩難抉擇牌陣比較各自的機會與代價。",
            "high",
            "complete_options",
        )

    if _matches_any(_TWO_CHOICE_PATTERNS, question):
        return _response(
            "two_choice",
            "你的問題呈現兩個方向或選項,適合用兩難抉擇牌陣做比較。",
            "medium",
            "two_choice_keywords",
        )

    if len(question) <= 18 or _matches_any(_SINGLE_GUIDANCE_PATTERNS, question):
        return _response(
            "single",
            "這個問題偏向即時指引或單一核心訊息,用單張牌能更快看見重點。",
            "medium",
            "single_guidance_keywords",
        )

    return _response(
        "past_present_future",
        "這個問題需要看背景、現況與可能發展,過去-現在-未來牌陣能提供清楚脈絡。",
        "fallback",
        "default_timeline",
    )

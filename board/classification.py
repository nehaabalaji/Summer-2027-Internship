"""Deterministic weighted keyword classifier. No external AI API required."""

from __future__ import annotations

import re
from dataclasses import dataclass

from board.config import classification_rules, settings
from board.constants import CATEGORIES
from board.config import classification_rules, settings
from board.constants import CATEGORIES
from board.normalization import phrase_in

_WORDISH = re.compile(r"[^a-z0-9&+]+")


@dataclass
class Classification:
    category: str
    confidence: float
    subcategory: str | None = None
    needs_review: bool = False


def _normalize_text(value: str) -> str:
    return _WORDISH.sub(" ", (value or "").lower()).strip()


def _score_text(text: str, weight: float, rules: dict) -> tuple[dict[str, float], dict[str, str]]:
    haystack = f" {_normalize_text(text)} "
    scores = {category: 0.0 for category in CATEGORIES if category != "Other"}
    matched: dict[str, str] = {}
    for category, spec in (rules.get("categories") or {}).items():
        if category not in scores:
            continue
        for keyword in spec.get("keywords") or []:
            needle = f" {_normalize_text(keyword)} "
            if needle == "  ":
                continue
            if needle in haystack:
                scores[category] += weight
                matched.setdefault(category, keyword)
    return scores, matched


def excluded_engineering_title(title: str) -> bool:
    """True when the title is a software/hardware role without a domain keyword."""
    rules = classification_rules()
    title_n = f" {_normalize_text(title)} "
    title_scores, _ = _score_text(title, 1.0, rules)
    if max(title_scores.values(), default=0) > 0:
        return False
    for keyword in rules.get("exclude_title_keywords") or []:
        needle = f" {_normalize_text(keyword)} "
        if needle != "  " and needle in title_n:
            return True
    return False


def classify_text(title: str, description: str = "") -> Classification:
    rules = classification_rules()
    title_weight = float(rules.get("title_weight", 3.0))
    description_weight = float(rules.get("description_weight", 1.0))
    threshold = float(rules.get("other_threshold", 0.35))
    title_scores, title_matched = _score_text(title, title_weight, rules)
    desc_scores, desc_matched = _score_text(description[:1500], description_weight, rules)

    # Description may reinforce a title match but must not assign a category alone.
    scores = {
        category: title_scores[category]
        + (desc_scores[category] if title_scores[category] > 0 else 0.0)
        for category in title_scores
    }
    matched = {**desc_matched, **title_matched}

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_category, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    confidence = min(1.0, best_score / title_weight) if title_weight else 0.0
    if best_score == 0 or confidence < threshold:
        return Classification(category="Other", confidence=round(confidence, 3), needs_review=True)
    if best_score == second_score:
        return Classification(
            category="Other",
            confidence=round(confidence, 3),
            needs_review=True,
        )
    return Classification(
        category=best_category,
        confidence=round(confidence, 3),
        subcategory=matched.get(best_category),
        needs_review=confidence < 0.5,
    )


def looks_like_early_career(title: str, source_job_type: str | None = None, extra: str = "") -> bool:
    rules = classification_rules()
    combined = " ".join([title or "", extra or ""])
    for keyword in rules.get("early_career_title_keywords") or []:
        if phrase_in(combined, keyword):
            return True
    if source_job_type in {"Internship", "Co-op", "Summer Internship", "Fall Internship", "Spring Internship", "Part-time Internship", "Full-time Internship", "New Graduate", "Entry Level"}:
        # Trust ATS-provided types, not types we previously inferred from "internal".
        if source_job_type != "Internship" or phrase_in(title, "intern") or phrase_in(title, "internship"):
            return True
    return False


def is_relevant(title: str, description: str, category: str) -> bool:
    if excluded_engineering_title(title):
        return False
    if category != "Other":
        return True
    if not settings()["pipeline"].get("drop_unrelated", True):
        return True
    blob = f" {_normalize_text(title)} "
    for keyword in classification_rules().get("relevance_keywords") or []:
        needle = f" {_normalize_text(keyword)} "
        if needle != "  " and needle in blob:
            return True
    return False

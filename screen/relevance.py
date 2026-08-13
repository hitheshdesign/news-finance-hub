"""
screen/relevance.py — score each raw item for "does this touch Indian markets?"
Uses the weighted keyword rules in knowledge/filters.yaml. Simple, transparent,
and free — you can tune the weights without touching code.
"""

from __future__ import annotations
import re

import config

_WORD_RE = re.compile(r"[a-z0-9]+")


def _text_of(item: dict) -> str:
    return f"{item.get('title','')} {item.get('summary','')}".lower()


def score(item: dict) -> float:
    f = config.FILTERS
    text = _text_of(item)
    kw = f.get("relevance_keywords", {})
    s = 0.0

    for word in kw.get("strong", []):
        if word in text:
            s += 2.0
    for word in kw.get("medium", []):
        if word in text:
            s += 1.0
    if any(word in text for word in kw.get("india_bonus", [])):
        s += 1.0
    for word in f.get("noise_keywords", []):
        if word in text:
            s -= 1.5

    # Small bonus for explicitly India-tagged feeds.
    if item.get("region") == "india":
        s += 0.5

    return s


def filter_items(items: list[dict]) -> list[dict]:
    """Attach a relevance score and keep only items above the threshold."""
    threshold = float(config.FILTERS.get("min_relevance_score", 2.0))
    kept = []
    for it in items:
        it["relevance"] = score(it)
        if it["relevance"] >= threshold:
            kept.append(it)
    kept.sort(key=lambda x: x["relevance"], reverse=True)
    print(f"  [screen] {len(kept)}/{len(items)} items passed relevance >= {threshold}")
    return kept

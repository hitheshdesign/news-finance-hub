"""
screen/relevance.py — score each raw item for "does this touch Indian markets,
and is it worth a reader's attention?"

Two questions, deliberately kept apart:

  1. TOPICAL — does this story touch a channel that reaches India at all?
     Driven by the weighted keyword lists in knowledge/filters.yaml.
  2. QUALITY — is it a decision, a shift, something structural? Or is it the
     daily price-tick churn, a stock tip, or somebody's unnamed source?

A story has to clear the topical bar on its own merits before a reputable
source's standing is allowed to help it. That stops a tier-1 feed carrying
something with no market relevance into the brief purely on reputation — and
stops a wire's churn getting in on volume.

All of it is transparent and free: keyword lists and regexes you can tune in
filters.yaml without touching code.
"""

from __future__ import annotations
import re

import config

_WORD_RE = re.compile(r"[a-z0-9]+")

# Compiled once. A bad pattern in the YAML is reported and skipped rather than
# taking the whole run down.
_NOISE_RE: list[re.Pattern] = []
for _p in config.FILTERS.get("noise_patterns", []) or []:
    try:
        _NOISE_RE.append(re.compile(_p, re.I))
    except re.error as e:
        print(f"  [screen] ignoring bad noise pattern {_p!r}: {e}")


def _text_of(item: dict) -> str:
    return f"{item.get('title','')} {item.get('summary','')}".lower()


def is_noise(text: str) -> bool:
    """True for the daily churn: index moves in points, tip sheets, IPO grey
    market chatter. These are dropped outright rather than scored down — no
    amount of topical relevance makes 'Sensex ends 200 pts higher' worth
    reading tomorrow."""
    return any(p.search(text) for p in _NOISE_RE)


def topical_score(text: str, item: dict) -> float:
    """How much genuine India-transmission content is in here."""
    f = config.FILTERS
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
    if item.get("region") == "india":
        s += 0.5
    return s


def quality_score(text: str, item: dict) -> float:
    """Reward decisions and structural shifts; punish hedged speculation and
    obvious junk; credit the source's standing."""
    f = config.FILTERS
    s = 0.0

    # Is this about something being DECIDED or CHANGED? Capped so a story
    # cannot win on keyword stuffing alone.
    hits = sum(1 for w in f.get("signal_keywords", []) if w in text)
    s += min(hits * 1.0, 3.0)

    # Unnamed sources and "may consider" are how rumour reaches print.
    for w in f.get("speculation_markers", []):
        if w in text:
            s -= 2.0

    for word in f.get("noise_keywords", []):
        if word in text:
            s -= 1.5

    # Where it came from. A central bank's own statement is not the same kind
    # of claim as a wire's write-up of it.
    tiers = f.get("source_tier_bonus", {}) or {}
    tier = item.get("tier")
    if tier is not None:
        s += float(tiers.get(tier, tiers.get(str(tier), 0.0)) or 0.0)

    return s


def score(item: dict) -> float:
    text = _text_of(item)
    item["_topical"] = topical_score(text, item)
    item["_quality"] = quality_score(text, item)
    return item["_topical"] + item["_quality"]


def filter_items(items: list[dict]) -> list[dict]:
    """Attach scores and keep what clears both bars."""
    f = config.FILTERS
    threshold = float(f.get("min_relevance_score", 3.0))
    min_topical = float(f.get("min_topical_score", 1.0))

    kept, n_noise, n_thin = [], 0, 0
    for it in items:
        text = _text_of(it)
        if is_noise(text):
            n_noise += 1
            continue
        it["relevance"] = score(it)
        if it["_topical"] < min_topical:
            n_thin += 1
            continue
        if it["relevance"] >= threshold:
            kept.append(it)

    kept.sort(key=lambda x: x["relevance"], reverse=True)
    print(f"  [screen] {len(kept)}/{len(items)} passed "
          f"(dropped {n_noise} as price-tick/tip noise, "
          f"{n_thin} with no real India angle)")
    return kept

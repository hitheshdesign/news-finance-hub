"""
analyze/engine.py — produce the India-impact analysis card for each event.

Two backends, chosen automatically:
  * "gemini"     — if GEMINI_API_KEY is set: richer, tailored explanations.
  * "rule_based" — otherwise: builds the card from the matched knowledge-base
                   linkage. Free, always available, still genuinely useful.

Both are grounded in knowledge/transmission_map.yaml so explanations stay
tied to real economic mechanics.

Everything here is EDUCATIONAL (mechanisms + tendencies), never buy/sell advice.
"""

from __future__ import annotations
import json
import requests

import config
from analyze.knowledge_match import match_linkages


# --------------------------------------------------------------------------
# RULE-BASED backend (no key needed)
# --------------------------------------------------------------------------
def _rule_based(event: dict) -> dict:
    links = match_linkages(event, top_n=1)
    if not links:
        return {
            "what_happened": event.get("headline", ""),
            "why_it_matters_india": [
                "This story was flagged as market-relevant, but it doesn't match a "
                "known transmission pattern yet.",
                "Consider adding a linkage for it to knowledge/transmission_map.yaml "
                "so future coverage is explained automatically.",
            ],
            "impacts": [],
            "watch_next": ["Watch for follow-up coverage that clarifies the market angle."],
            "confidence": "Low",
            "caveats": "No matching knowledge-base pattern; shown for awareness only.",
            "category": "uncategorized",
            "matched_linkage": None,
            "engine": "rule_based",
        }

    link = links[0]
    return {
        "what_happened": event.get("headline", ""),
        "why_it_matters_india": list(link.get("chain", [])),
        "impacts": [dict(i) for i in link.get("impacts", [])],
        "watch_next": list(link.get("watch_next", [])),
        "confidence": "Medium",
        "caveats": (
            "Generated from a knowledge-base pattern by keyword match. It describes the "
            "typical mechanism, not a guaranteed outcome — markets can react differently."
        ),
        "category": link.get("category", "general"),
        "matched_linkage": link.get("id"),
        "engine": "rule_based",
    }


# --------------------------------------------------------------------------
# GEMINI backend (free tier)
# --------------------------------------------------------------------------
_SYSTEM = """You are a markets educator who explains, for a BEGINNER Indian investor,
how a global news event could ripple through to India (inflation, the rupee,
sectors, specific stocks, gold). You explain MECHANISMS and TENDENCIES with rough
probabilities — you NEVER give buy/sell advice or price targets.

Return ONLY valid JSON (no markdown fences) with exactly this shape:
{
  "what_happened": "2-3 plain sentences a beginner understands",
  "why_it_matters_india": ["step 1 of the chain", "step 2", "step 3", "step 4"],
  "impacts": [
    {"target": "e.g. INR (rupee)", "direction": "up|down",
     "probability": "High|Medium|Low", "horizon": "hours|days|weeks|months",
     "rationale": "one short clause"}
  ],
  "watch_next": ["a leading indicator or upcoming event to track", "..."],
  "confidence": "High|Medium|Low",
  "caveats": "one sentence on where this chain could break"
}
Keep it concise, concrete, and India-specific. 3-6 impacts is ideal."""


def _gemini(event: dict) -> dict | None:
    links = match_linkages(event, top_n=2)
    grounding = ""
    if links:
        grounding = "Relevant known transmission patterns (use as grounding):\n"
        for link in links:
            grounding += f"- {link.get('name')}: " + " -> ".join(link.get("chain", [])) + "\n"

    headlines = "\n".join(f"- {it.get('title','')}" for it in event.get("items", [])[:5])
    user = (
        f"NEWS EVENT (from {', '.join(event.get('sources', []))}):\n"
        f"Main headline: {event.get('headline','')}\n"
        f"Related headlines:\n{headlines}\n\n"
        f"{grounding}\n"
        "Produce the India-impact JSON card."
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1200,
            "responseMimeType": "application/json",
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except Exception as e:
        print(f"    [gemini] failed ({e}); falling back to rule-based")
        return None

    # Attach metadata and normalize.
    parsed["engine"] = "gemini"
    parsed["category"] = links[0].get("category", "general") if links else "general"
    parsed["matched_linkage"] = links[0].get("id") if links else None
    parsed.setdefault("impacts", [])
    parsed.setdefault("watch_next", [])
    parsed.setdefault("why_it_matters_india", [])
    parsed.setdefault("confidence", "Medium")
    parsed.setdefault("caveats", "")
    return parsed


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------
def analyze_event(event: dict) -> dict:
    analysis = None
    if config.has_gemini():
        analysis = _gemini(event)
    if analysis is None:
        analysis = _rule_based(event)
    event["analysis"] = analysis
    event["category"] = analysis.get("category", "general")

    # Importance = relevance + how many outlets covered it + whether we could
    # actually explain an India impact.
    impact_bonus = min(len(analysis.get("impacts", [])), 4) * 0.4
    event["importance"] = round(
        event.get("relevance", 0) + event.get("coverage_boost", 0) + impact_bonus, 2
    )
    return event


def analyze_all(events: list[dict]) -> list[dict]:
    backend = "Gemini AI" if config.has_gemini() else "rule-based (free, no key)"
    print(f"  [analyze] backend: {backend}")
    out = []
    for i, ev in enumerate(events, 1):
        print(f"  [analyze] {i}/{len(events)}: {ev.get('headline','')[:70]}")
        out.append(analyze_event(ev))
    out.sort(key=lambda e: e.get("importance", 0), reverse=True)

    # Mark the top highlights.
    top_n = int(config.FILTERS.get("top_highlights", 3))
    for idx, ev in enumerate(out):
        ev["is_top"] = idx < top_n
    return out

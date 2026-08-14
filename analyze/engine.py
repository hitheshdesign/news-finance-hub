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
import time
import requests

import config
from analyze.knowledge_match import match_linkages


# --------------------------------------------------------------------------
# RULE-BASED backend (no key needed)
# --------------------------------------------------------------------------
def _rule_tldr(link: dict, impacts: list[dict]) -> str:
    """Build a one-line plain-English takeaway from the matched linkage."""
    if impacts:
        movers = ", ".join(i["target"] for i in impacts[:2])
        return f"{link.get('name', 'This event')} — likely to move {movers}."
    return link.get("name", "A market-relevant development to be aware of.")


def _rule_based(event: dict) -> dict:
    links = match_linkages(event, top_n=1)
    if not links:
        return {
            "tldr": "Flagged as market-relevant, but no clear India link yet.",
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
    impacts = [dict(i) for i in link.get("impacts", [])]
    return {
        "tldr": _rule_tldr(link, impacts),
        "what_happened": event.get("headline", ""),
        "why_it_matters_india": list(link.get("chain", [])),
        "impacts": impacts,
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
_SYSTEM = """You explain world news to a COMPLETE BEGINNER Indian investor who knows
almost no finance jargon. Your job: show how one global event could ripple through
to India (inflation, the rupee, sectors, specific stocks, gold). You explain HOW and
WHY with rough probabilities. You NEVER give buy/sell advice or price targets.

WRITING RULES (very important):
- Write like you're explaining to a smart friend with zero finance background.
- Use short, everyday sentences. Prefer common words over technical ones.
- The FIRST time you must use a technical term or acronym, immediately explain it in
  plain words in brackets. E.g. "the rupee weakens (each rupee buys fewer dollars)",
  "FIIs (big foreign investors)", "CAD (the gap between what India imports and exports)".
- Never assume the reader knows what a term means. No unexplained acronyms.
- Be concrete and India-specific. Name real sectors/companies where relevant.

Return ONLY valid JSON (no markdown fences) with exactly this shape:
{
  "tldr": "ONE punchy plain-English sentence: the single biggest takeaway a beginner should remember",
  "what_happened": "2-3 very plain sentences explaining the news itself",
  "why_it_matters_india": ["step 1 in plain words", "step 2", "step 3", "step 4"],
  "impacts": [
    {"target": "e.g. The rupee, Gold, Nifty 50, TCS/Infosys (IT firms)",
     "direction": "up|down",
     "probability": "High|Medium|Low", "horizon": "hours|days|weeks|months",
     "rationale": "one short plain-English clause on why"}
  ],
  "watch_next": ["a simple thing to keep an eye on next", "..."],
  "confidence": "High|Medium|Low",
  "caveats": "one plain sentence on where this could go differently"
}
Keep each piece short. 3-6 impacts is ideal. Everything must be understandable by
someone reading about markets for the very first time."""


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
            # Generous budget: newer Gemini models spend some tokens "thinking",
            # so a small budget would truncate the JSON answer.
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }

    # Retry politely on rate limits (429) / transient server errors (5xx),
    # which the free tier can return when calls come in quickly.
    data = None
    for attempt in range(4):
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code in (429, 500, 503):
                wait = 5 * (attempt + 1)
                print(f"    [gemini] {resp.status_code}, waiting {wait}s then retrying...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:
            print(f"    [gemini] request error ({e}); falling back to rule-based")
            return None
    if data is None:
        print("    [gemini] still rate-limited after retries; falling back to rule-based")
        return None

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except Exception as e:
        print(f"    [gemini] could not parse response ({e}); falling back to rule-based")
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
    parsed.setdefault("tldr", "")
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
        # Space out Gemini calls a little to stay under free-tier per-minute limits.
        if config.has_gemini() and i < len(events):
            time.sleep(4)
    out.sort(key=lambda e: e.get("importance", 0), reverse=True)

    # Mark the top highlights.
    top_n = int(config.FILTERS.get("top_highlights", 3))
    for idx, ev in enumerate(out):
        ev["is_top"] = idx < top_n
    return out

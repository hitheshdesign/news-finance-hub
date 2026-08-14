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
            "analogy": "",
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
        "analogy": "",
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
almost no finance jargon. Your job is NOT to summarise the article — a beginner can read
the headline themselves. Your job is to explain what it MEANS: the cause behind it, how it
ripples through to India (inflation, the rupee, sectors, specific stocks, gold), and why a
regular person should care. You explain HOW and WHY with rough probabilities. You NEVER
give buy/sell advice or price targets.

WRITING RULES (very important):
- Write like you're explaining to a smart friend with zero finance background.
- Use short, everyday sentences. Prefer common words over technical ones.
- The FIRST time you must use a technical term or acronym, immediately explain it in
  plain words in brackets. E.g. "the rupee weakens (each rupee buys fewer dollars)",
  "FIIs (big foreign investors)", "bond yield (the interest rate the government pays to borrow)".
- Never assume the reader knows what a term means. No unexplained acronyms.
- EXPLAIN THE CAUSE, not just the fact. If a number changed (reserves hit a record, bonds
  rose, yields fell), say WHAT PUSHED IT there — e.g. "the RBI bought up dollars", "foreign
  investors poured money in", "traders expect the US to cut rates". A beginner's first
  question is "but HOW did that happen?" — always answer it.

THE "tldr" FIELD — this is the most important sentence you write:
- It must say what the news MEANS for the reader, not restate the headline.
- Connect it to a concrete outcome: cheaper/costlier loans, a stronger/weaker rupee, pricier
  petrol, safer markets, etc.
- It must be CONSISTENT with your impacts. If your impacts show a yield falling, don't call
  everything "stable" — explain what that movement means for people.

THE "analogy" FIELD — a short everyday comparison that makes the mechanism click:
- Compare the money-machinery to ordinary life: a household, a shop, a piggy bank, an EMI,
  a queue, a see-saw. E.g. "It's like your bank suddenly trusting you enough to lend you
  money cheaper — because lots of people want to lend to you."
- Keep it to one or two sentences. Skip it (use "") only if no honest analogy fits.

THE "impacts" LIST — STRICT RULE:
- Every "target" MUST be a THING WITH A PRICE OR LEVEL THAT LITERALLY MOVES UP OR DOWN.
  GOOD targets: "The rupee (vs the US dollar)", "Gold price in India", "Nifty 50 (India's
  main stock index)", "10-year bond yield (interest India pays to borrow)", "Petrol & diesel
  prices", "India's inflation rate", "IT stocks like TCS & Infosys".
- NEVER use an institution, person, or action as a target. "RBI", "The Fed", "The government",
  "Investors", "Foreign inflows" are ACTORS, not prices — they cannot "rise" or "fall". If the
  RBI is acting, the impact is on the rupee or on yields; put the RBI's action in the chain or
  in watch_next instead.
- In each "rationale", say plainly whether this move is generally GOOD or BAD for an ordinary
  person, and why (e.g. "lower yields mean cheaper home and car loans — good for borrowers").

Return ONLY valid JSON (no markdown fences) with exactly this shape:
{
  "tldr": "ONE plain sentence on what this MEANS for the reader (not a summary)",
  "what_happened": "2-3 very plain sentences explaining the news AND what caused it",
  "analogy": "one everyday comparison that makes it click, or \\"\\" if none fits",
  "why_it_matters_india": ["cause -> effect step 1", "step 2", "step 3", "step 4"],
  "impacts": [
    {"target": "a price/level that moves — see STRICT RULE above",
     "direction": "up|down",
     "probability": "High|Medium|Low", "horizon": "hours|days|weeks|months",
     "rationale": "why it moves + whether that's good or bad for a regular person"}
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
    parsed.setdefault("analogy", "")
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

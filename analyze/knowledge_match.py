"""
analyze/knowledge_match.py — match an event's text to the transmission knowledge
base. Shared by BOTH backends:
  * rule-based analysis uses the matched linkage directly.
  * the Gemini prompt injects the matched linkage(s) as grounding.
"""

from __future__ import annotations
import config


def _event_text(event: dict) -> str:
    parts = [event.get("headline", "")]
    for it in event.get("items", []):
        parts.append(it.get("title", ""))
        parts.append(it.get("summary", ""))
    return " ".join(parts).lower()


def match_linkages(event: dict, top_n: int = 2) -> list[dict]:
    """Return the best-matching knowledge-base linkages for this event."""
    text = _event_text(event)
    scored = []
    for link in config.TRANSMISSION:
        hits = sum(1 for t in link.get("triggers", []) if t.lower() in text)
        if hits > 0:
            scored.append((hits, link))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [link for _, link in scored[:top_n]]

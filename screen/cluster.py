"""
screen/cluster.py — group items that describe the SAME event into one, so the
brief shows one card per story (not five near-duplicate headlines).

Simple word-overlap ('Jaccard') similarity on headlines. No ML, no cost.
"""

from __future__ import annotations
import re
import hashlib

import config

_WORD_RE = re.compile(r"[a-z0-9]+")

# Common words that shouldn't count toward "same story" similarity.
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "as", "at",
    "by", "with", "from", "is", "are", "be", "will", "after", "over", "amid",
    "says", "say", "new", "up", "down", "us", "india", "market", "markets",
}


def _keywords(title: str) -> set[str]:
    words = _WORD_RE.findall(title.lower())
    return {w for w in words if w not in _STOP and len(w) > 2}


def _similar(a: set[str], b: set[str], threshold: float) -> bool:
    if not a or not b:
        return False
    inter = len(a & b)
    union = len(a | b)
    return (inter / union) >= threshold


def cluster(items: list[dict]) -> list[dict]:
    """Return a list of 'event' dicts, each bundling one or more source items."""
    threshold = float(config.FILTERS.get("cluster_similarity", 0.45))
    events: list[dict] = []

    for it in items:
        kw = _keywords(it.get("title", ""))
        placed = False
        for ev in events:
            if _similar(kw, ev["_keywords"], threshold):
                ev["items"].append(it)
                ev["_keywords"] |= kw
                # Keep the most relevant headline as representative.
                if it.get("relevance", 0) > ev.get("relevance", 0):
                    ev["headline"] = it["title"]
                    ev["relevance"] = it.get("relevance", 0)
                placed = True
                break
        if not placed:
            events.append({
                "headline": it["title"],
                "relevance": it.get("relevance", 0),
                "items": [it],
                "_keywords": kw,
            })

    # Finalize: stable id, dedup source names & urls, drop the internal key set.
    for ev in events:
        ev["sources"] = sorted({i["source"] for i in ev["items"]})
        ev["urls"] = [i["url"] for i in ev["items"] if i.get("url")][:5]
        ev["item_count"] = len(ev["items"])
        # Boost importance a bit when many outlets cover the same story.
        ev["coverage_boost"] = min(len(ev["items"]) - 1, 3) * 0.5
        ev["id"] = hashlib.md5(ev["headline"].encode("utf-8")).hexdigest()[:10]
        del ev["_keywords"]

    events.sort(key=lambda e: e["relevance"] + e["coverage_boost"], reverse=True)
    print(f"  [screen] clustered into {len(events)} distinct events")
    return events

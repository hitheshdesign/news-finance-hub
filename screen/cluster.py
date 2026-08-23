"""
screen/cluster.py — group items that describe the SAME event into one, so the
brief shows one card per story (not five near-duplicate headlines).

Word-overlap ('Jaccard') similarity on headline + a slice of the summary, via
the shared screen/textsim.py helpers. No ML, no cost.
"""

from __future__ import annotations
import hashlib

import config
from screen import textsim

# How many words of the summary to fold into the similarity signal. Enough to
# help genuine duplicates overlap; short enough that a long summary can't
# swamp the headline.
_SUMMARY_WORDS = 30


def _item_keywords(item: dict) -> set[str]:
    """Keywords for clustering: the headline plus the first part of the summary."""
    summary = " ".join((item.get("summary") or "").split()[:_SUMMARY_WORDS])
    return textsim.keywords(item.get("title", ""), summary)


def cluster(items: list[dict]) -> list[dict]:
    """Return a list of 'event' dicts, each bundling one or more source items."""
    threshold = float(config.FILTERS.get("cluster_similarity", 0.4))
    min_shared = int(config.FILTERS.get("cluster_min_shared", 2))
    events: list[dict] = []

    for it in items:
        kw = _item_keywords(it)
        placed = False
        for ev in events:
            if textsim.similar(kw, ev["_keywords"], threshold, min_shared):
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

    # Finalize: stable id, dedup source names & urls, keep the keyword set for
    # cross-day de-duplication (screen/history.py reads it back from the brief).
    for ev in events:
        ev["sources"] = sorted({i["source"] for i in ev["items"]})
        ev["urls"] = [i["url"] for i in ev["items"] if i.get("url")][:5]
        ev["item_count"] = len(ev["items"])
        # Boost importance a bit when many outlets cover the same story.
        ev["coverage_boost"] = min(len(ev["items"]) - 1, 3) * 0.5
        ev["id"] = hashlib.md5(ev["headline"].encode("utf-8")).hexdigest()[:10]
        ev["keywords"] = sorted(ev.pop("_keywords"))

    events.sort(key=lambda e: e["relevance"] + e["coverage_boost"], reverse=True)
    print(f"  [screen] clustered into {len(events)} distinct events")
    return events

"""
screen/textsim.py — tiny shared text-similarity helpers (no ML, no cost).

Used by BOTH same-day clustering (screen/cluster.py) and cross-day
de-duplication (screen/history.py) so they judge "is this the same story?"
in exactly the same way.
"""

from __future__ import annotations
import re

_WORD_RE = re.compile(r"[a-z0-9]+")

# Common words that shouldn't count toward "same story" similarity.
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "as", "at",
    "by", "with", "from", "is", "are", "be", "will", "after", "over", "amid",
    "says", "say", "new", "up", "down", "us", "india", "market", "markets",
    "this", "that", "its", "has", "have", "was", "were", "but", "not", "than",
    "into", "out", "more", "less", "how", "why", "what", "week", "day", "year",
}


def keywords(*texts: str, limit: int | None = None) -> set[str]:
    """Significant lowercase word-tokens drawn from one or more text fields.

    Pass several fields (e.g. title + summary) to widen the signal; `limit`
    caps how many raw tokens are considered so a long summary can't dominate.
    """
    words: list[str] = []
    for t in texts:
        if not t:
            continue
        words.extend(_WORD_RE.findall(t.lower()))
        if limit is not None and len(words) >= limit:
            break
    if limit is not None:
        words = words[:limit]
    return {w for w in words if w not in _STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    """Word-overlap ratio: shared / total. 0.0 when either set is empty."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def overlap(a: set[str], b: set[str]) -> float:
    """Overlap coefficient: shared / size of the SMALLER set.

    Better than Jaccard for spotting near-duplicate news, where two write-ups
    of one event each carry a long tail of unique words that would otherwise
    drag the Jaccard score down. 0.0 when either set is empty.
    """
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def similar(a: set[str], b: set[str], threshold: float, min_shared: int = 2) -> bool:
    """True when two keyword sets look like the same story.

    Requires BOTH a minimum count of shared words AND an overlap-coefficient
    ratio, so two short headlines that merely share one strong word (e.g.
    "gold") don't get falsely merged.
    """
    if not a or not b:
        return False
    if len(a & b) < min_shared:
        return False
    return overlap(a, b) >= threshold

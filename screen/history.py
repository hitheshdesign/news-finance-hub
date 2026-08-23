"""
screen/history.py — cross-day de-duplication.

Each run is otherwise stateless: without this, a story covered yesterday would
reappear today as a fresh card. Here we read the last few days of briefs and:
  * DROP an event that is essentially the same as one already covered, and
  * KEEP but tag as "developing" an event that continues an earlier story with
    a genuinely new angle (e.g. a fresh record low) — so real updates survive
    and the reader sees the story arc.

Matching reuses the exact same word-overlap logic as same-day clustering
(screen/textsim.py), reading each past event's stored `keywords`.
"""

from __future__ import annotations
import json

import config
from screen import textsim


def load_recent_events(window_days: int, exclude_date: str | None = None) -> list[dict]:
    """Return events from the most recent `window_days` stored briefs.

    Reuses the DATA_DIR/*.json date-stem pattern also used by render/web.py.
    """
    data_dir = config.DATA_DIR
    if not data_dir.exists() or window_days <= 0:
        return []

    files = sorted(data_dir.glob("*.json"), key=lambda p: p.stem, reverse=True)
    recent: list[dict] = []
    days_used = 0
    for f in files:
        date = f.stem
        if exclude_date and date == exclude_date:
            continue
        try:
            brief = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for ev in brief.get("events", []):
            kws = ev.get("keywords")
            recent.append({
                "date": brief.get("date", date),
                "headline": ev.get("headline", ""),
                "keywords": set(kws) if kws else textsim.keywords(ev.get("headline", "")),
            })
        days_used += 1
        if days_used >= window_days:
            break
    return recent


def _event_keywords(ev: dict) -> set[str]:
    kws = ev.get("keywords")
    return set(kws) if kws else textsim.keywords(ev.get("headline", ""))


def suppress_repeats(
    events: list[dict],
    prior: list[dict],
    *,
    drop_threshold: float,
    developing_threshold: float,
    min_shared: int = 2,
) -> list[dict]:
    """Drop near-identical repeats; tag evolved follow-ups as developing."""
    if not prior:
        return events

    # Normalize prior keyword sets once (they may arrive as lists from JSON).
    prior_kw = [(p, set(p.get("keywords", []))) for p in prior]

    out: list[dict] = []
    for ev in events:
        kw = _event_keywords(ev)
        best_ratio, best = 0.0, None
        for p, pk in prior_kw:
            if len(kw & pk) < min_shared:
                continue
            r = textsim.overlap(kw, pk)
            if r > best_ratio:
                best_ratio, best = r, p

        if best and best_ratio >= drop_threshold:
            print(f"  [history] repeat dropped (~{best_ratio:.2f} vs {best['date']}): "
                  f"{ev.get('headline', '')[:60]}")
            continue
        if best and best_ratio >= developing_threshold:
            ev["developing"] = True
            ev["developing_since"] = best["date"]
        out.append(ev)
    return out

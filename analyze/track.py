"""
analyze/track.py — start building a track record of the brief's predictions.

Every card makes small, testable claims ("gold likely up, High probability,
over weeks"). We append each one to data/predictions.jsonl so that, over time,
we can look back and see how often the patterns actually played out — which is
how the reader builds real intuition.

v1 only COLLECTS. Scoring the outcomes (against price data) comes later, once
there are a few weeks of predictions to check. Rows carry empty `outcome` /
`scored` fields ready for that follow-up.
"""

from __future__ import annotations
import json

import config

_LEDGER_NAME = "predictions.jsonl"


def record_predictions(brief: dict) -> int:
    """Append this brief's impact predictions to the JSONL ledger.

    Returns the number of prediction rows written. Idempotent per date: if the
    ledger already contains rows for this brief's date (e.g. a re-run), those
    are dropped first so a day is never double-counted.
    """
    date = brief.get("date", "")
    rows: list[dict] = []
    for ev in brief.get("events", []):
        analysis = ev.get("analysis", {}) or {}
        for im in analysis.get("impacts", []):
            rows.append({
                "date": date,
                "event_id": ev.get("id", ""),
                "category": ev.get("category", "general"),
                "headline": ev.get("headline", ""),
                "target": im.get("target", ""),
                "direction": im.get("direction", ""),
                "probability": im.get("probability", ""),
                "horizon": im.get("horizon", ""),
                # Filled in later when we score how it actually went:
                "outcome": None,      # "hit" | "miss" | "unclear"
                "scored": False,
            })

    # Keep the ledger in data/ (one level up from the dated briefs) so it sits
    # apart from the per-day brief files.
    ledger_dir = config.DATA_DIR.parent
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / _LEDGER_NAME

    # Drop any existing rows for this date (safe re-runs), then rewrite.
    kept: list[str] = []
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                if json.loads(line).get("date") == date:
                    continue
            except Exception:
                continue
            kept.append(line)

    with open(ledger, "w", encoding="utf-8") as f:
        for line in kept:
            f.write(line + "\n")
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"  [track] logged {len(rows)} prediction(s) to {ledger.name}")
    return len(rows)

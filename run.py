"""
run.py — the daily pipeline. Run it by hand or let GitHub Actions run it each morning.

  python run.py                 # full run: ingest -> analyze -> render -> deliver
  python run.py --dry-run       # do everything EXCEPT sending email/telegram
  python run.py --sample        # use bundled sample news (offline demo, no network)
  python run.py --max 6         # override how many events to include

It always writes:
  data/briefs/<date>.json   (structured record — your history/"memory")
  data/briefs/<date>.md     (human-readable copy)
  site/index.html           (the web page)
"""

from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import config
from ingest import rss, gdelt, fred
from screen import relevance, cluster
from analyze import engine
from render import web, emailer, telegram


def _human_date(d: datetime) -> str:
    # e.g. "Wednesday, 13 August 2026"
    return d.strftime("%A, %d %B %Y")


def _load_sample() -> list[dict]:
    path = config.KNOWLEDGE_DIR / "sample_items.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_all(use_sample: bool) -> list[dict]:
    if use_sample:
        print("[ingest] using bundled sample items (offline demo)")
        return _load_sample()

    print("[ingest] pulling live sources...")
    items = []
    items += rss.fetch()
    items += gdelt.fetch()
    # If the network gave us nothing, fall back to sample so we always render.
    if not items:
        print("[ingest] no live items (network?), falling back to sample")
        return _load_sample()
    return items


def build_brief(events: list[dict], macro: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "date_human": _human_date(now),
        "generated_at": now.isoformat(timespec="seconds"),
        "engine": "Gemini AI" if config.has_gemini() else "rule-based (free)",
        "macro": macro,
        "events": events,
    }


def store_brief(brief: dict) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    # JSON (full structured record)
    json_path = config.DATA_DIR / f"{brief['date']}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2, ensure_ascii=False)
    # Markdown (easy to read/skim)
    md_path = config.DATA_DIR / f"{brief['date']}.md"
    md_path.write_text(_to_markdown(brief), encoding="utf-8")
    print(f"[store] saved {json_path.name} and {md_path.name}")


def _to_markdown(brief: dict) -> str:
    lines = [f"# India Impact Brief — {brief['date_human']}",
             f"_{len(brief['events'])} signals · analysis: {brief['engine']}_\n"]
    for ev in brief["events"]:
        a = ev.get("analysis", {})
        star = "★ " if ev.get("is_top") else ""
        lines.append(f"## {star}{ev['headline']}")
        if a.get("why_it_matters_india"):
            lines.append("**How it reaches India:** " + " → ".join(a["why_it_matters_india"]))
        for im in a.get("impacts", []):
            d = "▲" if im.get("direction") == "up" else "▼"
            lines.append(f"- {im.get('target')} {d} "
                         f"({im.get('probability')}, {im.get('horizon')}) — {im.get('rationale')}")
        if a.get("watch_next"):
            lines.append("**Watch next:** " + "; ".join(a["watch_next"]))
        lines.append(f"_Sources: {', '.join(ev.get('sources', []))}_\n")
    lines.append("\n---\n_Educational only — not investment advice._")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Daily News -> India Impact brief")
    ap.add_argument("--dry-run", action="store_true", help="skip email/telegram delivery")
    ap.add_argument("--sample", action="store_true", help="use bundled offline sample news")
    ap.add_argument("--max", type=int, default=None, help="max events in the brief")
    args = ap.parse_args()

    print("=" * 66)
    print("  NEWS FINANCE HUB — daily India-impact brief")
    print("=" * 66)

    # 1. INGEST
    raw = ingest_all(use_sample=args.sample)

    # 2. SCREEN (relevance + cluster into distinct events)
    print("[screen] applying ground rules...")
    kept = relevance.filter_items(raw)
    events = cluster.cluster(kept)

    # cap to max events (from CLI or filters.yaml)
    max_events = args.max or int(config.FILTERS.get("max_events_per_brief", 8))
    events = events[:max_events]

    # 3. ANALYZE (India-impact cards)
    print("[analyze] generating India-impact cards...")
    events = engine.analyze_all(events)

    # macro context (FRED) — optional
    macro = fred.fetch()

    # 4. ASSEMBLE + STORE
    brief = build_brief(events, macro)
    store_brief(brief)

    # 5. RENDER web page
    print("[render] building web page...")
    index_path = web.write_site(brief)

    # 6. DELIVER
    if args.dry_run:
        print("[deliver] --dry-run: skipping email/telegram")
    else:
        print("[deliver] sending...")
        telegram.send_telegram(brief)
        emailer.send_email(brief)

    print("=" * 66)
    print(f"  DONE — {len(events)} signals.")
    print(f"  Open this in your browser:  {index_path}")
    print("=" * 66)


if __name__ == "__main__":
    main()

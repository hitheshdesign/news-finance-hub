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
import calendar as _calmod
import json
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

import config
from ingest import rss, gdelt, fred
from screen import relevance, cluster, history
from analyze import engine, track, globe
from analyze.knowledge_match import match_linkages
from render import web, emailer, telegram


def _human_date(d: datetime) -> str:
    # e.g. "Wednesday, 13 August 2026"
    return d.strftime("%A, %d %B %Y")


def _load_sample() -> list[dict]:
    path = config.KNOWLEDGE_DIR / "sample_items.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Explainer/aggregator sources whose original articles we surface directly.
_DEEPER_SOURCES = {"finshots", "the ken"}


def _collect_deeper_reads(raw: list[dict], limit: int = 6) -> list[dict]:
    """Pick out today's explainer articles (Finshots / The Ken) so we can link
    their originals, not just our reprocessed cards."""
    seen: set[str] = set()
    out: list[dict] = []
    for it in raw:
        src = (it.get("source") or "").strip()
        if src.lower() not in _DEEPER_SOURCES:
            continue
        title = (it.get("title") or "").strip()
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        out.append({"title": title, "url": it.get("url", ""), "source": src})
        if len(out) >= limit:
            break
    return out


def _select_balanced(events: list[dict], max_events: int, max_per_topic: int) -> list[dict]:
    """Pick up to `max_events` with variety across themes, so one loud topic
    (e.g. the Fed) can't crowd out everything else.

    Topic is pre-tagged cheaply from the knowledge base (no Gemini cost) via
    analyze.knowledge_match. We then round-robin: the strongest story from each
    topic first, then the second, and so on — never more than `max_per_topic`
    from any one theme. Events arrive already sorted by relevance, so each
    topic contributes its highest-signal items first.
    """
    groups: dict[str, list[dict]] = {}
    order: list[str] = []                # topic keys, in importance order
    for i, ev in enumerate(events):
        links = match_linkages(ev, top_n=1)
        if links:
            ev["category"] = links[0].get("category", "general")
            key = links[0].get("id") or f"_uniq_{i}"
        else:
            ev["category"] = "general"
            key = f"_uniq_{i}"          # unmatched stories are each their own topic
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(ev)

    selected: list[dict] = []
    for rnd in range(max_per_topic):
        for key in order:
            if len(selected) >= max_events:
                break
            if len(groups[key]) > rnd:
                selected.append(groups[key][rnd])
        if len(selected) >= max_events:
            break
    return selected[:max_events]


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


def _safe_date(year: int, month: int, day: int) -> date:
    """A valid date, clamping the day to the month's last day (e.g. 31 -> 30)."""
    last = _calmod.monthrange(year, month)[1]
    return date(year, month, min(day, last))


def _upcoming_calendar(lookahead_days: int) -> list[dict]:
    """Resolve knowledge/calendar.yaml into concrete upcoming events.

    Fixed-date entries are used as-is; monthly-recurring entries roll to their
    next occurrence. Only events within `lookahead_days` from today are kept.
    """
    today = datetime.now(timezone.utc).date()
    horizon = today + timedelta(days=max(lookahead_days, 0))
    out: list[dict] = []

    def _add(d: date, ev: dict) -> None:
        out.append({
            "name": ev.get("name", ""),
            "date_human": d.strftime("%a, %d %b"),
            "month_label": d.strftime("%B %Y"),
            "days_away": (d - today).days,
            "category": ev.get("category", "general"),
            "why": ev.get("why", ""),
        })

    for ev in config.CALENDAR:
        if ev.get("date"):
            try:
                d = date.fromisoformat(str(ev["date"]))
            except Exception:
                continue
            if today <= d <= horizon:
                _add(d, ev)
        elif ev.get("recurs") == "monthly" and ev.get("day"):
            # Emit EVERY monthly occurrence inside the horizon, not just the next
            # one, so opening the calendar shows the months ahead.
            day = int(ev["day"])
            y, m = today.year, today.month
            for _ in range(24):                      # safety bound
                d = _safe_date(y, m, day)
                if d > horizon:
                    break
                if d >= today:
                    _add(d, ev)
                y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    out.sort(key=lambda e: e["days_away"])
    return out


def build_brief(events: list[dict], macro: list[dict], calendar: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "date_human": _human_date(now),
        "generated_at": now.isoformat(timespec="seconds"),
        "engine": "Gemini AI" if config.has_gemini() else "rule-based (free)",
        "macro": macro,
        "calendar": calendar,
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


def _store_global(gdata: dict) -> None:
    """Persist the Global Finance snapshot (history / future scoring)."""
    out_dir = config.DATA_DIR.parent / "global"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{gdata.get('updated', 'latest')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gdata, f, indent=2, ensure_ascii=False)
    print(f"  [global] saved {path.name}")


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
    deeper_reads = _collect_deeper_reads(raw)

    # 2. SCREEN (relevance + cluster into distinct events)
    print("[screen] applying ground rules...")
    kept = relevance.filter_items(raw)
    events = cluster.cluster(kept)

    # 2b. Cross-day de-dupe: drop stories already covered in recent days,
    #     tag evolved follow-ups as "developing".
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prior = history.load_recent_events(
        int(config.FILTERS.get("dedup_window_days", 5)), exclude_date=today)
    before = len(events)
    events = history.suppress_repeats(
        events, prior,
        drop_threshold=float(config.FILTERS.get("cross_day_similarity", 0.7)),
        developing_threshold=float(config.FILTERS.get("developing_similarity", 0.45)),
    )
    if len(events) < before:
        print(f"  [screen] cross-day de-dupe removed {before - len(events)} repeat(s)")

    # 2c. Select a category-balanced set so the brief isn't 'all Fed/gold'.
    max_events = args.max or int(config.FILTERS.get("max_events_per_brief", 8))
    events = _select_balanced(
        events, max_events, int(config.FILTERS.get("max_per_topic", 2)))

    # 3. ANALYZE (India-impact cards)
    print("[analyze] generating India-impact cards...")
    events = engine.analyze_all(events)

    # macro context (FRED) — optional
    macro = fred.fetch()

    # forward calendar — what to watch for in the days ahead
    upcoming = _upcoming_calendar(int(config.FILTERS.get("calendar_lookahead_days", 14)))

    # 4. ASSEMBLE + STORE
    brief = build_brief(events, macro, upcoming)
    alert_days = int(config.FILTERS.get("calendar_alert_days", 4))
    brief["calendar_alert_days"] = alert_days
    brief["calendar_alert"] = sum(1 for c in upcoming if c["days_away"] <= alert_days)
    brief["deeper_reads"] = deeper_reads
    store_brief(brief)
    track.record_predictions(brief)

    # 5. RENDER web page + the pattern-library and global-finance pages
    print("[render] building web page...")
    index_path = web.write_site(brief)
    web.write_patterns_page()
    gdata = globe.build_global(events)
    _store_global(gdata)
    web.write_global_page(gdata)

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

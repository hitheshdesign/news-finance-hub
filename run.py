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
from ingest import rss, gdelt, fred, quotes
from screen import relevance, cluster, history
from analyze import engine, track, globe, assets
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


def _collect_deeper_reads(raw: list[dict], events: list[dict], limit: int = 6) -> list[dict]:
    """Explainer articles (Finshots / The Ken) that did NOT become a card.

    These sources flow through the normal pipeline: if a story clears the
    relevance bar and gets selected, it appears as a full India-impact card in
    our own words. Whatever is left over is surfaced here as a plain link, so
    the original write-up is still one tap away and nothing is shown twice.
    """
    used_urls = {u for ev in events for u in (ev.get("urls") or [])}
    used_titles = {(it.get("title") or "").strip().lower()
                   for ev in events for it in (ev.get("items") or [])}

    seen: set[str] = set()
    out: list[dict] = []
    for it in raw:
        src = (it.get("source") or "").strip()
        if src.lower() not in _DEEPER_SOURCES:
            continue
        title = (it.get("title") or "").strip()
        key = title.lower()
        if not title or key in seen or key in used_titles:
            continue
        if it.get("url") and it["url"] in used_urls:
            continue                      # already covered as a card
        seen.add(key)
        out.append({"title": title, "url": it.get("url", ""), "source": src})
        if len(out) >= limit:
            break
    return out


def _select_balanced(events: list[dict], max_events: int, max_per_topic: int) -> list[dict]:
    """Pick up to `max_events` that actually span different subjects.

    There are two independent axes of sameness, and the brief needs guarding on
    both:

      * SUBJECT — the feed's topic (policy, climate, geopolitics, energy...).
        This is the one that matters most. Without it the brief drifts into
        being the same rates-and-crude story every day, because that is what
        the high-volume market wires publish most of.
      * MECHANISM — the knowledge-base linkage a story matches (e.g. "Fed
        raises rates -> FII outflows"). Two different stories can share one
        mechanism and read as a repeat even if their subjects differ.

    Events arrive sorted by relevance, so each bucket contributes its strongest
    story first. We round-robin across subjects, then fill any remaining slots
    by score — relaxing the subject cap last, since a thin news day should
    still produce a full brief.
    """
    per_subject = int(config.FILTERS.get("max_per_source_topic", 2))
    min_subjects = int(config.FILTERS.get("min_topics_per_brief", 4))

    # Tag every event with its mechanism, cheaply and with no Gemini cost.
    for i, ev in enumerate(events):
        links = match_linkages(ev, top_n=1)
        if links:
            ev["category"] = links[0].get("category", "general")
            ev["_mech"] = links[0].get("id") or f"_uniq_{i}"
        else:
            ev["category"] = ev.get("topic", "general")
            ev["_mech"] = f"_uniq_{i}"

    subjects: dict[str, list[dict]] = {}
    order: list[str] = []
    for ev in events:
        key = ev.get("topic") or "general"
        if key not in subjects:
            subjects[key] = []
            order.append(key)
        subjects[key].append(ev)

    selected: list[dict] = []
    used_mech: dict[str, int] = {}

    def take(ev) -> bool:
        m = ev.get("_mech", "")
        if used_mech.get(m, 0) >= max_per_topic:
            return False
        selected.append(ev)
        used_mech[m] = used_mech.get(m, 0) + 1
        return True

    # Pass 1 — one story from each subject, then a second, and so on.
    for rnd in range(per_subject):
        for key in order:
            if len(selected) >= max_events:
                break
            for ev in subjects[key]:
                if ev in selected:
                    continue
                if sum(1 for s in selected if s.get("topic") == key) > rnd:
                    break
                if take(ev):
                    break
        if len(selected) >= max_events:
            break

    # Pass 2 — fill any slots left by score, subject cap relaxed.
    if len(selected) < max_events:
        for ev in events:
            if len(selected) >= max_events:
                break
            if ev not in selected:
                take(ev)

    got = len({ev.get("topic") for ev in selected})
    print(f"  [screen] selected {len(selected)} cards across {got} subject(s)"
          f"{' — thin news day' if got < min_subjects else ''}")
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


def _todays_history() -> dict | None:
    """One episode from knowledge/market_history.yaml, rotating by date.

    Keyed off the date rather than randomly, so the same day always shows the
    same episode (a re-run does not shuffle it) and the library cycles through
    in order instead of repeating by chance. Add episodes and the cycle
    lengthens on its own.
    """
    eps = config.MARKET_HISTORY or []
    if not eps:
        return None
    day = datetime.now(timezone.utc).date()
    return dict(eps[(day.toordinal()) % len(eps)])


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


def _store_snapshot(kind: str, data: dict) -> None:
    """Persist a curated-page snapshot (history / future scoring).
    kind is the folder under data/ — e.g. "global", "assets"."""
    out_dir = config.DATA_DIR.parent / kind
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{data.get('updated', 'latest')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [{kind}] saved {path.name}")


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
    brief["deeper_reads"] = _collect_deeper_reads(raw, events)
    brief["history"] = _todays_history()
    if brief["history"]:
        print(f"  [history] today's pattern: {brief['history'].get('title')}")
    store_brief(brief)
    track.record_predictions(brief)

    # 5. RENDER the brief plus the three reference pages
    print("[render] building web page...")
    index_path = web.write_site(brief)
    web.write_patterns_page()
    gdata = globe.build_global(events)
    _store_snapshot("global", gdata)
    web.write_global_page(gdata)
    qdata = quotes.fetch()
    quotes.store(qdata)
    adata = assets.build_assets(events, qdata)
    _store_snapshot("assets", adata)
    web.write_assets_page(adata)

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

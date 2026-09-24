"""
ingest/rss.py — pull recent headlines from curated RSS feeds (free, reliable).
Returns a list of normalized raw items. Never raises: a broken feed is skipped.
"""

from __future__ import annotations
import time
import html
import re
from datetime import datetime, timezone
import feedparser
import requests

import config

# feedparser's built-in HTTP identifies itself as feedparser, and a fair number
# of publishers answer that with a 403. Nine of our sources — the ECB, Carbon
# Brief, Mongabay, MIT Technology Review, every Business Standard feed — return
# nothing that way and return fine to a normal browser user-agent. So fetch the
# bytes ourselves and hand those to feedparser to parse.
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _parse_feed(url: str):
    """Fetch with a browser user-agent, fall back to feedparser's own fetch."""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=25)
        if r.status_code == 200 and r.content:
            parsed = feedparser.parse(r.content)
            if parsed.entries:
                return parsed
    except Exception:
        pass
    return feedparser.parse(url)

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    """Strip HTML tags and unescape entities (&amp; -> &) for readable text."""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _entry_time(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def fetch(max_per_feed: int = 15) -> list[dict]:
    """Pull every configured feed.

    Each item carries its feed's `tier` (how primary the source is) and `topic`
    (what subject area it covers). Both are used later — tier by the relevance
    screen to weigh legitimacy, topic by the selector to keep the brief from
    becoming five versions of the same story.

    A feed may set its own `max_items`: high-volume wires are capped low so
    they cannot crowd out the slower, more considered sources simply by
    publishing more often.
    """
    items: list[dict] = []
    feeds = config.SOURCES.get("rss_feeds", [])
    per_feed: dict[str, int] = {}
    for feed in feeds:
        name = feed.get("name", "RSS")
        url = feed.get("url", "")
        region = feed.get("region", "")
        tier = feed.get("tier", 3)
        topic = feed.get("topic", "general")
        cap = int(feed.get("max_items", max_per_feed))
        try:
            parsed = _parse_feed(url)
            n = 0
            for entry in parsed.entries[:cap]:
                title = _clean(entry.get("title") or "")
                if not title:
                    continue
                summary = _clean(entry.get("summary") or entry.get("description") or "")[:600]
                items.append({
                    "title": title,
                    "url": (entry.get("link") or "").strip(),
                    "source": name,
                    "published": _entry_time(entry),
                    "summary": summary,
                    "region": region,
                    "tier": tier,
                    "topic": topic,
                    "origin": "rss",
                })
                n += 1
            per_feed[name] = n
            if n == 0:
                print(f"  [rss] WARNING {name} returned nothing — feed may be dead")
        except Exception as e:
            print(f"  [rss] skipped {name}: {e}")
            continue
    live = sum(1 for v in per_feed.values() if v)
    print(f"  [rss] collected {len(items)} items from {live}/{len(feeds)} live feeds")
    return items

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

import config

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
    items: list[dict] = []
    feeds = config.SOURCES.get("rss_feeds", [])
    for feed in feeds:
        name = feed.get("name", "RSS")
        url = feed.get("url", "")
        region = feed.get("region", "")
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:max_per_feed]:
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
                    "origin": "rss",
                })
        except Exception as e:
            print(f"  [rss] skipped {name}: {e}")
            continue
    print(f"  [rss] collected {len(items)} items from {len(feeds)} feeds")
    return items

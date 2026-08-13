"""
ingest/gdelt.py — pull recent global articles from the GDELT DOC 2.0 API.
Free, no API key. GDELT monitors world news in near real-time.
Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
Never raises: on any failure it returns [].
"""

from __future__ import annotations
import html
from datetime import datetime, timezone
import requests

import config

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def fetch() -> list[dict]:
    cfg = config.SOURCES.get("gdelt", {})
    if not cfg.get("enabled", False):
        return []

    terms = cfg.get("query_terms", [])
    if not terms:
        return []

    # Build an OR query of quoted phrases, and keep it to English articles.
    or_block = " OR ".join(f'"{t}"' for t in terms)
    query = f"({or_block}) sourcelang:english"

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": int(cfg.get("max_records", 60)),
        "timespan": cfg.get("timespan", "1d"),
        "sort": "datedesc",
    }
    headers = {"User-Agent": "news-finance-hub/1.0 (personal research)"}

    try:
        resp = requests.get(GDELT_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        # GDELT sometimes returns non-JSON (e.g. an error string); guard it.
        try:
            data = resp.json()
        except ValueError:
            print("  [gdelt] non-JSON response, skipping")
            return []
    except Exception as e:
        print(f"  [gdelt] request failed: {e}")
        return []

    items: list[dict] = []
    for art in data.get("articles", []):
        title = html.unescape((art.get("title") or "").strip())
        if not title:
            continue
        # seendate looks like 20260813T101500Z
        published = art.get("seendate", "")
        try:
            dt = datetime.strptime(published, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            published = dt.isoformat()
        except Exception:
            published = datetime.now(timezone.utc).isoformat()

        items.append({
            "title": title,
            "url": (art.get("url") or "").strip(),
            "source": (art.get("domain") or "GDELT").strip(),
            "published": published,
            "summary": "",
            "region": "global",
            "origin": "gdelt",
        })

    print(f"  [gdelt] collected {len(items)} global articles")
    return items

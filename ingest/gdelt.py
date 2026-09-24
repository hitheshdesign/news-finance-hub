"""
ingest/gdelt.py — pull recent global articles from the GDELT DOC 2.0 API.
Free, no API key. GDELT monitors world news in near real-time.
Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
Never raises: on any failure it returns [].
"""

from __future__ import annotations
import html
import time
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

    # GDELT rate-limits long queries with a 429, and our term list is now much
    # broader than it was. Ask in small themed batches instead of one giant OR,
    # with a pause between them. A batch that fails just contributes nothing.
    batch_size = int(cfg.get("batch_size", 10))
    batches = [terms[i:i + batch_size] for i in range(0, len(terms), batch_size)]
    per_batch = max(10, int(cfg.get("max_records", 60)) // max(len(batches), 1))
    headers = {"User-Agent": "news-finance-hub/1.0 (personal research)"}

    articles, ok = [], 0
    for n, batch in enumerate(batches):
        or_block = " OR ".join(f'"{t}"' for t in batch)
        params = {
            "query": f"({or_block}) sourcelang:english",
            "mode": "artlist",
            "format": "json",
            "maxrecords": per_batch,
            "timespan": cfg.get("timespan", "1d"),
            "sort": "datedesc",
        }
        if n:
            time.sleep(float(cfg.get("batch_pause_seconds", 2.0)))
        try:
            resp = requests.get(GDELT_URL, params=params, headers=headers, timeout=30)
            if resp.status_code == 429:
                time.sleep(5)
                resp = requests.get(GDELT_URL, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            try:
                articles += resp.json().get("articles", []) or []
                ok += 1
            except ValueError:
                continue
        except Exception as e:
            print(f"  [gdelt] batch {n + 1}/{len(batches)} failed: {str(e)[:80]}")
            continue
    if not articles:
        print("  [gdelt] no articles returned")
        return []
    print(f"  [gdelt] {ok}/{len(batches)} batches returned {len(articles)} articles")
    data = {"articles": articles}

    items: list[dict] = []
    seen_urls: set[str] = set()
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

        u = (art.get("url") or "").strip()
        if u and u in seen_urls:
            continue
        seen_urls.add(u)
        items.append({
            "title": title,
            "url": (art.get("url") or "").strip(),
            "source": (art.get("domain") or "GDELT").strip(),
            "published": published,
            "summary": "",
            "region": "global",
            # GDELT is a firehose of whoever published, so it gets no source
            # standing. Its job here is breadth — surfacing the CAUSE behind a
            # move (a policy, a drought, a closed shipping lane) that the
            # curated feeds may not have covered yet.
            "tier": 3,
            "topic": "general",
            "origin": "gdelt",
        })

    print(f"  [gdelt] collected {len(items)} global articles")
    return items

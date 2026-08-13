"""
ingest/fred.py — pull latest values for key US macro series from FRED.
Free, but needs a FRED_API_KEY. If no key is set, this is skipped cleanly.
These are CONTEXT signals shown at the top of the brief (e.g. the Fed rate,
US CPI, jobs) — the very data that moves gold and the rupee.
Never raises: on failure it returns [].
"""

from __future__ import annotations
import requests

import config

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch() -> list[dict]:
    if not config.has_fred():
        return []
    cfg = config.SOURCES.get("fred", {})
    if not cfg.get("enabled", False):
        return []

    results: list[dict] = []
    for series in cfg.get("series", []):
        sid = series.get("id")
        label = series.get("label", sid)
        params = {
            "series_id": sid,
            "api_key": config.FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 2,   # latest + previous, to show direction
        }
        try:
            resp = requests.get(FRED_URL, params=params, timeout=20)
            resp.raise_for_status()
            obs = resp.json().get("observations", [])
        except Exception as e:
            print(f"  [fred] {sid} failed: {e}")
            continue

        if not obs:
            continue
        latest = obs[0]
        prev = obs[1] if len(obs) > 1 else None
        try:
            latest_val = float(latest["value"])
            prev_val = float(prev["value"]) if prev else None
        except (ValueError, KeyError, TypeError):
            continue

        direction = "flat"
        if prev_val is not None:
            if latest_val > prev_val:
                direction = "up"
            elif latest_val < prev_val:
                direction = "down"

        results.append({
            "id": sid,
            "label": label,
            "value": latest_val,
            "date": latest.get("date", ""),
            "prev_value": prev_val,
            "direction": direction,
        })

    print(f"  [fred] collected {len(results)} macro series")
    return results

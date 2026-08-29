"""
analyze/global.py — assemble the Global Finance data object.

Combines three things, all $0:
  * curated country valuations (config.GLOBAL_MARKETS, from CAPE data),
  * a LIVE news overlay — today's brief events tagged to the countries they
    mention, so each country shows its current headwinds/tailwinds, and
  * a curated money-rotation timeline (config.MONEY_ROTATION).

No Gemini, no paid data. Everything is labelled indicative/educational.
"""

from __future__ import annotations
from datetime import datetime, timezone

import config

# Keywords that tie a news event to a country (matched against headline +
# analysis text, lower-cased). Kept specific to avoid false hits.
_COUNTRY_KEYWORDS: dict[str, list[str]] = {
    "US": ["fed", "federal reserve", "u.s.", "united states", "wall street",
           "powell", "treasury", "s&p", "nasdaq", "dow jones", "american"],
    "IN": ["india", "indian", "rupee", "nifty", "sensex", "rbi", "mumbai"],
    "CN": ["china", "chinese", "beijing", "yuan", "pboc", "shanghai"],
    "JP": ["japan", "japanese", "yen", "nikkei", "tokyo", "boj"],
    "HK": ["hong kong", "hang seng"],
    "GB": ["uk ", "u.k.", "britain", "british", "london", "ftse", "sterling",
           "bank of england"],
    "DE": ["german", "germany", "dax", "frankfurt"],
    "FR": ["france", "french", "cac 40", "paris"],
    "KR": ["korea", "korean", "kospi", "seoul", "samsung"],
    "TW": ["taiwan", "taiwanese", "tsmc", "taipei"],
    "BR": ["brazil", "brazilian", "bovespa", "sao paulo"],
    "ID": ["indonesia", "indonesian", "rupiah", "jakarta"],
    "VN": ["vietnam", "vietnamese", "hanoi"],
    "CA": ["canada", "canadian", "toronto"],
    "AU": ["australia", "australian", "asx"],
    "SA": ["saudi", "opec", "gulf", "riyadh", "aramco"],
    "ZA": ["south africa", "rand ", "johannesburg"],
    "MX": ["mexico", "mexican", "peso"],
}

# Words hinting at today's overall risk mood (nudges the rotation "now" note).
_RISK_OFF = ["sell-off", "selloff", "outflow", "risk-off", "safe haven", "war",
             "escalat", "plunge", "crash", "tariff", "sanction", "record low"]
_RISK_ON = ["rally", "record high", "surge", "inflow", "risk-on", "rebound",
            "optimism", "rate cut"]


def _event_text(ev: dict) -> str:
    """Text used to tag an event to a country. Use the RAW news (headline,
    what-happened, source titles) — NOT the India-impact analysis, which always
    mentions India/rupee and would over-match every country to India."""
    a = ev.get("analysis", {}) or {}
    parts = [ev.get("headline", ""), a.get("what_happened", "")]
    for it in ev.get("items", []) or []:
        parts.append(it.get("title", ""))
    return " ".join(parts).lower()


def _overlay_news(events: list[dict]) -> dict[str, list[dict]]:
    """Return {country_code: [ {title, url}, ... ]} from today's events."""
    tagged: dict[str, list[dict]] = {}
    for ev in events:
        text = _event_text(ev)
        url = (ev.get("urls") or [""])[0]
        for code, kws in _COUNTRY_KEYWORDS.items():
            if any(k in text for k in kws):
                tagged.setdefault(code, [])
                if len(tagged[code]) < 4:
                    tagged[code].append({"title": ev.get("headline", ""), "url": url})
    return tagged


def _today_mood(events: list[dict]) -> str | None:
    off = on = 0
    for ev in events:
        t = _event_text(ev)
        off += sum(1 for w in _RISK_OFF if w in t)
        on += sum(1 for w in _RISK_ON if w in t)
    if off == 0 and on == 0:
        return None
    if off > on * 1.4:
        return "risk-off"
    if on > off * 1.4:
        return "risk-on"
    return "mixed"


def build_global(events: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    overlay = _overlay_news(events)

    countries = []
    stats = {"cheap": 0, "fair": 0, "expensive": 0}
    for m in config.GLOBAL_MARKETS:
        rec = dict(m)
        rec["news"] = overlay.get(m.get("code", ""), [])
        band = m.get("valuation", "fair")
        if band in stats:
            stats[band] += 1
        countries.append(rec)

    rotation = config.MONEY_ROTATION.get("periods", [])
    current = dict(config.MONEY_ROTATION.get("current", {}) or {})
    mood = _today_mood(events)
    if mood:
        current["mood_today"] = mood

    return {
        "updated": now.strftime("%Y-%m-%d"),
        "updated_human": now.strftime("%A, %d %B %Y"),
        "note": config.MONEY_ROTATION.get("note", ""),
        "countries": countries,
        "stats": stats,
        "rotation": rotation,
        "current": current,
    }

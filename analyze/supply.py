"""
analyze/supply.py — assemble the Supply Lines data object.

Curated underneath, live on top:

  * knowledge/supply_lines.yaml carries the slow-moving part — who produces a
    big share of what, which narrow stretches of water it travels through, who
    depends on it, and what has gone wrong before.
  * Each morning's news is matched against those commodities and routes, so a
    disruption raises an alert on the day it is reported. That is the part that
    answers "tell me as soon as something happens".

Alert levels are calm -> watch -> alert, and they only ever go UP from the
curated baseline. A quiet news day does not clear a standing problem; only a
human editing the YAML does. Getting that backwards would mean the page
declared the Red Sea fine because nobody wrote about it that morning.

No Gemini, no paid data.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone

import config

_LEVELS = {"calm": 0, "watch": 1, "alert": 2}

# What a story has to mention for us to say it concerns this commodity.
# Narrow on purpose: "oil" alone would match cooking oil, olive oil and oil
# paintings, so the phrases carry their context with them.
_COMMODITY_KEYWORDS: dict[str, list[str]] = {
    "crude_oil":      ["crude", "brent", "wti", "opec", "oil price", "oil export",
                       "oil supply", "petroleum", "refinery", "oil output"],
    "natural_gas":    ["natural gas", "lng", "gas price", "gas supply", "pipeline gas",
                       "liquefied natural"],
    "rice":           ["rice export", "rice price", "rice ban", "basmati", "paddy"],
    "wheat":          ["wheat", "grain export", "grain deal", "flour price"],
    "palm_oil":       ["palm oil", "edible oil", "cooking oil", "vegetable oil",
                       "soybean oil", "sunflower oil"],
    "sugar":          ["sugar export", "sugar price", "sugar mill", "sugarcane",
                       "sugar output"],
    "fertiliser":     ["fertiliser", "fertilizer", "urea", "potash", "di-ammonium",
                       "phosphate"],
    "copper":         ["copper"],
    "iron_ore":       ["iron ore", "steel price", "steel output", "steel export"],
    "lithium":        ["lithium"],
    "cobalt":         ["cobalt"],
    "rare_earths":    ["rare earth", "rare-earth", "permanent magnet", "neodymium"],
    "semiconductors": ["semiconductor", "chip shortage", "chipmaker", "foundry",
                       "tsmc", "chip export", "advanced chips", "wafer"],
    "coffee":         ["coffee", "arabica", "robusta"],
    "cocoa":          ["cocoa", "chocolate price"],
    "gold":           ["gold price", "gold import", "bullion", "gold demand"],
    "shipping":       ["freight rate", "container rate", "shipping cost",
                       "charter rate", "port congestion", "box rate"],
    "soybeans":       ["soybean", "soyabean", "soymeal", "soya", "soy oil"],
    "corn":           ["corn price", "maize", "corn crop", "corn export"],
    "natural_rubber": ["natural rubber", "rubber price", "tyre cost"],
    "tea":            ["tea export", "tea price", "tea crop", "tea auction"],
    "spices":         ["spice", "cumin", "turmeric", "chilli", "cardamom",
                       "pepper price", "coriander"],
    "cotton":         ["cotton"],
    "onion":          ["onion"],
    "nickel":         ["nickel"],
    "aluminium":      ["aluminium", "aluminum", "bauxite", "alumina"],
    "graphite":       ["graphite", "anode material"],
    "uranium":        ["uranium", "nuclear fuel", "enrichment"],
    "phosphate":      ["phosphate", "dap ", "di-ammonium phosphate", "phosphoric"],
    "potash":         ["potash", "muriate of potash"],
    "palladium":      ["palladium", "platinum"],
    "silver":         ["silver price", "silver import", "silver demand"],
    "coal":           ["coal price", "coal import", "coal export", "coking coal",
                       "thermal coal", "coal shortage", "coal stock"],
    "chip_equipment": ["lithography", "asml", "chip equipment", "chipmaking tool",
                       "euv"],
    "pharma_api":     ["active pharmaceutical", "drug ingredient", "api export",
                       "bulk drug", "paracetamol", "medicine shortage"],
}

# Routes are named things, so these can be quite specific.
_ROUTE_KEYWORDS: dict[str, list[str]] = {
    "hormuz":          ["hormuz", "strait of hormuz", "persian gulf shipping"],
    "suez":            ["suez", "suez canal"],
    "bab_el_mandeb":   ["bab el-mandeb", "bab al-mandab", "red sea", "houthi",
                        "gulf of aden"],
    "malacca":         ["malacca", "strait of malacca", "singapore strait"],
    "panama":          ["panama canal", "gatun"],
    "turkish_straits": ["bosphorus", "dardanelles", "black sea", "turkish straits",
                        "grain corridor", "odesa", "odessa"],
    "cape":            ["cape of good hope", "around africa", "cape route"],
    "taiwan_strait":   ["taiwan strait", "taiwan tension", "taiwan blockade"],
}

# Words that turn a mention into a real problem — something is physically
# stopped, restricted or destroyed. Deliberately excludes price words: a price
# rising is the SYMPTOM, and treating every "crude surges" headline as a supply
# emergency puts the whole map on alert and makes the alerts worthless.
_DISRUPTION = [
    "blockade", "blocked", "closure", "closed", "shut down", "shuts", "halt",
    "halted", "suspend", "suspended", "attack", "sabotage", "strike at",
    "miners strike", "workers strike", "walkout", "shortage", "export ban",
    "import ban", "banned export", "bans export", "embargo", "force majeure",
    "cut output", "output falls", "production falls", "crop failure",
    "harvest fails", "drought", "flood", "cyclone", "frost", "outage",
    "export duty", "export levy", "export curb", "export restrict", "quota",
    "seized", "detained", "disrupt",
]

# A price move or a tension is worth noticing without being an emergency.
_CONCERN = [
    "surge", "spike", "soar", "record high", "jump", "rally", "tension",
    "escalat", "warn", "risk", "protest", "unrest", "sanction", "tariff",
    "shortfall", "tight supply", "stockpile",
]

# Words that say a problem is easing — enough to note, never enough to clear
# a curated alert on its own.
_EASING = ["resume", "reopen", "restored", "eased", "lifted", "normalis",
           "normaliz", "deal reached", "agreement reached", "returns to"]


def _event_text(ev: dict) -> str:
    """Raw news only — the headline and the source article titles. Our own
    analysis prose mentions oil and the rupee constantly and would light up
    every commodity on the board."""
    parts = [ev.get("headline", "")]
    for it in ev.get("items", []) or []:
        parts.append(it.get("title", ""))
    return " ".join(parts).lower()


def _match(events: list[dict], keywords: dict[str, list[str]]) -> dict[str, dict]:
    """{key: {level, news[], easing}} from today's stories."""
    out: dict[str, dict] = {}
    for ev in events:
        text = _event_text(ev)
        disrupted = any(w in text for w in _DISRUPTION)
        concern = any(w in text for w in _CONCERN)
        easing = any(w in text for w in _EASING)
        url = (ev.get("urls") or [""])[0]
        for key, kws in keywords.items():
            if not any(k in text for k in kws):
                continue
            # A bare mention is not news. Something has to be happening.
            if not (disrupted or concern or easing):
                continue
            rec = out.setdefault(key, {"level": "watch", "news": [], "easing": False})
            if disrupted and not easing:
                rec["level"] = "alert"
            if easing:
                rec["easing"] = True
            if len(rec["news"]) < 4:
                rec["news"].append({"title": ev.get("headline", ""), "url": url})
    return out


def _raise(current: str, candidate: str) -> str:
    """Status only ever goes up from the curated baseline."""
    return current if _LEVELS.get(current, 0) >= _LEVELS.get(candidate, 0) else candidate


def build_supply(events: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    kb = config.SUPPLY_LINES or {}
    commodities = kb.get("commodities", {}) or {}

    com_hits = _match(events, _COMMODITY_KEYWORDS)
    route_hits = _match(events, _ROUTE_KEYWORDS)

    # ---- routes -----------------------------------------------------------
    routes = []
    for r in kb.get("routes", []) or []:
        rec = json.loads(json.dumps(r))
        hit = route_hits.get(r["id"], {})
        level = _raise(rec.get("status", "calm"), hit.get("level", "calm"))
        # A route inherits concern from what it carries, but never an alert:
        # "crude oil surges" is not the Strait of Hormuz closing, and letting
        # one commodity story redden five straits at once would make the whole
        # map useless. Only the route being named can turn it red.
        if any(com_hits.get(c) for c in r.get("carries", [])):
            level = _raise(level, "watch")
        rec["status"] = level
        rec["news"] = hit.get("news", [])
        rec["live"] = bool(hit)
        rec["carries_detail"] = [
            {"key": c, **commodities.get(c, {})} for c in r.get("carries", [])
            if c in commodities
        ]
        routes.append(rec)

    # ---- countries --------------------------------------------------------
    countries = []
    for c in kb.get("countries", []) or []:
        rec = json.loads(json.dumps(c))
        worst = "calm"
        for sup in rec.get("supplies", []):
            hit = com_hits.get(sup["commodity"], {})
            level = _raise(sup.get("status", "calm"), hit.get("level", "calm"))
            sup["status"] = level
            sup["news"] = hit.get("news", [])
            sup["live"] = bool(hit)
            sup["info"] = commodities.get(sup["commodity"], {})
            worst = _raise(worst, level)
        rec["status"] = worst
        rec["emojis"] = [commodities.get(s["commodity"], {}).get("emoji", "")
                         for s in rec.get("supplies", [])]
        countries.append(rec)

    # ---- what is actually wrong right now ---------------------------------
    alerts = []
    for r in routes:
        if r["status"] == "alert":
            alerts.append({"kind": "route", "id": r["id"], "name": r["name"],
                           "what": r["headline"], "live": r["live"],
                           "news": r.get("news", [])})
    for c in countries:
        for s in c.get("supplies", []):
            if s["status"] == "alert":
                alerts.append({"kind": "country", "id": c["code"],
                               "name": f"{c['name']} · {s['info'].get('name', '')}",
                               "what": s["share"], "live": s["live"],
                               "news": s.get("news", [])})

    stats = {"alert": sum(1 for a in alerts), "live_today": sum(1 for a in alerts if a["live"])}
    print(f"  [supply] {len(countries)} countries, {len(routes)} routes · "
          f"{stats['alert']} on alert ({stats['live_today']} raised by today's news)")

    return {
        "updated": now.strftime("%Y-%m-%d"),
        "updated_human": now.strftime("%A, %d %B %Y"),
        "as_of": kb.get("updated", ""),
        "note": kb.get("note", ""),
        "commodities": commodities,
        "countries": countries,
        "routes": routes,
        "alerts": alerts,
        "stats": stats,
    }

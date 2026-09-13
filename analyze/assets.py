"""
analyze/assets.py — assemble the Asset Classes data object.

Same shape and same $0 rules as analyze/globe.py:
  * curated per-asset records (config.ASSET_CLASSES) — valuation versus each
    asset's OWN history, where the return comes from, and the real routes to
    buy it in India,
  * a LIVE news overlay — today's brief events tagged to the assets they
    actually concern, so each panel shows its current headwinds/tailwinds,
  * a LIVE regime read — which of the five "market weather" patterns today's
    news is pointing at, which is the thing worth learning.

No Gemini, no paid data, no live prices. Everything is labelled indicative.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone

import config

# Keywords that tie a news event to an asset, matched against the RAW news text
# (headline + what-happened + source titles), lower-cased. Deliberately narrow:
# a word like "rupee" appears in almost every India story and would tag
# everything to everything.
_ASSET_KEYWORDS: dict[str, list[str]] = {
    "LARGECAP":   ["nifty 50", "sensex", "large-cap", "largecap", "blue chip",
                   "benchmark index"],
    "MIDCAP":     ["midcap", "mid-cap", "mid cap"],
    "SMALLCAP":   ["smallcap", "small-cap", "small cap"],
    "BROAD":      ["nifty 500", "broader market", "total market"],
    "BANKS":      ["indian bank", "private bank", "psu bank", "public sector bank",
                   "bank nifty", "bank stock", "banking stock", "repo rate",
                   "credit growth", "loan growth", "npa", "non-performing",
                   "hdfc bank", "icici", "axis bank", "kotak", "state bank of india",
                   "nbfc", "deposit growth", "rbi policy", "rbi rate"],
    "IT":         ["it services", "software exports", "tcs", "infosys", "wipro",
                   "hcl tech", "tech mahindra", "nasscom", "it stocks",
                   "rupee slips", "rupee falls", "rupee weaken", "rupee depreciat",
                   "rupee hits record low", "rupee to record low"],
    "FMCG":       ["fmcg", "consumer goods", "hindustan unilever", "itc ",
                   "nestle", "britannia", "dabur", "marico", "rural demand"],
    "PHARMA":     ["pharma", "drugmaker", "drug maker", "usfda", "us fda",
                   "cipla", "sun pharma", "dr reddy", "medicine", "hospital"],
    "AUTO":       ["auto sales", "carmaker", "car maker", "two-wheeler",
                   "maruti", "tata motors", "mahindra", "bajaj auto",
                   "hero moto", "vehicle sales", "electric vehicle"],
    "ENERGY":     ["crude", "brent", "opec", "petrol", "diesel", "oil price",
                   "reliance", "ongc", "refiner", "electricity", "power demand",
                   "ntpc", "natural gas"],
    "METALS":     ["steel", "aluminium", "aluminum", "iron ore", "tata steel",
                   "hindalco", "vedanta", "coal india", "metal stocks", "zinc"],
    "REALTY":     ["realty", "real estate develop", "housing sales", "dlf",
                   "godrej propert", "lodha", "home loan", "property price"],
    "PSU":        ["psu", "public sector undertaking", "disinvest", "defence order",
                   "railway order", "hindustan aeronautics", "bharat electronics",
                   "state-owned"],
    "GOLD":       ["gold", "bullion", "sovereign gold bond"],
    "SILVER":     ["silver"],
    "COPPER":     ["copper"],
    "REALESTATE": ["property price", "housing price", "rental yield",
                   "home loan", "residential sales", "real estate price"],
    "REIT":       ["reit", "office space", "commercial real estate",
                   "office leasing"],
    "INVIT":      ["invit", "infrastructure trust", "toll collection",
                   "transmission asset"],
    "GSEC":       ["bond yield", "g-sec", "gsec", "gilt", "government bond",
                   "10-year yield", "fiscal deficit", "borrowing programme",
                   "government borrowing"],
    "CORPBOND":   ["corporate bond", "debt fund", "credit spread", "aaa-rated",
                   "rating downgrade"],
    "CASH":       ["fixed deposit", "deposit rate", "savings rate",
                   "liquid fund", "money market"],
    "SMALLSAV":   ["small savings", "ppf", "provident fund", "sukanya",
                   "epfo", "epf "],
    "INTL":       ["s&p 500", "nasdaq", "wall street", "dow jones",
                   "us stocks", "global equities", "federal reserve", "fed ",
                   "msci world", "rupee slips", "rupee falls", "rupee weaken",
                   "rupee depreciat", "rupee to record low"],
    "CRYPTO":     ["bitcoin", "crypto", "ether", "stablecoin"],
}

# Keywords that point at one of the five market-weather regimes. Used only to
# say "today's news smells like this" — never to claim we know what happens next.
_REGIME_KEYWORDS: dict[str, list[str]] = {
    "Inflation runs hot": [
        "inflation", "cpi", "wholesale price", "food price", "vegetable price",
        "price rise", "hawkish", "crude spike", "onion", "tomato", "wheat price"],
    "Interest rates come down": [
        "rate cut", "cuts rate", "dovish", "easing", "liquidity boost",
        "lower interest", "yield falls", "repo cut"],
    "The rupee weakens fast": [
        "rupee", "record low", "dollar index", "fii outflow", "forex reserves",
        "currency depreciat", "dollar strength"],
    "The world gets frightened": [
        "sell-off", "selloff", "risk-off", "safe haven", "war", "escalat",
        "plunge", "crash", "tariff", "sanction", "geopolitic", "conflict",
        "volatility spike"],
    "Growth is strong and boring": [
        "gdp growth", "record high", "rally", "profit growth", "strong earnings",
        "credit growth", "pmi", "capex", "order book", "hiring"],
}

_RISK_OFF = ["sell-off", "selloff", "outflow", "risk-off", "safe haven", "war",
             "escalat", "plunge", "crash", "tariff", "sanction", "record low"]
_RISK_ON = ["rally", "record high", "surge", "inflow", "risk-on", "rebound",
            "optimism", "rate cut"]


def _event_text(ev: dict) -> str:
    """Text used to tag an event to an asset: ONLY the genuinely raw news —
    the headline and the source article titles.

    Deliberately excludes the generated analysis, including what_happened.
    Our own prose routinely says "central banks", "the rupee", "equities",
    which tagged four US Fed stories onto Indian banks. The news itself does
    not use those words unless the story is really about them."""
    parts = [ev.get("headline", "")]
    for it in ev.get("items", []) or []:
        parts.append(it.get("title", ""))
    return " ".join(parts).lower()


def _regime_text(ev: dict) -> str:
    """The regime read is about the market WEATHER, not about one asset, so it
    can safely use the analysis too — a story only reaches the brief if our
    analysis found an India angle, and that angle is the signal here."""
    a = ev.get("analysis", {}) or {}
    return " ".join([_event_text(ev), a.get("what_happened", "")]).lower()


def _overlay_news(events: list[dict]) -> dict[str, list[dict]]:
    """Return {asset_code: [ {title, url}, ... ]} from today's events."""
    tagged: dict[str, list[dict]] = {}
    for ev in events:
        text = _event_text(ev)
        url = (ev.get("urls") or [""])[0]
        for code, kws in _ASSET_KEYWORDS.items():
            if any(k in text for k in kws):
                tagged.setdefault(code, [])
                if len(tagged[code]) < 4:
                    tagged[code].append({"title": ev.get("headline", ""),
                                         "url": url})
    return tagged


def _regime_signals(events: list[dict]) -> dict[str, int]:
    """How many of today's stories point at each market-weather regime."""
    hits: dict[str, int] = {}
    for name, kws in _REGIME_KEYWORDS.items():
        hits[name] = sum(1 for ev in events
                         if any(k in _regime_text(ev) for k in kws))
    return hits


def _today_mood(events: list[dict]) -> str | None:
    off = on = 0
    for ev in events:
        t = _regime_text(ev)
        off += sum(1 for w in _RISK_OFF if w in t)
        on += sum(1 for w in _RISK_ON if w in t)
    if off == 0 and on == 0:
        return None
    if off > on * 1.4:
        return "risk-off"
    if on > off * 1.4:
        return "risk-on"
    return "mixed"


def _total_return(asset: dict) -> float | None:
    """Sum of the return breakdown, on one basis for every asset: a nominal
    rupee return before tax. None when an asset has no cash flows to build an
    estimate from (crypto) — showing 0.0% there would be a claim, not a blank."""
    rows = asset.get("returns") or []
    if not rows:
        return None
    return round(sum(float(r.get("value") or 0) for r in rows), 1)


# How far from its own normal an asset has to be before we call it cheap or
# dear. Inside +/-8% is "fair" — the point is to flag a real gap, not to react
# to noise.
_CHEAP_AT = 0.92
_DEAR_AT = 1.08
# The marker bar spans 30% cheaper than normal to 30% dearer.
_SCALE = 0.60
# How much of the gap between today and normal we assume closes over a decade.
# Full reversion (1.0) is too confident; markets can stay mispriced for years.
_REVERSION = 0.60


def _num(v) -> str:
    """2.8 -> '2.8', 148.0 -> '148'."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:g}"


def _dearness(now_v: float, avg_v: float, direction: str) -> float | None:
    """How dear today is against this asset's own normal, as a multiple.
    Above 1 = dearer than usual, whichever way the metric runs."""
    if not now_v or not avg_v:
        return None
    return (avg_v / now_v) if direction == "high_cheap" else (now_v / avg_v)


def _pin(dear_x: float | None, fallback_pct) -> int:
    """Marker position on the history bar, 0-100. Live assets place it by
    distance from their own normal; curated ones keep their percentile."""
    if dear_x is None:
        return max(3, min(97, int(fallback_pct))) if fallback_pct is not None else 50
    pos = 50 + (dear_x - 1) / _SCALE * 100
    return int(max(3, min(97, round(pos))))


def _band(dear_x: float | None, curated: str) -> str:
    if dear_x is None:
        return curated
    if dear_x < _CHEAP_AT:
        return "cheap"
    if dear_x > _DEAR_AT:
        return "expensive"
    return "fair"


def _live_value(asset: dict, q: dict) -> tuple[float | None, list[dict], str]:
    """Today's real number for an asset, plus the live supporting figures and
    a source label. Returns (None, [], "") when nothing is reachable."""
    live = asset.get("live") or {}
    if not live or not q:
        return None, [], ""

    if live.get("source") == "nse_index":
        rec = (q.get("indices") or {}).get(str(live.get("index", "")).upper())
        if not rec:
            return None, [], ""
        val = rec.get(live.get("field"))
        if val is None:
            return None, [], ""
        extras = []
        if live.get("field") != "pe" and rec.get("pe") is not None:
            extras.append({"label": "PE ratio", "value": f"{_num(rec['pe'])}x",
                           "def": "Price divided by one year's profit, published "
                                  "by the NSE with today's close."})
        if live.get("field") != "pb" and rec.get("pb") is not None:
            extras.append({"label": "Price to book", "value": f"{_num(rec['pb'])}x",
                           "def": "What you pay for each rupee of the companies' "
                                  "net assets on paper. Live from the NSE."})
        if rec.get("div_yield") is not None:
            extras.append({"label": "Dividend yield", "value": f"{_num(rec['div_yield'])}%",
                           "def": "Cash paid out each year as a percentage of the "
                                  "price you pay. Live from the NSE."})
        if rec.get("close") is not None:
            chg = rec.get("change_pct")
            v = f"{rec['close']:,.0f}" + (f"  ({chg:+.2f}% today)" if chg is not None else "")
            extras.append({"label": "Index level", "value": v,
                           "def": "Where the index closed on the last trading day."})
        return val, extras, "NSE"

    if live.get("source") == "derived":
        val = (q.get("derived") or {}).get(live.get("key"))
        if val is None:
            return None, [], ""
        extras = []
        d = q.get("derived") or {}
        if d.get("SILVER_INR_KG"):
            extras.append({"label": "Silver today", "value": f"\u20b9{d['SILVER_INR_KG']:,.0f} a kg",
                           "def": "Spot silver converted into rupees at today's "
                                  "exchange rate."})
        if d.get("GOLD_INR_10G"):
            extras.append({"label": "Gold today", "value": f"\u20b9{d['GOLD_INR_10G']:,.0f} per 10g",
                           "def": "Spot gold converted into rupees at today's "
                                  "exchange rate."})
        return val, extras, "COMEX + ECB"

    return None, [], ""


def _premium_extra(code: str, q: dict) -> dict | None:
    """Mid and small caps live or die on their premium over the Nifty, so
    compute it from today's numbers rather than quoting a stale one."""
    idx = {"MIDCAP": "NIFTY MIDCAP 150", "SMALLCAP": "NIFTY SMALLCAP 250"}.get(code)
    if not idx:
        return None
    inds = q.get("indices") or {}
    me, big = inds.get(idx, {}).get("pe"), inds.get("NIFTY 50", {}).get("pe")
    if not me or not big:
        return None
    normal = "1.25x" if code == "MIDCAP" else "1.10x"
    return {"label": "Premium to large caps", "value": f"{me / big:.2f}x",
            "def": f"This segment's PE divided by the Nifty 50's. The long-run "
                   f"normal is about {normal}; well above it means you are paying "
                   f"for growth twice over. Computed from today's live numbers."}


def _apply_live(rec: dict, q: dict) -> dict:
    """Overlay today's real number and recompute everything that depends on
    it — the band, the marker, and the valuation-drift part of the return."""
    val, live_extras, source = _live_value(rec, q)
    if val is None:
        rec["live_ok"] = False
        return rec

    avg = rec.get("metric_avg")
    rec["metric_now"] = val
    rec["live_ok"] = True
    rec["live_source"] = source
    rec["live_as_of"] = q.get("nse_date") or ""

    prem = _premium_extra(rec.get("code", ""), q)
    if prem:
        live_extras.append(prem)

    # Live figures replace their curated equivalents; curated extras that have
    # no live counterpart (bad loans, dollar revenue share) survive.
    live_labels = {e["label"] for e in live_extras}
    kept = [e for e in (rec.get("extras") or []) if e.get("label") not in live_labels]
    rec["extras"] = live_extras + kept

    # Mean reversion over a decade, recomputed from today's gap to normal.
    dear_x = _dearness(val, avg, rec.get("metric_dir", "high_dear"))
    if dear_x and rec.get("returns"):
        # Assume the gap to normal only PARTLY closes over a decade. Assuming
        # it closes fully is the standard way these estimates end up flattering
        # whatever happens to be cheap today.
        closed = 1 + _REVERSION * (1 / dear_x - 1)
        drift = (closed ** 0.1 - 1) * 100 if closed > 0 else 0.0
        drift = round(max(-4.0, min(4.0, drift)), 1)
        for row in rec["returns"]:
            if str(row.get("label", "")).lower().startswith("valuation drift"):
                row["value"] = drift
                where = "above" if dear_x > 1 else "below"
                effect = ("so expect the price tag investors are willing to pay to "
                          "drift back down — a drag on returns"
                          if dear_x > 1 else
                          "so the price tag may drift back up, which adds to returns")
                row["def"] = (
                    f"Today's reading sits {where} this asset's own normal, {effect}. "
                    f"Worked out fresh each morning from the live number, assuming only "
                    f"about 60% of the gap closes over ten years — markets can stay "
                    f"mispriced for a long time.")
                break
    return rec


def _reading(rec: dict) -> str:
    """One generated sentence stating today's level, so the curated verdict can
    stay about the mechanism and never go stale."""
    now_v, avg = rec.get("metric_now"), rec.get("metric_avg")
    if now_v is None or avg is None:
        return ""
    dear_x = _dearness(now_v, avg, rec.get("metric_dir", "high_dear"))
    if not dear_x:
        return ""
    gap = abs(dear_x - 1) * 100
    unit = rec.get("metric_unit") or ""
    label = str(rec.get("metric_label", ""))   # keep its own case: "PE ratio"
    if gap < 3:
        how = "almost exactly its normal level"
    else:
        how = f"about {gap:.0f}% {'dearer' if dear_x > 1 else 'cheaper'} than usual"
    return (f"Today: {label} of {_num(now_v)}{unit} against a "
            f"{rec.get('metric_avg_label', 'long-run average').lower()} of "
            f"{_num(avg)}{unit} — {how}.")


def build_assets(events: list[dict], quotes: dict | None = None) -> dict:
    """Assemble the Asset Classes view model.

    `events` is today's analysed brief (news overlay + regime read). `quotes` is
    today's free market data; where an asset has a live number, it replaces the
    curated one and the band, marker and valuation drift are all recomputed."""
    now = datetime.now(timezone.utc)
    kb = config.ASSET_CLASSES or {}
    q = quotes or {}
    overlay = _overlay_news(events)
    signals = _regime_signals(events)

    assets: list[dict] = []
    stats = {"cheap": 0, "fair": 0, "expensive": 0, "no_anchor": 0}
    n_live = 0
    for a in kb.get("assets", []) or []:
        rec = _apply_live(json.loads(json.dumps(a)), q)
        rec["news"] = overlay.get(a.get("code", ""), [])
        rec["total_return"] = _total_return(rec)

        now_v, avg_v = rec.get("metric_now"), rec.get("metric_avg")
        dear_x = _dearness(now_v, avg_v, rec.get("metric_dir", "high_dear"))
        rec["dear"] = None if dear_x is None else dear_x > 1
        rec["pin"] = _pin(dear_x, rec.get("metric_pct"))
        # An asset with no way to value it keeps its curated band whatever
        # happens; everything else is banded from the live gap when we have one.
        curated_band = a.get("valuation", "fair")
        rec["valuation"] = (curated_band if curated_band == "no_anchor"
                            else _band(dear_x if rec.get("live_ok") else None,
                                       curated_band))
        rec["reading"] = _reading(rec) if rec.get("live_ok") else ""
        if rec["valuation"] in stats:
            stats[rec["valuation"]] += 1
        if rec.get("live_ok"):
            n_live += 1
        assets.append(rec)
    print(f"  [assets] {n_live} of {len(assets)} priced from live data")

    # Families, in the curated order, each carrying its own assets.
    families = []
    for f in kb.get("families", []) or []:
        members = [a for a in assets if a.get("family") == f.get("key")]
        if members:
            families.append({**f, "assets": members})

    regimes = []
    for r in kb.get("regimes", []) or []:
        regimes.append({**r, "signals": signals.get(r.get("name", ""), 0)})
    # The regime today's news points at hardest (ties -> none highlighted).
    top = sorted(regimes, key=lambda r: -r["signals"])
    leading = top[0]["name"] if top and top[0]["signals"] > 0 and (
        len(top) == 1 or top[0]["signals"] > top[1]["signals"]) else None

    live_ok = bool(q.get("ok", {}).get("nse"))
    return {
        "updated": now.strftime("%Y-%m-%d"),
        "updated_human": now.strftime("%A, %d %B %Y"),
        "as_of": kb.get("updated", ""),
        "live_ok": live_ok,
        "live_count": n_live,
        "live_as_of": q.get("nse_date") or "",
        "usd_inr": (q.get("usd_inr") if q else None),
        "gold_inr": (q.get("derived", {}) or {}).get("GOLD_INR_10G"),
        "note": kb.get("note", ""),
        "assets": assets,
        "families": families,
        "gauges": kb.get("gauges", []) or [],
        "regimes": regimes,
        "leading_regime": leading,
        "mood_today": _today_mood(events),
        "stats": stats,
    }

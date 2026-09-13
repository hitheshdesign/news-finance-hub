"""
ingest/quotes.py — free daily market numbers for the Asset Classes page.

Three sources, all free, none needing an API key:

  * NSE's own published index file (nsearchives.nseindia.com) — the daily close
    plus **P/E, P/B and dividend yield for every NSE index**. This is the real
    prize: it makes the whole equity half of the Asset Classes page live rather
    than hand-curated.
  * Yahoo's chart endpoint — gold, silver and copper futures in dollars.
  * Frankfurter (European Central Bank data) — USD/INR.

Everything degrades gracefully. If a source is unreachable the page falls back
to the curated number and says so, rather than showing a stale figure as if it
were live. That matters here: NSE may well block GitHub Actions' datacentre IP
even though it answers from a home connection.
"""

from __future__ import annotations
import csv
import io
import json
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

import config

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_TIMEOUT = 25

# Yahoo futures symbols -> what we call them.
_SPOT = {"GOLD": "GC=F", "SILVER": "SI=F", "COPPER": "HG=F"}

# Troy ounces in 10 grams — gold and silver are quoted per ounce, India buys
# gold by the 10 grams and silver by the kilogram.
_OZ_PER_10G = 10.0 / 31.1035
_OZ_PER_KG = 1000.0 / 31.1035


def _get(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def _f(v) -> float | None:
    """NSE writes '-' for a missing value and '.59' for 0.59."""
    try:
        s = str(v).strip()
        if not s or s in ("-", "NA", "N/A"):
            return None
        return float(s)
    except (TypeError, ValueError):
        return None


def _nse_indices() -> tuple[dict, str | None]:
    """{INDEX NAME: {close, pe, pb, div_yield}} from NSE's daily index file.

    Walks back a few days because of weekends and holidays — the file only
    exists for trading days."""
    today = datetime.now(timezone.utc).date()
    for back in range(0, 7):
        day = today - timedelta(days=back)
        if day.weekday() >= 5:                 # Sat/Sun: no file
            continue
        url = ("https://nsearchives.nseindia.com/content/indices/"
               f"ind_close_all_{day.strftime('%d%m%Y')}.csv")
        try:
            body = _get(url)
        except Exception:
            continue
        try:
            rows = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig"))))
        except Exception:
            continue
        out = {}
        for r in rows:
            name = (r.get("Index Name") or "").strip().upper()
            if not name:
                continue
            out[name] = {
                "close": _f(r.get("Closing Index Value")),
                "change_pct": _f(r.get("Change(%)")),
                "pe": _f(r.get("P/E")),
                "pb": _f(r.get("P/B")),
                "div_yield": _f(r.get("Div Yield")),
            }
        if out:
            return out, day.isoformat()
    return {}, None


def _yahoo(symbol: str) -> float | None:
    try:
        raw = _get("https://query1.finance.yahoo.com/v8/finance/chart/"
                   f"{urllib.parse.quote(symbol)}?interval=1d&range=5d")
        meta = json.loads(raw)["chart"]["result"][0]["meta"]
        return _f(meta.get("regularMarketPrice"))
    except Exception:
        return None


def _usd_inr() -> float | None:
    try:
        raw = _get("https://api.frankfurter.app/latest?from=USD&to=INR")
        return _f(json.loads(raw)["rates"]["INR"])
    except Exception:
        return None


def fetch() -> dict:
    """Today's numbers. Always returns a dict; `ok` flags say what arrived."""
    print("[quotes] fetching free daily market numbers...")
    indices, nse_date = _nse_indices()
    spot = {k: _yahoo(sym) for k, sym in _SPOT.items()}
    fx = _usd_inr()

    derived: dict[str, float] = {}
    if spot.get("GOLD") and fx:
        derived["GOLD_INR_10G"] = round(spot["GOLD"] * _OZ_PER_10G * fx, 0)
    if spot.get("SILVER") and fx:
        derived["SILVER_INR_KG"] = round(spot["SILVER"] * _OZ_PER_KG * fx, 0)
    if spot.get("GOLD") and spot.get("SILVER"):
        derived["GOLD_SILVER_RATIO"] = round(spot["GOLD"] / spot["SILVER"], 1)

    data = {
        "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nse_date": nse_date,
        "indices": indices,
        "spot_usd": spot,
        "usd_inr": fx,
        "derived": derived,
        "ok": {
            "nse": bool(indices),
            "metals": any(spot.values()),
            "fx": fx is not None,
        },
    }
    print(f"  [quotes] NSE indices: {len(indices)}"
          f"{' (as of ' + nse_date + ')' if nse_date else ' — UNREACHABLE, using curated'}"
          f" · metals: {'ok' if data['ok']['metals'] else 'unreachable'}"
          f" · USD/INR: {fx if fx else 'unreachable'}")
    return data


def store(data: dict) -> Path | None:
    """Keep a dated copy so the history is there if we ever want to chart it."""
    out_dir = config.DATA_DIR.parent / "quotes"
    out_dir.mkdir(parents=True, exist_ok=True)
    day = data.get("nse_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = out_dir / f"{day}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

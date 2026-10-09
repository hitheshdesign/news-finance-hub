"""
render/web.py — build the static web page(s) for GitHub Pages from a brief.
Produces:
  site/index.html          -> the latest brief
  site/briefs/<date>.html  -> a dated archive copy
Never needs a server: it's plain HTML the browser opens directly.
"""

from __future__ import annotations
import json
import shutil
from pathlib import Path
from jinja2 import Environment
from markupsafe import Markup

import config
from render import templates, global_page, assets_page, supply_page, worldmap
from render.glossary import annotate

# CSS is trusted, pre-written stylesheet text. Mark it safe so Jinja's autoescape
# does not turn quotes inside selectors/content rules into &#34; (which breaks
# [data-theme="light"] selectors and every content:"" pseudo-element).
_CSS = Markup(templates.CSS)
_ICON = Markup(templates.HEAD_ICON)      # favicon / theme-color tags
_LOGO = Markup(templates.LOGO_INLINE)    # brand mark, tinted per page
_TIPJS = Markup(templates.TIP_FIT_JS)    # keeps panel tooltips on-screen
_THEMEBOOT = Markup(templates.THEME_BOOT)   # applies a stored theme pre-paint
_THEMEBTN = Markup(templates.THEME_BTN)     # the light/dark button
_THEMEJS = Markup(templates.THEME_JS)       # its click handler


def _nav(active: str, prefix: str = "") -> Markup:
    """Shared top-tab navigation used by every page. `active` is one of
    news|supply|global|assets|learn; `prefix` (e.g. '../') fixes links for archived pages
    that live one folder deeper."""
    tabs = [
        ("news", "index.html", "News"),
        ("supply", "supply.html", "Supply Lines"),
        ("global", "global.html", "Global Finance"),
        ("assets", "assets.html", "Asset Classes"),
        ("learn", "patterns.html", "Learn"),
    ]
    items = "".join(
        f'<a href="{prefix}{href}" class="tab{" on" if key == active else ""}">{label}</a>'
        for key, href, label in tabs
    )
    return Markup(f'<nav class="tabs">{items}</nav>')


def _dots(level: str) -> Markup:
    """Render a 3-dot likelihood/confidence meter for High/Medium/Low."""
    filled = {"high": 3, "medium": 2, "low": 1}.get(str(level).lower(), 0)
    pips = "".join(
        f'<i class="{"on" if i < filled else ""}"></i>' for i in range(3)
    )
    return Markup(f'<span class="dots" aria-hidden="true">{pips}</span>')


def _env() -> Environment:
    env = Environment(autoescape=True)
    # `gloss` = wrap finance jargon with tap-to-define tooltips.
    # `dots`  = a small visual meter for likelihood/confidence.
    env.filters["gloss"] = annotate
    env.filters["dots"] = _dots
    card_tpl = env.from_string(templates.CARD)
    # expose the card as a callable inside the page template.
    # Markup(...) marks the already-rendered (and escaped) card HTML as safe so
    # the page template doesn't double-escape it into visible tags.
    env.globals["card"] = lambda ev: Markup(card_tpl.render(ev=ev))
    return env


def _archive_list(current_date: str) -> list[dict]:
    """Scan stored briefs to build a small 'past briefs' nav (newest first)."""
    briefs_dir = config.DATA_DIR
    if not briefs_dir.exists():
        return []
    dates = sorted(
        [p.stem for p in briefs_dir.glob("*.json")],
        reverse=True,
    )
    out = []
    for d in dates:
        if d == current_date:
            continue
        out.append({"label": d, "href": f"briefs/{d}.html"})
    return out[:14]


# Keys the page template reads that older stored briefs may predate. Re-rendering
# the archive after a design change replays every payload we have ever written,
# so a field added in September must not break an August brief.
_BRIEF_DEFAULTS = {
    "calendar_alert_days": 4,
    "calendar_alert": 0,
    "calendar": [],
    "deeper_reads": [],
    "history": None,
    "macro": None,
}


def render_page(brief: dict) -> str:
    env = _env()
    # archive links are relative to site/ root (index) — dated pages fix paths below
    brief = {**_BRIEF_DEFAULTS, **brief}
    brief["archive"] = _archive_list(brief["date"])
    page = env.from_string(templates.PAGE)
    return page.render(brief=brief, css=_CSS, fonts=templates.FONTS,
                       nav=_nav("news"), icon=_ICON, logo=_LOGO, themeboot=_THEMEBOOT,
                       themebtn=_THEMEBTN, themejs=_THEMEJS)


def render_patterns() -> str:
    """Render the Pattern Library: every knowledge-base linkage, grouped by
    category, as a browsable learning reference."""
    env = _env()
    groups: list[dict] = []
    index: dict[str, dict] = {}
    for lk in config.TRANSMISSION:
        cat = lk.get("category", "general")
        if cat not in index:
            index[cat] = {"category": cat, "linkages": []}
            groups.append(index[cat])
        index[cat]["linkages"].append(lk)
    total = sum(len(g["linkages"]) for g in groups)
    page = env.from_string(templates.PATTERNS_PAGE)
    return page.render(groups=groups, total=total,
                       css=_CSS, fonts=templates.FONTS,
                       nav=_nav("learn"), icon=_ICON, logo=_LOGO, themeboot=_THEMEBOOT,
                       themebtn=_THEMEBTN, themejs=_THEMEJS)


# Markets too small to appear on a 110m-resolution map — drawn as a dot instead.
# (longitude, latitude)
_MICRO = {"HK": (114.2, 22.3)}
_VCLASS = {"cheap": "v-cheap", "fair": "v-fair", "expensive": "v-exp"}
# Signal value -> heat-map cell class (JS-safe names; "m" = minus).
_SIG_CLS = {2: "s2", 1: "s1", 0: "s0", -1: "sm1", -2: "sm2"}

# Fields the client-side detail panel needs (keeps the inline JSON lean).
_PANEL_FIELDS = (
    "name", "index", "region", "valuation", "cape_now", "cape_avg", "cape_pct",
    "pb", "div_yield", "roe", "top10_weight", "govt_debt_gdp", "rule_of_law",
    "demographics", "worst_drawdown", "er_growth", "er_dividend", "er_valuation",
    "er_currency", "currency_note", "access", "economy", "sectors",
    "upside", "downside", "outlook", "verdict", "india_angle", "news",
)


def _xy(lon: float, lat: float) -> tuple[float, float]:
    """Lon/lat -> x,y on the generated map canvas (1000x500, poles cropped).
    Must match the projection used to build render/worldmap.py."""
    lat_max, lat_min = 83.0, -56.0
    x = (lon + 180.0) / 360.0 * 1000.0
    lat = max(min(lat, lat_max), lat_min)
    y = (lat_max - lat) / (lat_max - lat_min) * 500.0
    return round(x, 1), round(y, 1)


def _json_safe(obj) -> Markup:
    """JSON for an inline <script> — neutralise any </script> breakout."""
    return Markup(json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c"))


def render_global(gdata: dict) -> str:
    env = _env()
    covered = {c.get("code"): c for c in gdata.get("countries", [])}

    # 1. The choropleth: every real country path, coloured if we cover it.
    map_countries = []
    for iso, d in worldmap.PATHS.items():
        c = covered.get(iso)
        cls = f"{c['valuation']} has" if c else ""
        map_countries.append({"code": iso if c else "", "cls": cls, "d": d})

    # 2. Dots for markets too small to render as a shape (e.g. Hong Kong).
    map_dots = []
    for iso, (lon, lat) in _MICRO.items():
        c = covered.get(iso)
        if not c:
            continue
        x, y = _xy(lon, lat)
        map_dots.append({"code": iso, "x": x, "y": y,
                         "cls": f"{c['valuation']} has"})

    # 3. Rotation periods: precompute heat-map cell classes per bucket.
    buckets = config.MONEY_ROTATION.get("buckets", [])
    rotation = []
    for p in gdata.get("rotation", []):
        sig = p.get("signals", {}) or {}
        rec = dict(p)
        rec["cls"] = {b["key"]: _SIG_CLS.get(int(sig.get(b["key"], 0)), "s0")
                      for b in buckets}
        rec["gold_spike"] = int(sig.get("GOLD", 0)) == 2
        rotation.append(rec)

    view = dict(gdata)
    view["rotation"] = rotation
    view["buckets"] = buckets

    js_map = {code: {k: c.get(k) for k in _PANEL_FIELDS}
              for code, c in covered.items()}
    rot_json = [{"period": p.get("period"),
                 "why": p.get("headline") or p.get("trigger", "")} for p in rotation]

    page = env.from_string(global_page.GLOBAL_PAGE)
    return page.render(g=view, map_countries=map_countries, map_dots=map_dots,
                       g_json=_json_safe(js_map), rot_json=_json_safe(rot_json),
                       css=_CSS, fonts=templates.FONTS, nav=_nav("global"),
                       icon=_ICON, logo=_LOGO, themeboot=_THEMEBOOT,
                       themebtn=_THEMEBTN, themejs=_THEMEJS, tipjs=_TIPJS)


def write_global_page(gdata: dict) -> Path:
    site = config.SITE_DIR
    site.mkdir(parents=True, exist_ok=True)
    html = render_global(gdata)
    path = site / "global.html"
    path.write_text(html, encoding="utf-8")
    print(f"  [web] wrote {path}")
    return path


# ---------------------------------------------------------------- Asset Classes
# Human-facing labels for the four valuation bands. "no_anchor" is deliberate:
# some things (crypto) have no earnings, rent or interest to value them against.
_BAND_LABEL = {
    "cheap": "Cheap vs its past", "fair": "Fairly priced",
    "expensive": "Dear vs its past", "no_anchor": "Cannot be valued",
}
_BAND_SHORT = {
    "cheap": "Cheap", "fair": "Fair", "expensive": "Dear", "no_anchor": "No anchor",
}
_BAND_CLS = {
    "cheap": "v-cheap", "fair": "v-fair", "expensive": "v-exp", "no_anchor": "v-none",
}

# Fields the client-side detail panel needs (keeps the inline JSON lean).
_ASSET_FIELDS = (
    "code", "name", "short", "proxy", "family_label", "valuation", "vc",
    "band_label", "band_short", "metric_label", "metric_def", "metric_now",
    "metric_avg", "metric_avg_label", "metric_show", "metric_avg_show",
    "metric_pct", "metric_avg_short", "pin", "heat", "gap_show", "dear",
    "reading", "live_ok",
    "live_source", "live_as_of", "extras", "what_it_is", "own", "composition",
    "returns", "return_note", "total_return", "total_show", "history", "worst_fall",
    "drivers_up", "drivers_down", "wins_when", "role", "how_to_invest",
    "tax", "watch", "verdict", "news",
)


def _num(v) -> str:
    """2.8 -> '2.8', 148.0 -> '148'. Keeps the tiles from reading '148.0'."""
    if v is None:
        return ""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:g}"


def _decorate_asset(a: dict, family_labels: dict[str, str]) -> dict:
    """Add the display-only fields the template and the detail panel read."""
    band = a.get("valuation", "fair")
    unit = a.get("metric_unit") or ""
    rec = dict(a)
    rec["vc"] = _BAND_CLS.get(band, "v-fair")
    rec["band_label"] = _BAND_LABEL.get(band, band)
    rec["band_short"] = _BAND_SHORT.get(band, band)
    rec["family_label"] = family_labels.get(a.get("family", ""), "")
    rec["metric_show"] = (_num(a.get("metric_now")) + unit
                          if a.get("metric_now") is not None else "—")
    rec["metric_avg_show"] = (_num(a.get("metric_avg")) + unit
                              if a.get("metric_avg") is not None else "—")
    # analyze/assets.py already places the marker — from the live gap to this
    # asset's own normal where we have live data, from the curated percentile
    # otherwise. Only fall back if it somehow did not.
    if rec.get("pin") is None:
        pct = a.get("metric_pct")
        rec["pin"] = max(3, min(97, int(pct))) if pct is not None else 50
    # Five-step colour, from the same distance-from-normal that places the
    # marker. Kept here rather than in CSS so the thresholds are visible and
    # arguable in one place.
    pin = rec["pin"]
    if band == "no_anchor" or a.get("metric_now") is None:
        rec["heat"] = "na"
        rec["gap_show"] = "cannot be valued"
    else:
        rec["heat"] = ("c2" if pin < 20 else "c1" if pin < 38 else
                       "n" if pin <= 62 else "d1" if pin <= 80 else "d2")
        now_v, avg_v = a.get("metric_now"), a.get("metric_avg")
        if avg_v:
            direction = a.get("metric_dir", "high_dear")
            dear = (avg_v / now_v) if direction == "high_cheap" else (now_v / avg_v)
            pct = abs(dear - 1) * 100
            if pct < 3:
                rec["gap_show"] = "about normal"
            else:
                rec["gap_show"] = f"{pct:.0f}% {'dearer' if dear > 1 else 'cheaper'}"
        else:
            rec["gap_show"] = ""

    total = a.get("total_return")
    rec["total_show"] = ("—" if total is None
                         else f"{'+' if total > 0 else ''}{total:.1f}%")
    return rec


def render_assets(adata: dict) -> str:
    env = _env()
    family_labels = {f.get("key"): f.get("label", "") for f in adata.get("families", [])}

    assets = [_decorate_asset(a, family_labels) for a in adata.get("assets", [])]
    by_code = {a["code"]: a for a in assets}

    families = []
    for f in adata.get("families", []):
        members = [by_code[a["code"]] for a in f.get("assets", []) if a["code"] in by_code]
        families.append({**f, "assets": members})

    view = dict(adata)
    view["families"] = families
    # The record list reads best strongest-first, with anything that has no
    # honest estimate (crypto) at the end rather than sorted as a zero.
    view["by_return"] = sorted(
        assets,
        key=lambda x: (x.get("total_return") is None, -(x.get("total_return") or 0)))
    view["gauges"] = [{**g, "vc": _BAND_CLS.get(g.get("verdict", "fair"), "v-fair")}
                      for g in adata.get("gauges", [])]

    js = {a["code"]: {k: a.get(k) for k in _ASSET_FIELDS} for a in assets}
    page = env.from_string(assets_page.ASSETS_PAGE)
    return page.render(a=view, a_json=_json_safe(js), css=_CSS,
                       fonts=templates.FONTS, nav=_nav("assets"),
                       icon=_ICON, logo=_LOGO, themeboot=_THEMEBOOT,
                       themebtn=_THEMEBTN, themejs=_THEMEJS, tipjs=_TIPJS)


def write_assets_page(adata: dict) -> Path:
    site = config.SITE_DIR
    site.mkdir(parents=True, exist_ok=True)
    html = render_assets(adata)
    path = site / "assets.html"
    path.write_text(html, encoding="utf-8")
    print(f"  [web] wrote {path}")
    return path


# ------------------------------------------------------------------ Supply Lines
# Routes are drawn as polylines and producers as emoji markers, both projected
# with the same _xy() the choropleth uses so everything lines up.
_ST_CLS = {"calm": "st-calm", "watch": "st-watch", "alert": "st-alert"}
# How many commodity emojis fit on one map marker before it is summarised.
_MARK_MAX = 3


def _points(path: list) -> str:
    """[[lon,lat],...] -> an SVG points attribute."""
    return " ".join("%s,%s" % _xy(float(lon), float(lat)) for lon, lat in path)


def render_supply(sdata: dict) -> str:
    env = _env()
    by_code = {c["code"]: c for c in sdata.get("countries", [])}

    # 1. Country shapes, tinted by the worst state of anything they supply.
    map_countries = []
    for iso, d in worldmap.PATHS.items():
        c = by_code.get(iso)
        cls = f"has {_ST_CLS.get(c['status'], 'st-calm')}" if c else ""
        map_countries.append({"code": iso if c else "", "cls": cls, "d": d})

    # 2. Shipping routes.
    map_routes = []
    for r in sdata.get("routes", []):
        lx, ly = _xy(float(r["label"][0]), float(r["label"][1]))
        map_routes.append({
            "id": r["id"], "short": r.get("short", r["name"]),
            "cls": _ST_CLS.get(r.get("status", "calm"), "st-calm"),
            "points": _points(r.get("path", [])),
            "lx": lx, "ly": ly - 9,
        })

    # 3. One marker per producer, carrying its commodity emojis.
    map_marks = []
    for c in sdata.get("countries", []):
        at = c.get("at") or []
        if len(at) != 2:
            continue
        cx, cy = _xy(float(at[0]), float(at[1]))
        all_e = [e for e in c.get("emojis", []) if e]
        # India supplies eight things. Showing eight emojis would blot out its
        # neighbours, so the marker shows the first few and a count; the panel
        # lists every one.
        shown, extra = all_e[:_MARK_MAX], max(len(all_e) - _MARK_MAX, 0)
        # A rough first width so the marker is not invisible before scripting
        # runs; sizeMarkers() in the page measures the real text and corrects it.
        w = 10 + 16 * len(shown) + (14 if extra else 0)
        map_marks.append({
            "code": c["code"], "cx": cx, "cy": cy,
            "x": round(cx - w / 2, 1), "y": round(cy - 9, 1),
            "w": w, "h": 18, "emojis": "".join(shown),
            "more": f"+{extra}" if extra else "",
            "cls": _ST_CLS.get(c.get("status", "calm"), "st-calm"),
        })

    page = env.from_string(supply_page.SUPPLY_PAGE)
    return page.render(s=sdata, map_countries=map_countries, map_routes=map_routes,
                       map_marks=map_marks, s_json=_json_safe(sdata), css=_CSS,
                       fonts=templates.FONTS, nav=_nav("supply"),
                       icon=_ICON, logo=_LOGO, tipjs=_TIPJS,
                       themeboot=_THEMEBOOT, themebtn=_THEMEBTN, themejs=_THEMEJS)


def write_supply_page(sdata: dict) -> Path:
    site = config.SITE_DIR
    site.mkdir(parents=True, exist_ok=True)
    html = render_supply(sdata)
    path = site / "supply.html"
    path.write_text(html, encoding="utf-8")
    print(f"  [web] wrote {path}")
    return path


def write_patterns_page() -> Path:
    """Write site/patterns.html (and a copy under site/briefs/ so links from the
    dated archive pages resolve too)."""
    site = config.SITE_DIR
    (site / "briefs").mkdir(parents=True, exist_ok=True)
    html = render_patterns()
    path = site / "patterns.html"
    path.write_text(html, encoding="utf-8")
    (site / "briefs" / "patterns.html").write_text(html, encoding="utf-8")
    print(f"  [web] wrote {path}")
    return path


def _copy_assets() -> None:
    """Copy static brand assets (favicon.ico, apple-touch-icon.png, favicon.svg)
    to the site root. Browsers request /favicon.ico and /apple-touch-icon.png
    from the domain root automatically, so these need no <link> tag and work
    from every page depth — including the dated archive pages."""
    src = config.ROOT / "assets"
    if not src.exists():
        return
    config.SITE_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("favicon.ico", "favicon.svg", "apple-touch-icon.png"):
        f = src / name
        if f.exists():
            shutil.copyfile(f, config.SITE_DIR / name)


def write_site(brief: dict) -> Path:
    site = config.SITE_DIR
    (site / "briefs").mkdir(parents=True, exist_ok=True)
    _copy_assets()

    # index.html (latest)
    html = render_page(brief)
    index_path = site / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # dated copy (archive) — fix relative links (it lives one folder deeper):
    # archive links drop the briefs/ prefix; the top-tab links gain a ../ prefix
    # (these three hrefs only occur in the nav on the news page).
    dated_html = (html
                  .replace('href="briefs/', 'href="')
                  .replace('href="index.html"', 'href="../index.html"')
                  .replace('href="global.html"', 'href="../global.html"')
                  .replace('href="assets.html"', 'href="../assets.html"')
                  .replace('href="supply.html"', 'href="../supply.html"')
                  .replace('href="patterns.html"', 'href="../patterns.html"'))
    dated_path = site / "briefs" / f"{brief['date']}.html"
    dated_path.write_text(dated_html, encoding="utf-8")

    print(f"  [web] wrote {index_path} and {dated_path}")
    return index_path

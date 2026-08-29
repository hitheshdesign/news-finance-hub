"""
render/web.py — build the static web page(s) for GitHub Pages from a brief.
Produces:
  site/index.html          -> the latest brief
  site/briefs/<date>.html  -> a dated archive copy
Never needs a server: it's plain HTML the browser opens directly.
"""

from __future__ import annotations
import json
from pathlib import Path
from jinja2 import Environment
from markupsafe import Markup

import config
from render import templates, global_page, worldmap
from render.glossary import annotate

# CSS is trusted, pre-written stylesheet text. Mark it safe so Jinja's autoescape
# does not turn quotes inside selectors/content rules into &#34; (which breaks
# [data-theme="light"] selectors and every content:"" pseudo-element).
_CSS = Markup(templates.CSS)


def _nav(active: str, prefix: str = "") -> Markup:
    """Shared top-tab navigation used by every page. `active` is one of
    news|global|learn; `prefix` (e.g. '../') fixes links for archived pages
    that live one folder deeper."""
    tabs = [
        ("news", "index.html", "News"),
        ("global", "global.html", "Global Finance"),
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


def render_page(brief: dict) -> str:
    env = _env()
    # archive links are relative to site/ root (index) — dated pages fix paths below
    brief = dict(brief)
    brief["archive"] = _archive_list(brief["date"])
    page = env.from_string(templates.PAGE)
    return page.render(brief=brief, css=_CSS, fonts=templates.FONTS,
                       nav=_nav("news"))


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
                       nav=_nav("learn"))


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
    "er_currency", "currency_note", "access", "risks", "tailwinds", "headwinds",
    "outlook", "verdict", "india_angle", "news",
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
    rot_json = [{"period": p.get("period"), "why": p.get("why")} for p in rotation]

    page = env.from_string(global_page.GLOBAL_PAGE)
    return page.render(g=view, map_countries=map_countries, map_dots=map_dots,
                       g_json=_json_safe(js_map), rot_json=_json_safe(rot_json),
                       css=_CSS, fonts=templates.FONTS, nav=_nav("global"))


def write_global_page(gdata: dict) -> Path:
    site = config.SITE_DIR
    site.mkdir(parents=True, exist_ok=True)
    html = render_global(gdata)
    path = site / "global.html"
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


def write_site(brief: dict) -> Path:
    site = config.SITE_DIR
    (site / "briefs").mkdir(parents=True, exist_ok=True)

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
                  .replace('href="patterns.html"', 'href="../patterns.html"'))
    dated_path = site / "briefs" / f"{brief['date']}.html"
    dated_path.write_text(dated_html, encoding="utf-8")

    print(f"  [web] wrote {index_path} and {dated_path}")
    return index_path

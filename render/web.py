"""
render/web.py — build the static web page(s) for GitHub Pages from a brief.
Produces:
  site/index.html          -> the latest brief
  site/briefs/<date>.html  -> a dated archive copy
Never needs a server: it's plain HTML the browser opens directly.
"""

from __future__ import annotations
from pathlib import Path
from jinja2 import Environment
from markupsafe import Markup

import config
from render import templates


def _env() -> Environment:
    env = Environment(autoescape=True)
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
    return page.render(brief=brief, css=templates.CSS)


def write_site(brief: dict) -> Path:
    site = config.SITE_DIR
    (site / "briefs").mkdir(parents=True, exist_ok=True)

    # index.html (latest)
    html = render_page(brief)
    index_path = site / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # dated copy (archive) — fix relative links (it lives one folder deeper)
    dated_html = html.replace('href="briefs/', 'href="')
    dated_path = site / "briefs" / f"{brief['date']}.html"
    dated_path.write_text(dated_html, encoding="utf-8")

    print(f"  [web] wrote {index_path} and {dated_path}")
    return index_path

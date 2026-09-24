"""
ingest/article.py — fetch the actual text of the stories we are about to write
about.

Until now the analyser was handed nothing but a headline and asked to produce a
full card. With no article to work from it had no choice but to generalise, so
cards about specific reporting came out as generic macro prose — "South Korea is
figuring out how to protect its economy" — which is not what the article said
and not worth reading.

This fetches the body text so the analysis is grounded in what was actually
reported. It runs only on the handful of stories that made the brief (about
nine a day), after selection and before analysis, so it is a few polite requests
per run and costs nothing.

Extraction is a deliberately small heuristic rather than a dependency: take the
<p> text, drop the short fragments and the obvious furniture (cookie notices,
newsletter pitches, share prompts). That handles ordinary news pages well and
fails cleanly on the ones it cannot read — and failing cleanly matters, because
an empty result tells the analyser to stay quiet rather than invent.
"""

from __future__ import annotations
import html
import re
import time
from html.parser import HTMLParser

import requests

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Containers whose text is never the story.
_SKIP_TAGS = {
    "script", "style", "nav", "header", "footer", "aside", "form", "noscript",
    "figure", "figcaption", "iframe", "svg", "button", "select", "template",
}

# Paragraphs that are site furniture rather than reporting.
_BOILERPLATE = (
    "cookie", "subscribe", "subscription", "newsletter", "sign up", "sign in",
    "log in", "all rights reserved", "follow us", "share this", "read more at",
    "terms of service", "privacy policy", "advertisement", "click here",
    "download the app", "already a member", "you have exhausted", "free articles",
    "gain access to content", "become a member", "support our work",
    "this article is free", "enjoying this article",
)

_MIN_PARA = 45          # shorter than this is almost always a caption or a link
_MIN_USABLE = 400       # below this we treat the fetch as failed


class _Paragraphs(HTMLParser):
    """Collect the text inside <p> tags, ignoring scripted/navigational parts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paras: list[str] = []
        self._skip = 0
        self._in_p = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip += 1
        elif tag == "p" and not self._skip:
            self._in_p = True
            self._buf = []
        elif tag == "br" and self._in_p:
            self._buf.append(" ")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag == "p" and self._in_p:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                self.paras.append(text)
            self._in_p = False
            self._buf = []

    def handle_data(self, data):
        if self._in_p and not self._skip:
            self._buf.append(data)


def _clean(paras: list[str]) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for p in paras:
        if len(p) < _MIN_PARA:
            continue
        low = p.lower()
        if any(b in low for b in _BOILERPLATE):
            continue
        key = low[:80]
        if key in seen:              # repeated standfirst / teaser blocks
            continue
        seen.add(key)
        out.append(p)
    return "\n\n".join(out)


def fetch_text(url: str, max_chars: int = 6000, timeout: int = 20) -> str:
    """The readable body of one article, or "" if it could not be read."""
    if not url or not url.startswith("http"):
        return ""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=timeout)
        if r.status_code != 200:
            return ""
        ctype = (r.headers.get("content-type") or "").lower()
        if "html" not in ctype:
            return ""
        # A few MB of markup is a page we do not want to parse anyway.
        if len(r.content) > 4_000_000:
            return ""
        parser = _Paragraphs()
        parser.feed(r.text)
        text = _clean(parser.paras)
    except Exception:
        return ""
    text = html.unescape(text).strip()
    if len(text) < _MIN_USABLE:
        return ""                    # paywalled, JS-rendered, or not an article
    return text[:max_chars]


def enrich(events: list[dict], max_chars: int = 6000,
           pause: float = 0.6) -> list[dict]:
    """Attach the source article's text to each selected event.

    Tries each of the event's URLs in turn — a clustered event may have several
    sources, and the second one often reads where the first is paywalled.
    """
    got = 0
    for ev in events:
        urls = [u for u in (ev.get("urls") or []) if u][:3]
        text, used = "", ""
        for u in urls:
            text = fetch_text(u, max_chars=max_chars)
            if text:
                used = u
                break
            time.sleep(pause)
        ev["article_text"] = text
        ev["article_url"] = used
        if text:
            got += 1
        time.sleep(pause)
    print(f"  [article] read the full text of {got}/{len(events)} stories")
    if got < len(events):
        missing = [ev.get("headline", "")[:48] for ev in events
                   if not ev.get("article_text")]
        print(f"    [article] headline-only (paywall or unreadable): {missing}")
    return events

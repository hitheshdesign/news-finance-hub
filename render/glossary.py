"""
render/glossary.py — auto-underline finance jargon and attach a plain-English
definition that shows on hover/tap. Keeps the analysis short while making sure
a beginner never gets stuck on a word.
"""

from __future__ import annotations
import re
import html
from markupsafe import Markup

import config

# Map lowercase term -> (canonical term, definition), longest terms first so
# "current account deficit" wins over "deficit".
_TERMS = sorted(config.GLOSSARY.items(), key=lambda kv: len(kv[0]), reverse=True)
_LOOKUP = {t.lower(): (t, d) for t, d in config.GLOSSARY.items()}

if _TERMS:
    _PATTERN = re.compile(
        r"\b(" + "|".join(re.escape(t) for t, _ in _TERMS) + r")\b",
        re.IGNORECASE,
    )
else:
    _PATTERN = None


def annotate(text: str) -> Markup:
    """Return HTML-safe text with the FIRST mention of each known term wrapped
    in a definition tooltip (later repeats are left plain to avoid clutter)."""
    if not text or _PATTERN is None:
        return Markup(html.escape(text or ""))

    escaped = html.escape(text)
    used: set[str] = set()

    def _repl(m: re.Match) -> str:
        word = m.group(0)
        canonical, definition = _LOOKUP.get(word.lower(), (None, None))
        if canonical is None or canonical.lower() in used:
            return word
        used.add(canonical.lower())
        d = html.escape(definition, quote=True)
        return (
            f'<span class="term" tabindex="0" role="button" '
            f'aria-label="{d}" data-def="{d}">{word}</span>'
        )

    return Markup(_PATTERN.sub(_repl, escaped))

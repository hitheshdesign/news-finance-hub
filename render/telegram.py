"""
render/telegram.py — build a concise message and push it to your Telegram.
Free via the Telegram Bot API. Skips cleanly if not configured.
"""

from __future__ import annotations
import requests

import config


def build_message(brief: dict) -> str:
    lines = [f"🌍→🇮🇳 *India Impact Brief* — {brief['date_human']}",
             f"_{len(brief['events'])} signals · {brief['engine']}_", ""]

    tops = [e for e in brief["events"] if e.get("is_top")]
    for ev in tops:
        a = ev.get("analysis", {})
        lines.append(f"★ *{_clean(ev['headline'])}*")
        # one-line takeaway = top impact
        impacts = a.get("impacts", [])
        if impacts:
            im = impacts[0]
            d = "▲" if im.get("direction") == "up" else "▼"
            lines.append(f"   → {_clean(im.get('target',''))} {d} "
                         f"({im.get('probability','')}, {im.get('horizon','')})")
        lines.append("")

    rest = [e for e in brief["events"] if not e.get("is_top")]
    if rest:
        lines.append("*Also on the radar:*")
        for ev in rest[:5]:
            lines.append(f"• {_clean(ev['headline'])}")
        lines.append("")

    if config.SITE_URL:
        lines.append(f"[Read the full brief]({config.SITE_URL})")

    lines.append("\n_Educational only — not investment advice._")
    return "\n".join(lines)


def _clean(s: str) -> str:
    # Escape the few characters Telegram Markdown treats specially.
    for ch in ["_", "*", "[", "]", "`"]:
        s = s.replace(ch, " ")
    return s.strip()


def send_telegram(brief: dict) -> bool:
    if not config.has_telegram():
        print("  [telegram] not configured, skipping")
        return False

    text = build_message(brief)
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        print("  [telegram] message sent")
        return True
    except Exception as e:
        print(f"  [telegram] failed: {e}")
        return False

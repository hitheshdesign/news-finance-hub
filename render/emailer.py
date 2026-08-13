"""
render/emailer.py — build the email HTML and send it via Gmail SMTP.
Uses a Gmail address + 16-char "App Password" (free). Skips cleanly if not set.
"""

from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from render.web import render_page


def build_email_html(brief: dict) -> str:
    # The web page is already a full, styled, self-contained HTML document —
    # perfect for an HTML email too.
    return render_page(brief)


def send_email(brief: dict) -> bool:
    if not config.has_email():
        print("  [email] not configured, skipping")
        return False

    html = build_email_html(brief)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌍→🇮🇳 India Impact Brief — {brief['date_human']} ({len(brief['events'])} signals)"
    msg["From"] = config.SMTP_USER
    msg["To"] = config.EMAIL_TO

    text_fallback = "Your daily India-impact brief is ready. Open in an HTML-capable client."
    msg.attach(MIMEText(text_fallback, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASS)
            server.sendmail(config.SMTP_USER, [config.EMAIL_TO], msg.as_string())
        print(f"  [email] sent to {config.EMAIL_TO}")
        return True
    except Exception as e:
        print(f"  [email] failed: {e}")
        return False

"""
config.py — loads settings, API keys, and the knowledge-base YAML files.

Design goals:
  * Works with ZERO keys (demo / rule-based mode) so you can see output for free.
  * Keys are read from environment variables (set locally in a .env file, or as
    GitHub Actions "secrets" when it runs in the cloud). Claude never stores them.
"""

from __future__ import annotations
import os
from pathlib import Path
import yaml

# Load a local .env file if present (harmless if it isn't).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_DIR = ROOT / "knowledge"
DATA_DIR = ROOT / "data" / "briefs"
SITE_DIR = ROOT / "site"


def _load_yaml(name: str) -> dict:
    path = KNOWLEDGE_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- Knowledge base + config (read once) ---
TRANSMISSION = _load_yaml("transmission_map.yaml").get("linkages", [])
SOURCES = _load_yaml("sources.yaml")
FILTERS = _load_yaml("filters.yaml")

# --- Secrets / keys (all optional; missing keys just disable that feature) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
FRED_API_KEY = os.getenv("FRED_API_KEY", "").strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Email (Gmail SMTP + App Password recommended)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()          # your gmail address
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()          # 16-char app password
EMAIL_TO = os.getenv("EMAIL_TO", "").strip()            # where to send the brief

# The public URL of your GitHub Pages site (used in Telegram/email links).
SITE_URL = os.getenv("SITE_URL", "").strip()


def has_gemini() -> bool:
    return bool(GEMINI_API_KEY)


def has_telegram() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def has_email() -> bool:
    return bool(SMTP_USER and SMTP_PASS and EMAIL_TO)


def has_fred() -> bool:
    return bool(FRED_API_KEY)

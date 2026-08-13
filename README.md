# 🌍 → 🇮🇳 News Finance Hub

Your personal daily brief that reads what's happening around the world and explains,
**in plain English, how each event could ripple through to Indian markets** — inflation,
the rupee, sectors, specific stocks, gold — with a rough sense of probability and *what to
watch next*.

It runs **for free**, **by itself**, every morning, and delivers to **Email + Telegram + a
web page**.

> **Educational only.** This tool explains how events *tend* to affect markets so you can
> learn the patterns and probabilities and make your *own* decisions. It gives **no buy/sell
> advice**. Probabilities are rough judgments, not guarantees.

---

## What it does each morning

1. **Reads** world news (GDELT), US economic data (FRED), and top business feeds (Reuters, ET, Mint…).
2. **Filters** out the noise — keeps only what can plausibly touch Indian markets.
3. **Explains** each surviving story: *what happened → how it reaches India → what could move (with odds) → what to watch next*, grounded in a hand-built library of real economic linkages.
4. **Delivers** a clean brief to your email, your Telegram, and a web page.
5. **Saves** every brief so you build a searchable history and start seeing patterns over time.

---

## It works in two modes (both free)

| Mode | Needs | What you get |
|---|---|---|
| **Rule-based** (default) | Nothing at all | Real news, matched to the built-in knowledge base. Genuinely useful. |
| **AI mode** | A free Google Gemini key | Richer, tailored explanations written for each specific story. |

You can start with rule-based today and add the Gemini key whenever you like.

---

## See it right now (no setup, no keys)

If you have this folder open, just double-click **`site/index.html`** to see the latest brief
your machine already generated. To make a fresh one from a built-in sample:

```bash
python run.py --sample --dry-run
```

Then open `site/index.html` in your browser.

To make one from **live news** (still free, no keys needed):

```bash
python run.py --dry-run
```

*(`--dry-run` means "build it but don't email/telegram it yet".)*

---

## Turn on the free extras (optional, ~15 min)

Each of these is free and independent — add only the ones you want. Put the values in a file
named `.env` (copy `.env.example` to `.env` and fill it in) for local runs, **and/or** in your
GitHub repo's **Settings → Secrets and variables → Actions** for the automatic cloud run.

### 1. AI analysis — Google Gemini (free)
- Go to <https://aistudio.google.com/apikey>, sign in, click **Create API key**.
- Put it in `GEMINI_API_KEY`.

### 2. US economic data — FRED (free)
- Go to <https://fredaccount.stlouisfed.org/apikeys>, create a free account, request a key.
- Put it in `FRED_API_KEY`. *(This adds the Fed rate / US CPI / jobs numbers to the top of the brief.)*

### 3. Phone push — Telegram (free)
- In Telegram, message **@BotFather**, send `/newbot`, follow the prompts. It gives you a **token** → `TELEGRAM_BOT_TOKEN`.
- Send your new bot any message ("hi"). Then open
  `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser and copy the `"chat":{"id": ...}` number → `TELEGRAM_CHAT_ID`.

### 4. Email digest — Gmail (free)
- Turn on 2-Step Verification on your Google account, then create an **App Password**
  (Google account → Security → App passwords). It's a 16-character code.
- Set `SMTP_USER` = your Gmail address, `SMTP_PASS` = that app password, `EMAIL_TO` = where to send it.

---

## Make it run automatically every morning (free, in the cloud)

You don't need to keep your computer on. **GitHub Actions** will run it daily for free.

1. Create a free account at <https://github.com>.
2. Make a new repository (e.g. `news-finance-hub`) and upload this whole folder to it.
3. In the repo: **Settings → Secrets and variables → Actions** → add the keys from above as **secrets** (same names).
4. **Settings → Pages** → set **Source** to **GitHub Actions** (this publishes your web page).
5. Done. It runs every day at **6:30 AM IST**. You can also trigger it any time from the
   **Actions** tab → *Daily India Impact Brief* → **Run workflow**.

Your web page will be live at `https://<your-username>.github.io/<repo-name>/`.
(Optional: add that URL as a repo **variable** named `SITE_URL` so the Telegram message links to it.)

---

## Make it yours (this is also how you learn)

Everything tunable lives in the **`knowledge/`** folder as plain, commented text files:

- **`transmission_map.yaml`** — the library of "event → India impact" linkages. **Add your own** as
  you learn them; every future news story that matches is then explained automatically. This file
  growing *is* you getting sharper at reading the market.
- **`sources.yaml`** — the news feeds and data series. Add or remove freely.
- **`filters.yaml`** — the "ground rules". Make the brief stricter (fewer, higher-signal items) or
  looser by changing a couple of numbers. No coding needed.

---

## How the code is organised

```
run.py            The daily pipeline (ties everything together)
config.py         Loads settings + keys
ingest/           Pulls raw news/data   (rss, gdelt, fred)
screen/           The "ground rules"    (relevance, cluster)
analyze/          The brain             (engine = rule-based OR Gemini + knowledge base)
render/           Output                (web page, email, telegram)
knowledge/        Your editable brain   (transmission_map, sources, filters)
data/briefs/      Saved briefs (JSON + Markdown) — your history
site/             The generated web page
.github/workflows/daily.yml   The free daily scheduler
```

---

## Command cheat-sheet

```bash
python run.py                 # full run (build + deliver)
python run.py --dry-run       # build but DON'T send email/telegram
python run.py --sample        # use built-in offline sample news
python run.py --max 6         # limit the brief to 6 stories
```

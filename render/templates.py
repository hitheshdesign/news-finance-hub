"""
render/templates.py — Jinja2 templates (kept as strings so the project stays
self-contained). One shared card macro powers both the web page and the email.
"""

# Shared CSS — theme-aware (respects the reader's light/dark preference).
CSS = """
:root{
  --bg:#f6f7f9; --panel:#ffffff; --ink:#12151a; --muted:#5b6472;
  --line:#e6e8ec; --accent:#1a56db; --up:#0b8a3d; --down:#c0281c;
  --chip:#eef2ff; --chipink:#1a56db; --topbg:#fff8e6; --topline:#f2d98a;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0e1116; --panel:#161b22; --ink:#e6edf3; --muted:#9aa4b2;
    --line:#232a33; --accent:#58a6ff; --up:#3fb950; --down:#f85149;
    --chip:#1b2537; --chipink:#79b8ff; --topbg:#20211a; --topline:#5a5320;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:820px;margin:0 auto;padding:24px 18px 64px;}
header.top{padding:8px 0 20px;border-bottom:1px solid var(--line);margin-bottom:24px;}
h1{font-size:24px;margin:0 0 4px;letter-spacing:-.3px;}
.sub{color:var(--muted);font-size:14px;}
.macro{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.macro .m{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:8px 11px;font-size:13px;color:var(--muted);}
.macro .m b{color:var(--ink);}
.arrow-up{color:var(--up);font-weight:600;}
.arrow-down{color:var(--down);font-weight:600;}
.sectionlabel{font-size:12px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin:26px 0 12px;font-weight:600;}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:18px 18px 14px;margin:0 0 16px;box-shadow:0 1px 2px rgba(0,0,0,.03);}
.card.top{background:var(--topbg);border-color:var(--topline);}
.card h2{font-size:18px;margin:0 0 8px;line-height:1.35;}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;}
.chip{background:var(--chip);color:var(--chipink);border-radius:999px;
  padding:3px 10px;font-size:12px;font-weight:600;}
.chip.gray{background:transparent;color:var(--muted);border:1px solid var(--line);}
.what{margin:0 0 12px;color:var(--ink);}
.chain{margin:0 0 12px;padding:0;list-style:none;}
.chain li{position:relative;padding:2px 0 2px 22px;color:var(--ink);font-size:15px;}
.chain li:before{content:"↓";position:absolute;left:6px;color:var(--muted);}
.chain li:first-child:before{content:"•";}
table.impacts{width:100%;border-collapse:collapse;margin:6px 0 12px;font-size:14px;}
table.impacts th,table.impacts td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top;}
table.impacts th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em;}
.prob-High{color:var(--down);font-weight:700;}
.prob-Medium{color:#b8860b;font-weight:600;}
.prob-Low{color:var(--muted);font-weight:600;}
.watch{margin:8px 0 4px;padding-left:18px;}
.watch li{color:var(--ink);font-size:14px;margin:2px 0;}
.meta{color:var(--muted);font-size:12px;margin-top:10px;display:flex;flex-wrap:wrap;gap:10px;}
.meta a{color:var(--accent);text-decoration:none;}
.caveat{color:var(--muted);font-size:13px;font-style:italic;margin-top:8px;}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--muted);font-size:13px;}
.archive a{color:var(--accent);text-decoration:none;margin-right:12px;}
.disclaimer{background:var(--panel);border:1px dashed var(--line);border-radius:10px;
  padding:12px 14px;color:var(--muted);font-size:13px;margin-top:22px;}
"""

# One event card (used by web + email). Expects `ev` with `ev.analysis`.
CARD = """
<div class="card {{ 'top' if ev.is_top else '' }}">
  <div class="chips">
    {% if ev.is_top %}<span class="chip">★ Top signal</span>{% endif %}
    <span class="chip gray">{{ ev.category|replace('_',' ')|title }}</span>
    {% if ev.analysis.matched_linkage %}<span class="chip gray">pattern: {{ ev.analysis.matched_linkage }}</span>{% endif %}
    <span class="chip gray">{{ ev.item_count }} source{{ 's' if ev.item_count>1 else '' }}</span>
  </div>
  <h2>{{ ev.headline }}</h2>
  {% if ev.analysis.what_happened and ev.analysis.what_happened != ev.headline %}
    <p class="what">{{ ev.analysis.what_happened }}</p>
  {% endif %}

  {% if ev.analysis.why_it_matters_india %}
    <div class="sectionlabel" style="margin:10px 0 6px">How it reaches India</div>
    <ul class="chain">
      {% for step in ev.analysis.why_it_matters_india %}<li>{{ step }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if ev.analysis.impacts %}
    <table class="impacts">
      <tr><th>What could move</th><th>Dir.</th><th>Odds</th><th>When</th><th>Why</th></tr>
      {% for im in ev.analysis.impacts %}
      <tr>
        <td>{{ im.target }}</td>
        <td class="{{ 'arrow-up' if im.direction=='up' else 'arrow-down' }}">{{ '▲' if im.direction=='up' else '▼' }}</td>
        <td class="prob-{{ im.probability }}">{{ im.probability }}</td>
        <td>{{ im.horizon }}</td>
        <td>{{ im.rationale }}</td>
      </tr>
      {% endfor %}
    </table>
  {% endif %}

  {% if ev.analysis.watch_next %}
    <div class="sectionlabel" style="margin:8px 0 4px">Watch next</div>
    <ul class="watch">
      {% for w in ev.analysis.watch_next %}<li>{{ w }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if ev.analysis.caveats %}<div class="caveat">Caveat: {{ ev.analysis.caveats }}</div>{% endif %}

  <div class="meta">
    <span>Confidence: {{ ev.analysis.confidence }}</span>
    <span>Sources: {{ ev.sources|join(', ') }}</span>
    {% if ev.urls %}<a href="{{ ev.urls[0] }}" target="_blank" rel="noopener">Read the news →</a>{% endif %}
  </div>
</div>
"""

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ brief.title }}</title>
<style>{{ css }}</style>
</head><body><div class="wrap">
<header class="top">
  <h1>🌍→🇮🇳 News → India Impact</h1>
  <div class="sub">{{ brief.date_human }} · {{ brief.events|length }} signals ·
    analysis: {{ brief.engine }}</div>
  {% if brief.macro %}
  <div class="macro">
    {% for m in brief.macro %}
    <div class="m"><b>{{ m.label }}:</b> {{ m.value }}
      {% if m.direction=='up' %}<span class="arrow-up">▲</span>
      {% elif m.direction=='down' %}<span class="arrow-down">▼</span>{% endif %}</div>
    {% endfor %}
  </div>
  {% endif %}
</header>

{% set tops = brief.events|selectattr('is_top')|list %}
{% set rest = brief.events|rejectattr('is_top')|list %}

{% if tops %}<div class="sectionlabel">Today — what matters most</div>{% endif %}
{% for ev in tops %}{{ card(ev) }}{% endfor %}

{% if rest %}<div class="sectionlabel">Also on the radar</div>{% endif %}
{% for ev in rest %}{{ card(ev) }}{% endfor %}

<div class="disclaimer">
  <b>Educational only.</b> This brief explains how events <i>tend</i> to affect markets so
  you can learn the patterns and probabilities. It is not investment advice and gives no
  buy/sell recommendations. Probabilities are rough judgments, not guarantees.
</div>

<footer>
  {% if brief.archive %}
  <div class="archive"><b>Past briefs:</b>
    {% for a in brief.archive %}<a href="{{ a.href }}">{{ a.label }}</a>{% endfor %}
  </div>{% endif %}
  <p>Generated automatically by your News Finance Hub · {{ brief.generated_at }}</p>
</footer>
</div></body></html>
"""

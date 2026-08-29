"""
render/templates.py — editorial, beginner-friendly templates (Jinja2 strings so
the project stays self-contained). One shared card macro powers web + email.

Design language (from the ui-ux-pro-max design system):
  * Editorial: Newsreader serif headlines + Inter sans body, generous whitespace.
  * Calm slate palette; green/red used ONLY for direction, never decoration.
  * Every card leads with a plain-English takeaway; jargon is tap-to-define.
"""

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&"
    "family=Inter:wght@400;500;600;700&display=swap"
)

CSS = """
:root{
  --font-serif:'Newsreader',Georgia,'Times New Roman',serif;
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --bg:#f7f6f3; --panel:#ffffff; --panel2:#faf9f7;
  --ink:#141a24; --ink2:#3b4453; --muted:#6b7482; --faint:#98a1af;
  --line:#e7e4de; --line2:#efece6;
  --brand:#0f172a; --link:#1f5fd6;
  --up:#15803d; --up-bg:#e9f6ee; --down:#c02626; --down-bg:#fbebe9;
  --tip-bg:#1c2430; --tip-ink:#f2f5f9;
  --top-bg:#fbf7ec; --top-line:#ecdcae;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0b0e14; --panel:#141a22; --panel2:#111721;
    --ink:#e8edf3; --ink2:#c3ccd8; --muted:#93a0af; --faint:#6b7788;
    --line:#232c38; --line2:#1c2430;
    --brand:#e8edf3; --link:#6ea8fe;
    --up:#42c17d; --up-bg:#12271c; --down:#f2726f; --down-bg:#2a1514;
    --tip-bg:#e9edf2; --tip-ink:#10151d;
    --top-bg:#1c1a12; --top-line:#4a4022;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;overflow-x:hidden;}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:var(--font-sans);font-size:17px;line-height:1.62;
  -webkit-font-smoothing:antialiased;overflow-x:hidden;}
.wrap{max-width:720px;margin:0 auto;padding:28px 20px 72px;}

/* ---------- Masthead ---------- */
.mast{padding-bottom:20px;border-bottom:2px solid var(--ink);margin-bottom:8px;}
.kicker{font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin-bottom:8px;}
.mast h1{font-family:var(--font-serif);font-weight:700;letter-spacing:-.02em;
  font-size:clamp(30px,7vw,44px);line-height:1.05;margin:0 0 10px;color:var(--ink);}
.mast .date{font-size:15px;color:var(--ink2);}
.mast .date b{color:var(--ink);}
.mast .engine{color:var(--muted);}

/* ---------- Tabs (News · Global Finance · Learn) ---------- */
.tabs{display:flex;gap:4px;margin:16px 0 4px;border-bottom:1px solid var(--line);}
.tabs a{padding:9px 14px;font-size:14px;font-weight:600;color:var(--muted);
  text-decoration:none;border-bottom:2px solid transparent;margin-bottom:-1px;
  border-radius:8px 8px 0 0;}
.tabs a:hover{color:var(--ink2);background:var(--panel2);}
.tabs a.on{color:var(--ink);border-bottom-color:var(--link);}

/* ---------- Reading guide (used on the Learn / Global pages) ---------- */
.guide{margin:18px 0 4px;padding:12px 15px;background:var(--panel2);
  border:1px solid var(--line);border-radius:12px;font-size:13.5px;color:var(--ink2);}
.guide b{color:var(--ink);}
.guide .flow{color:var(--muted);}

/* ---------- Macro strip ---------- */
.macro{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.macro .m{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:7px 11px;font-size:12.5px;color:var(--muted);}
.macro .m b{color:var(--ink);font-weight:600;}

/* ---------- Forward calendar ("what to watch") — collapsible accordion ---------- */
.cal{margin-top:16px;border:1px solid var(--line);border-radius:12px;
  background:var(--panel);overflow:hidden;}
.cal>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:11px;
  font-family:var(--font-sans);font-size:12.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.1em;color:var(--muted);
  padding:15px 18px;border-radius:12px;}
/* Hide the browser's own ▶ marker (both engines) so only our chevron shows. */
.cal>summary::-webkit-details-marker{display:none;}
.cal>summary::marker{content:"";font-size:0;}
.cal>summary:hover{color:var(--ink2);background:var(--panel2);}
.cal>summary .chev{margin-left:auto;transition:transform .18s ease;color:var(--faint);
  font-size:10px;font-weight:700;}
.cal[open]>summary .chev{transform:rotate(180deg);}
.cal[open]>summary{border-bottom:1px solid var(--line2);border-radius:12px 12px 0 0;}
.cal .calmonth{font-size:11px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
  color:var(--faint);padding:11px 18px 5px;background:var(--panel2);
  border-bottom:1px solid var(--line2);}
.cal .alert{font-size:11px;font-weight:700;letter-spacing:.02em;text-transform:none;
  color:#8a4b00;background:#ffe6b8;padding:2px 9px;border-radius:999px;}
@media (prefers-color-scheme:dark){.cal .alert{color:#ffcf8a;background:#3a2a10;}}
.cal ul{list-style:none;margin:0;padding:0;}
.cal li{display:flex;gap:14px;align-items:baseline;padding:13px 18px;
  border-bottom:1px solid var(--line2);}
.cal li:last-child{border-bottom:none;}
.cal li.soon{background:var(--panel2);}
.cal .when{flex:0 0 88px;font-weight:600;color:var(--ink);font-size:13.5px;}
.cal .when .in{display:block;font-weight:400;color:var(--faint);font-size:11.5px;}
.cal .ev{flex:1;}
.cal .ev b{color:var(--ink);font-weight:600;font-size:14.5px;}
.cal .ev p{margin:2px 0 0;color:var(--muted);font-size:13px;line-height:1.45;}

/* ---------- Section labels ---------- */
.section{font-family:var(--font-sans);font-size:12.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.1em;color:var(--muted);
  margin:34px 0 14px;display:flex;align-items:center;gap:10px;}
.section::after{content:"";flex:1;height:1px;background:var(--line);}

/* ---------- Card ---------- */
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:22px 22px 18px;margin:0 0 18px;}
.card.top{background:linear-gradient(180deg,var(--top-bg),var(--panel));
  border-color:var(--top-line);}
.tags{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px;}
.tag{font-size:11.5px;font-weight:600;letter-spacing:.03em;color:var(--muted);
  text-transform:uppercase;}
.tag.dot::before{content:"•";margin-right:8px;color:var(--faint);}
.badge{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;
  letter-spacing:.04em;text-transform:uppercase;color:#7a5b00;background:#f6e7bd;
  padding:3px 9px;border-radius:999px;}
@media (prefers-color-scheme:dark){.badge{color:#ffdf8a;background:#3a3216;}}
.badge.dev{color:#2f52b8;background:#e6ecfb;}
@media (prefers-color-scheme:dark){.badge.dev{color:#a9c2ff;background:#1c2740;}}
.card h2{font-family:var(--font-serif);font-weight:600;letter-spacing:-.01em;
  font-size:24px;line-height:1.22;margin:0 0 14px;color:var(--ink);}

/* Plain-English takeaway — the rookie's anchor. Label sits ABOVE the sentence
   so the sentence gets the full width and reads as one clean line of meaning. */
.tldr{background:var(--panel2);border-left:3px solid var(--link);
  border-radius:0 10px 10px 0;padding:13px 16px;margin:0 0 16px;}
.tldr .lbl{display:block;font-size:11px;font-weight:700;letter-spacing:.09em;
  text-transform:uppercase;color:var(--link);margin:0 0 6px;}
.tldr p{margin:0;font-size:17px;font-weight:500;color:var(--ink);line-height:1.5;}

.blocklabel{font-size:12px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--muted);margin:18px 0 9px;}
.what{margin:0 0 4px;color:var(--ink2);font-size:16px;}

/* "Think of it like…" — an everyday analogy that makes the mechanism click */
.analogy{margin:14px 0 4px;padding:11px 14px;background:var(--panel2);
  border:1px dashed var(--line);border-radius:11px;font-size:15px;color:var(--ink2);
  line-height:1.55;}
.analogy b{color:var(--ink);font-weight:600;}

/* How it reaches India — connected chain */
.chain{list-style:none;margin:0;padding:0;}
.chain li{position:relative;padding:0 0 14px 26px;color:var(--ink2);font-size:15.5px;}
.chain li::before{content:"";position:absolute;left:7px;top:8px;width:8px;height:8px;
  border-radius:50%;background:var(--link);}
.chain li::after{content:"";position:absolute;left:10.5px;top:16px;bottom:0;
  width:1px;background:var(--line);}
.chain li:last-child{padding-bottom:0;}
.chain li:last-child::after{display:none;}

/* What could move — impact rows */
.impacts{display:flex;flex-direction:column;gap:9px;margin-top:4px;}
.impact{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:baseline;
  padding:11px 13px;background:var(--panel2);border:1px solid var(--line2);border-radius:11px;}
.dir{font-size:12.5px;font-weight:700;padding:3px 9px;border-radius:7px;white-space:nowrap;}
.dir.up{color:var(--up);background:var(--up-bg);}
.dir.down{color:var(--down);background:var(--down-bg);}
.impact-body{flex:1 1 220px;min-width:180px;}
.impact-target{font-weight:600;color:var(--ink);font-size:15.5px;}
.impact-why{color:var(--muted);font-size:13.5px;margin-top:1px;}
.impact-side{display:flex;align-items:center;gap:12px;margin-left:auto;}
.meter{display:inline-flex;align-items:center;gap:8px;}
.dots{display:inline-flex;gap:3px;}
.dots i{width:7px;height:7px;border-radius:50%;background:var(--line);display:block;}
.dots i.on{background:var(--ink2);}
.meter .lvl{font-size:12px;color:var(--muted);font-weight:600;}
.when{font-size:12.5px;color:var(--faint);white-space:nowrap;}

/* Pattern Library: the trigger keywords that fire a linkage */
.triggers{font-size:12.5px;color:var(--muted);margin:0 0 10px;
  display:flex;flex-wrap:wrap;gap:6px;align-items:baseline;}
.triggers .lead{margin-right:2px;}
.trig{background:var(--panel2);border:1px solid var(--line2);border-radius:6px;
  padding:2px 8px;color:var(--ink2);font-size:12px;}

/* Watch next */
.watch{list-style:none;margin:6px 0 0;padding:0;}
.watch li{position:relative;padding:4px 0 4px 24px;color:var(--ink2);font-size:15px;}
.watch li::before{content:"→";position:absolute;left:2px;color:var(--link);font-weight:700;}

/* Footer bits */
.foot{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;
  margin-top:16px;padding-top:13px;border-top:1px solid var(--line2);
  font-size:12.5px;color:var(--muted);}
.foot .conf{display:inline-flex;align-items:center;gap:7px;}
.foot a{color:var(--link);text-decoration:none;font-weight:600;}
.foot a:hover{text-decoration:underline;}
.caveat{color:var(--muted);font-size:13px;font-style:italic;margin-top:11px;
  padding-left:11px;border-left:2px solid var(--line);}

/* Jargon tooltips */
.term{border-bottom:1.5px dotted var(--faint);cursor:help;position:relative;
  color:inherit;outline:none;}
.term:hover,.term:focus{border-bottom-color:var(--link);}
.term::after{content:attr(data-def);position:absolute;left:0;top:calc(100% + 8px);
  width:min(300px,78vw);background:var(--tip-bg);color:var(--tip-ink);
  font-family:var(--font-sans);font-size:13px;font-weight:400;font-style:normal;
  line-height:1.45;padding:10px 12px;border-radius:9px;
  box-shadow:0 8px 24px rgba(0,0,0,.22);z-index:20;
  opacity:0;visibility:hidden;transform:translateY(-3px);
  transition:opacity .15s ease,transform .15s ease;pointer-events:none;}
.term:hover::after,.term:focus::after{opacity:1;visibility:visible;transform:translateY(0);}

/* Deeper reads — original explainer links (Finshots / The Ken) */
.deeper{display:flex;flex-direction:column;gap:8px;margin-bottom:8px;}
.deeper .dr{display:flex;flex-wrap:wrap;gap:6px 11px;align-items:baseline;
  padding:12px 14px;background:var(--panel);border:1px solid var(--line);
  border-radius:11px;text-decoration:none;}
.deeper .dr:hover{border-color:var(--link);}
.deeper .src{font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:.04em;color:var(--link);white-space:nowrap;}
.deeper .t{color:var(--ink2);font-size:15px;}
.deeper .dr:hover .t{color:var(--ink);}

/* ============ GLOBAL FINANCE ============ */
:root{
  --c-cheap:#2f9e5f; --c-fair:#d99a2b; --c-exp:#d1483f; --c-none:#dcd8d1;
  --cb-cheap:#e9f6ee; --cb-fair:#faf1db; --cb-exp:#fbebe9;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --c-cheap:#3fbe79; --c-fair:#e0a94a; --c-exp:#ef5f5b; --c-none:#28303c;
    --cb-cheap:#12271c; --cb-fair:#33280f; --cb-exp:#2a1514;
  }
}
.v-cheap{--vc:var(--c-cheap);--vb:var(--cb-cheap);}
.v-fair{--vc:var(--c-fair);--vb:var(--cb-fair);}
.v-exp{--vc:var(--c-exp);--vb:var(--cb-exp);}

/* View switch (Valuation | Market Movers) */
.gf-switch{display:inline-flex;gap:3px;background:var(--panel2);border:1px solid var(--line);
  border-radius:11px;padding:4px;margin:18px 0 6px;}
.gf-switch button{font-family:var(--font-sans);font-size:13.5px;font-weight:600;
  color:var(--muted);background:transparent;border:0;border-radius:8px;
  padding:9px 16px;cursor:pointer;}
.gf-switch button:hover{color:var(--ink2);}
.gf-switch button.on{color:var(--ink);background:var(--panel);
  box-shadow:0 1px 3px rgba(0,0,0,.12);}
.gf-view[hidden]{display:none;}

.gf-note{background:var(--panel2);border:1px dashed var(--line);border-radius:12px;
  padding:12px 15px;color:var(--muted);font-size:13px;margin:14px 0 12px;}
.gf-note b{color:var(--ink2);}
.gf-legend{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px;align-items:center;}
.gf-legend .lg{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;
  color:var(--ink2);background:var(--panel);border:1px solid var(--line);
  border-radius:999px;padding:5px 12px;}
.gf-legend .sw{width:11px;height:11px;border-radius:3px;background:var(--vc);}
.gf-legend .hintx{color:var(--faint);font-size:12.5px;}

/* ---- Choropleth world map ---- */
.map-wrap{position:relative;background:var(--panel);border:1px solid var(--line);
  border-radius:14px;overflow:hidden;}
.map-wrap svg{display:block;width:100%;height:auto;cursor:grab;touch-action:none;
  background:var(--panel2);}
.map-wrap svg.drag{cursor:grabbing;}
.cty{fill:var(--c-none);stroke:var(--panel);stroke-width:.4;
  transition:fill .15s ease,opacity .15s ease;}
.cty.cheap{fill:var(--c-cheap);}
.cty.fair{fill:var(--c-fair);}
.cty.expensive{fill:var(--c-exp);}
.cty.has{cursor:pointer;}
.cty.has:hover{opacity:.78;}
.cty.sel{stroke:var(--ink);stroke-width:1.4;}
.dot{pointer-events:none;}
.dot circle{stroke:var(--panel);stroke-width:1.2;}
.mapctl{position:absolute;top:10px;right:10px;display:flex;flex-direction:column;gap:5px;}
.mapctl button{width:32px;height:32px;font-size:15px;font-weight:700;line-height:1;
  color:var(--ink2);background:var(--panel);border:1px solid var(--line);
  border-radius:8px;cursor:pointer;}
.mapctl button:hover{color:var(--ink);border-color:var(--link);}
.maptip{position:absolute;pointer-events:none;z-index:30;background:var(--tip-bg);
  color:var(--tip-ink);font-size:12.5px;line-height:1.4;padding:7px 10px;
  border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.25);opacity:0;
  transition:opacity .12s ease;white-space:nowrap;}
.maptip.on{opacity:1;}
.maptip b{display:block;font-size:13.5px;}

/* ---- Two-column: table + sticky detail ---- */
.gf-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,400px);
  gap:16px;margin-top:16px;align-items:start;}
.gf-panelwrap{position:sticky;top:14px;}
@media (max-width:900px){
  .gf-grid{grid-template-columns:1fr;}
  .gf-panelwrap{position:static;order:-1;}
}

/* Country table */
.ctable{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  overflow:hidden;}
.ctable .thead{display:flex;font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:.06em;color:var(--muted);border-bottom:1px solid var(--line2);
  background:var(--panel2);}
.ctable .thead span{padding:11px 10px;cursor:pointer;user-select:none;}
.ctable .thead span:hover{color:var(--ink2);}
.ctable .thead span.sorted{color:var(--ink);}
.ctable .row{display:flex;align-items:center;border-bottom:1px solid var(--line2);
  cursor:pointer;font-size:13.5px;}
.ctable .row:last-child{border-bottom:none;}
.ctable .row:hover{background:var(--panel2);}
.ctable .row.sel{background:var(--panel2);box-shadow:inset 3px 0 0 var(--vc);}
.ctable .row>span{padding:11px 10px;}
.c-name{flex:1 1 auto;min-width:0;display:flex;align-items:center;gap:9px;
  color:var(--ink);font-weight:600;}
.c-name .sw{width:9px;height:9px;border-radius:3px;background:var(--vc);flex:none;}
.c-name i{font-style:normal;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.c-val{flex:0 0 96px;color:var(--vc);font-weight:600;font-size:12px;
  text-transform:uppercase;letter-spacing:.03em;}
.c-cape{flex:0 0 74px;color:var(--ink2);text-align:right;}
.c-er{flex:0 0 78px;text-align:right;font-weight:600;}
@media (max-width:520px){.c-val{display:none;}}

/* Detail panel */
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:18px;max-height:calc(100vh - 28px);overflow-y:auto;}
.panel .hint{color:var(--muted);font-size:14px;margin:0;}
.panel h3{font-family:var(--font-serif);font-size:23px;font-weight:600;margin:0 0 2px;
  color:var(--ink);line-height:1.2;}
.panel .sub{color:var(--muted);font-size:13px;margin-bottom:12px;}
.gf-vpill{display:inline-block;font-family:var(--font-sans);font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.05em;color:var(--vc);background:var(--vb);
  padding:3px 10px;border-radius:999px;vertical-align:middle;margin-left:8px;}
.verdict{background:var(--panel2);border-left:3px solid var(--vc);border-radius:0 10px 10px 0;
  padding:12px 14px;margin:0 0 14px;color:var(--ink);font-size:15px;line-height:1.5;}
.verdict b{color:var(--vc);display:block;font-size:11px;text-transform:uppercase;
  letter-spacing:.07em;margin-bottom:4px;}
.pblock{margin:0 0 14px;}
.pblock h4{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin:0 0 7px;padding-bottom:5px;border-bottom:1px solid var(--line2);}
.kv{display:flex;flex-wrap:wrap;gap:6px;}
.kv .k{flex:1 1 88px;background:var(--panel2);border:1px solid var(--line2);
  border-radius:9px;padding:8px 10px;font-size:11px;color:var(--muted);}
.kv .k b{display:block;color:var(--ink);font-size:15px;font-weight:600;margin-top:1px;}
.kv .k b.sm{font-size:12.5px;font-weight:500;line-height:1.45;}
.kv .k.wide{flex:1 1 100%;}
.maptip .wrapline{display:block;max-width:280px;white-space:normal;margin-top:3px;
  font-weight:400;}
/* Expected-return bar */
.erbar{display:flex;flex-direction:column;gap:7px;}
.erow{display:flex;align-items:center;gap:9px;font-size:13px;}
.erow .lbl{flex:0 0 108px;color:var(--ink2);}
.erow .track{flex:1;height:8px;background:var(--line2);border-radius:99px;position:relative;
  overflow:hidden;}
.erow .fill{position:absolute;top:0;bottom:0;border-radius:99px;}
.erow .fill.pos{background:var(--c-cheap);}
.erow .fill.neg{background:var(--c-exp);}
.erow .num{flex:0 0 52px;text-align:right;font-weight:600;color:var(--ink);}
.erow.total{border-top:1px solid var(--line2);padding-top:7px;margin-top:2px;}
.erow.total .lbl,.erow.total .num{font-weight:700;}
.plist{list-style:none;margin:0;padding:0;}
.plist li{position:relative;padding:3px 0 3px 16px;color:var(--ink2);font-size:13.5px;
  line-height:1.5;}
.plist li::before{content:"";position:absolute;left:2px;top:11px;width:5px;height:5px;
  border-radius:50%;background:var(--faint);}
.plist.good li::before{background:var(--c-cheap);}
.plist.bad li::before{background:var(--c-exp);}
.pnote{color:var(--ink2);font-size:13.5px;line-height:1.55;margin:0;}
.pnote em{color:var(--muted);font-style:normal;}
.gf-india{padding:11px 13px;background:var(--panel2);border-left:3px solid var(--link);
  border-radius:0 10px 10px 0;font-size:13.5px;color:var(--ink2);line-height:1.5;}
.gf-india b{color:var(--link);}
.gf-news a{display:block;color:var(--link);text-decoration:none;font-size:13.5px;
  padding:4px 0;line-height:1.45;}
.gf-news a:hover{text-decoration:underline;}

/* ---- Market movers: heat-map ---- */
.rot-now{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px;margin-bottom:14px;}
.rot-now .mood{font-size:12px;font-weight:700;text-transform:uppercase;
  letter-spacing:.06em;color:var(--link);}
.rot-now p{margin:6px 0 0;color:var(--ink2);font-size:15.5px;line-height:1.5;}
.heatwrap{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:14px;overflow-x:auto;}
.heat{border-collapse:separate;border-spacing:3px;width:100%;min-width:640px;}
.heat th{font-size:11px;font-weight:700;color:var(--muted);text-align:left;padding:4px 6px;
  white-space:nowrap;}
.heat th.per{writing-mode:horizontal-tb;text-align:center;font-size:11px;}
.heat td{height:30px;border-radius:6px;cursor:pointer;position:relative;
  transition:transform .1s ease;}
.heat td:hover{transform:scale(1.13);z-index:5;}
.heat .rowlbl{font-size:12.5px;font-weight:600;color:var(--ink2);white-space:nowrap;
  padding-right:8px;width:1%;}
.heat .rowlbl.gold{color:var(--c-fair);}
.s2{background:var(--c-cheap);}
.s1{background:var(--c-cheap);opacity:.5;}
.s0{background:var(--line2);}
.sm1{background:var(--c-exp);opacity:.5;}
.sm2{background:var(--c-exp);}
.heatlegend{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-top:12px;
  font-size:12px;color:var(--muted);}
.heatlegend .sc{display:inline-flex;align-items:center;gap:6px;}
.heatlegend .box{width:15px;height:15px;border-radius:4px;display:inline-block;}

/* Money rotation narrative timeline */
.rot{position:relative;list-style:none;margin:0;padding:0;}
.rot li{position:relative;padding:0 0 16px 26px;}
.rot li::before{content:"";position:absolute;left:6px;top:6px;width:9px;height:9px;
  border-radius:50%;background:var(--link);}
.rot li::after{content:"";position:absolute;left:10px;top:15px;bottom:0;width:1px;
  background:var(--line);}
.rot li:last-child::after{display:none;}
.rot li.hl::before{background:var(--c-fair);box-shadow:0 0 0 4px var(--cb-fair);}
.rot .per{font-weight:700;color:var(--ink);font-size:15px;}
.rot .mood-tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.03em;
  padding:2px 8px;border-radius:999px;margin-left:8px;}
.rot .mood-on{color:var(--up);background:var(--up-bg);}
.rot .mood-off{color:var(--down);background:var(--down-bg);}
.rot .mood-mixed{color:var(--muted);background:var(--panel2);}
.rot .flows{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0;}
.rot .into,.rot .outof{font-size:12.5px;padding:3px 9px;border-radius:7px;}
.rot .into{color:var(--up);background:var(--up-bg);}
.rot .outof{color:var(--down);background:var(--down-bg);}
.rot .into.gold{color:var(--c-fair);background:var(--cb-fair);font-weight:600;}
.rot .rwhy{color:var(--muted);font-size:13.5px;line-height:1.5;margin-top:2px;}

/* Disclaimer + footer */
.disclaimer{background:var(--panel2);border:1px dashed var(--line);border-radius:12px;
  padding:14px 16px;color:var(--muted);font-size:13px;margin-top:28px;}
.disclaimer b{color:var(--ink2);}
.pagefoot{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--muted);font-size:13px;}
.archive{margin-bottom:12px;}
.archive b{color:var(--ink2);}
.archive a{color:var(--link);text-decoration:none;margin:0 10px 6px 0;
  display:inline-block;}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media (max-width:520px){
  body{font-size:16px}
  .card{padding:18px 16px 15px;border-radius:14px}
  .impact-side{margin-left:0}
}
"""

# One event card (used by web + email). `gloss` and `dots` are Jinja filters.
CARD = """
<article class="card {{ 'top' if ev.is_top else '' }}">
  <div class="tags">
    {% if ev.is_top %}<span class="badge">★ Top signal</span>{% endif %}
    {% if ev.developing %}<span class="badge dev">↻ Developing</span>{% endif %}
    <span class="tag">{{ ev.category|replace('_',' ')|title }}</span>
    <span class="tag dot">{{ ev.item_count }} source{{ 's' if ev.item_count>1 else '' }}</span>
  </div>

  <h2>{{ ev.headline }}</h2>

  {% if ev.analysis.tldr %}
  <div class="tldr">
    <span class="lbl">In plain English</span>
    <p>{{ ev.analysis.tldr|gloss }}</p>
  </div>
  {% endif %}

  {% if ev.analysis.what_happened and ev.analysis.what_happened != ev.headline %}
    <p class="what">{{ ev.analysis.what_happened|gloss }}</p>
  {% endif %}

  {% if ev.analysis.analogy %}
    <div class="analogy"><b>Think of it like…</b> {{ ev.analysis.analogy|gloss }}</div>
  {% endif %}

  {% if ev.analysis.why_it_matters_india %}
    <div class="blocklabel">How this reaches India</div>
    <ul class="chain">
      {% for step in ev.analysis.why_it_matters_india %}<li>{{ step|gloss }}</li>{% endfor %}
    </ul>
  {% endif %}

  {% if ev.analysis.impacts %}
    <div class="blocklabel">What could move — and how likely</div>
    <div class="impacts">
      {% for im in ev.analysis.impacts %}
      <div class="impact">
        <span class="dir {{ 'up' if im.direction=='up' else 'down' }}">
          {{ '▲ Rises' if im.direction=='up' else '▼ Falls' }}</span>
        <div class="impact-body">
          <div class="impact-target">{{ im.target }}</div>
          {% if im.rationale %}<div class="impact-why">{{ im.rationale|gloss }}</div>{% endif %}
        </div>
        <div class="impact-side">
          <span class="meter">{{ im.probability|dots }}<span class="lvl">{{ im.probability }}</span></span>
          <span class="when">{{ im.horizon }}</span>
        </div>
      </div>
      {% endfor %}
    </div>
  {% endif %}

  {% if ev.analysis.watch_next %}
    <div class="blocklabel">What to watch next</div>
    <ul class="watch">
      {% for w in ev.analysis.watch_next %}<li>{{ w|gloss }}</li>{% endfor %}
    </ul>
  {% endif %}

  <div class="foot">
    <span class="conf">Confidence {{ ev.analysis.confidence|dots }}<b>{{ ev.analysis.confidence }}</b></span>
    <span>{{ ev.sources|join(', ') }}</span>
    {% if ev.urls %}<a href="{{ ev.urls[0] }}" target="_blank" rel="noopener">Read the source →</a>{% endif %}
  </div>
  {% if ev.analysis.caveats %}<div class="caveat">Where this could be wrong: {{ ev.analysis.caveats|gloss }}</div>{% endif %}
</article>
"""

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ brief.title }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
<style>{{ css }}</style>
</head><body><div class="wrap">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <h1>The India Impact Brief</h1>
  <div class="date"><b>{{ brief.date_human }}</b> · {{ brief.events|length }} signals ·
    <span class="engine">analysis by {{ brief.engine }}</span></div>
</header>

{{ nav }}

{% if brief.macro %}
<div class="macro">
  {% for m in brief.macro %}
  <div class="m"><b>{{ m.label }}:</b> {{ m.value }}
    {% if m.direction=='up' %}▲{% elif m.direction=='down' %}▼{% endif %}</div>
  {% endfor %}
</div>
{% endif %}

{% if brief.calendar %}
<details class="cal">
  <summary>Mark your calendar — what to watch
    {% if brief.calendar_alert %}<span class="alert">🔔 {{ brief.calendar_alert }} within {{ brief.calendar_alert_days }} days</span>{% endif %}
    <span class="chev">▼</span>
  </summary>
  <ul>
    {% set ns = namespace(month='') %}
    {% for c in brief.calendar %}
      {% if c.month_label != ns.month %}
        {% set ns.month = c.month_label %}
        <li class="calmonth" style="display:block">{{ c.month_label }}</li>
      {% endif %}
    <li class="{{ 'soon' if c.days_away <= brief.calendar_alert_days else '' }}">
      <span class="when">{{ c.date_human }}
        <span class="in">{% if c.days_away==0 %}today{% elif c.days_away==1 %}tomorrow{% else %}in {{ c.days_away }} days{% endif %}</span>
      </span>
      <span class="ev"><b>{{ c.name }}</b><p>{{ c.why|gloss }}</p></span>
    </li>
    {% endfor %}
  </ul>
</details>
{% endif %}

{% set tops = brief.events|selectattr('is_top')|list %}
{% set rest = brief.events|rejectattr('is_top')|list %}

{% if tops %}<div class="section">Today — what matters most</div>{% endif %}
{% for ev in tops %}{{ card(ev) }}{% endfor %}

{% if rest %}<div class="section">Also on the radar</div>{% endif %}
{% for ev in rest %}{{ card(ev) }}{% endfor %}

{% if brief.deeper_reads %}
<div class="section">Deeper reads</div>
<div class="deeper">
  {% for r in brief.deeper_reads %}
  <a class="dr" href="{{ r.url }}" target="_blank" rel="noopener">
    <span class="src">{{ r.source }}</span><span class="t">{{ r.title }}</span>
  </a>
  {% endfor %}
</div>
{% endif %}

<div class="disclaimer">
  <b>Learning tool, not advice.</b> This brief explains how world events <i>tend</i> to
  affect markets so you can learn the patterns and probabilities yourself. It never tells
  you what to buy or sell, and the odds shown are rough judgments, not guarantees.
</div>

<footer class="pagefoot">
  {% if brief.archive %}
  <div class="archive"><b>Past briefs:</b>
    {% for a in brief.archive %}<a href="{{ a.href }}">{{ a.label }}</a>{% endfor %}
  </div>{% endif %}
  <p>Generated automatically by your News Finance Hub · {{ brief.generated_at }}</p>
</footer>
</div></body></html>
"""

# The Pattern Library — a browsable study page of every transmission linkage.
PATTERNS_PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Pattern Library — India Impact Brief</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
<style>{{ css }}</style>
</head><body><div class="wrap">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <h1>The Pattern Library</h1>
  <div class="date">How global events tend to ripple into Indian markets —
    <b>{{ total }}</b> patterns the engine watches for</div>
</header>

{{ nav }}

<div class="guide">
  <b>How to use this:</b> <span class="flow">each pattern shows a cause → how it
  reaches India → what tends to move (and how likely) → what to watch.</span>
  These are typical mechanisms, not guarantees — the point is to learn the linkages
  so you can spot them in the news yourself. Any
  <span class="term" tabindex="0" role="button" data-def="Tap or hover an underlined word to see a simple definition.">underlined word</span>
  has a plain-English meaning.
</div>

{% for g in groups %}
<div class="section">{{ g.category|replace('_',' ')|title }}</div>
{% for lk in g.linkages %}
<article class="card">
  <h2>{{ lk.name }}</h2>
  {% if lk.triggers %}
  <div class="triggers"><span class="lead">Fires on news like:</span>
    {% for t in lk.triggers %}<span class="trig">{{ t }}</span>{% endfor %}
  </div>
  {% endif %}
  {% if lk.chain %}
    <div class="blocklabel">How this reaches India</div>
    <ul class="chain">{% for step in lk.chain %}<li>{{ step|gloss }}</li>{% endfor %}</ul>
  {% endif %}
  {% if lk.impacts %}
    <div class="blocklabel">What tends to move — and how likely</div>
    <div class="impacts">
      {% for im in lk.impacts %}
      <div class="impact">
        <span class="dir {{ 'up' if im.direction=='up' else 'down' }}">
          {{ '▲ Rises' if im.direction=='up' else '▼ Falls' }}</span>
        <div class="impact-body">
          <div class="impact-target">{{ im.target }}</div>
          {% if im.rationale %}<div class="impact-why">{{ im.rationale|gloss }}</div>{% endif %}
        </div>
        <div class="impact-side">
          <span class="meter">{{ im.probability|dots }}<span class="lvl">{{ im.probability }}</span></span>
          <span class="when">{{ im.horizon }}</span>
        </div>
      </div>
      {% endfor %}
    </div>
  {% endif %}
  {% if lk.watch_next %}
    <div class="blocklabel">What to watch next</div>
    <ul class="watch">{% for w in lk.watch_next %}<li>{{ w|gloss }}</li>{% endfor %}</ul>
  {% endif %}
</article>
{% endfor %}
{% endfor %}

<div class="disclaimer">
  <b>Learning tool, not advice.</b> These are typical cause-and-effect patterns to help
  you understand the machinery — never a recommendation to buy or sell anything.
</div>

<footer class="pagefoot">
  <div class="archive"><a href="index.html">← Back to today's brief</a></div>
  <p>News Finance Hub · the pattern library grows as new linkages are added.</p>
</footer>
</div></body></html>
"""


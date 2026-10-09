"""
render/templates.py — editorial, beginner-friendly templates (Jinja2 strings so
the project stays self-contained). One shared card macro powers web + email.

Design language (from the ui-ux-pro-max design system):
  * Editorial: Newsreader serif headlines + Inter sans body, generous whitespace.
  * Calm slate palette; green/red used ONLY for direction, never decoration.
  * Every card leads with a plain-English takeaway; jargon is tap-to-define.
"""

from urllib.parse import quote as _urlquote

# ---------------------------------------------------------------------------
# Brand mark: incoming waves from the wider world arriving at a single gold
# point — India. The product in one image. Drawn as plain geometry so it stays
# crisp at 16px (browser tab) and needs no font or external file.
# ---------------------------------------------------------------------------
LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
    'role="img" aria-label="The India Impact Brief">'
    '<rect width="64" height="64" rx="14" fill="#0f172a"/>'
    '<g fill="none" stroke="#5fa8ff" stroke-linecap="round" stroke-width="5">'
    '<path d="M39.1 22.2A12 12 0 0 0 39.1 41.8" opacity=".95"/>'
    '<path d="M34.5 15.6A20 20 0 0 0 34.5 48.4" opacity=".62"/>'
    '<path d="M29.9 9.1A28 28 0 0 0 29.9 54.9" opacity=".34"/>'
    '</g>'
    '<circle cx="46" cy="32" r="6" fill="#e0a94a"/>'
    '</svg>'
)

# The same mark for use inside a page. A data: URI favicon has no document to
# inherit from, so LOGO_SVG above keeps literal colours; this copy reads the
# page accent, which is how the brand mark tells you which section you are in.
LOGO_INLINE = LOGO_SVG.replace('stroke="#5fa8ff"', 'stroke="var(--accent)"')

# Inline data-URI favicon: self-contained, so it also works for local previews
# and file:// copies (no separate asset to 404).
_FAVICON_HREF = "data:image/svg+xml," + _urlquote(LOGO_SVG, safe="")
HEAD_ICON = (
    f'<link rel="icon" type="image/svg+xml" href="{_FAVICON_HREF}">'
    f'<link rel="apple-touch-icon" href="{_FAVICON_HREF}">'
    '<meta name="theme-color" content="#0f172a">'
)

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&"
    "family=Inter:wght@400;500;600;700&"
    # Geist Mono carries every small uppercase label and every number. It is
    # what makes a data product read as instrumented rather than typed.
    "family=Geist+Mono:wght@400;500;600;700&display=swap"
)

CSS = """/* ===========================================================================
   NEWS FINANCE HUB — stylesheet
   Dark only. One semantic colour scale. One spacing scale. One type scale.

   The previous sheet had grown to four separate red/amber/green systems, 56
   distinct padding values and 30 font sizes — which is why the pages drifted
   apart and why every fix needed another fix. Everything below is built from
   the tokens in section 1. Change a token, every page follows.

   Sections
     1  tokens          7  cards & panels
     2  reset & base    8  meters, pills, chips
     3  layout          9  tables & lists
     4  type           10  maps & charts
     5  keys           11  page-specific blocks
     6  surfaces       12  motion & reduced motion
   =========================================================================== */

/* ---------------------------------------------------------------- 1 TOKENS */
:root{
  color-scheme:dark;

  /* fonts */
  --serif:'Newsreader',Georgia,'Times New Roman',serif;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --mono:'Geist Mono',ui-monospace,'SFMono-Regular',Menlo,monospace;

  /* ---- elevation: one ladder, deepest at the back --------------------
     Cards sit only a little above the page and stay genuinely dark, so
     light text on them is high-contrast rather than washed out.          */
  --bg:        #080a0e;
  --surface-1: #0f131a;   /* cards, panels            */
  --surface-2: #141922;   /* blocks nested in a card  */
  --surface-3: #1b212c;   /* keys, chips              */
  --well:      #05070a;   /* recessed: maps, tracks   */

  /* ---- ink ----------------------------------------------------------- */
  --ink:    #eef2f7;      /* headings, numbers        */
  --ink-2:  #c6cedb;      /* body copy                */
  --ink-3:  #96a1b2;      /* secondary                */
  --ink-4:  #808c9b;      /* labels, captions         */

  --line:   #1e2530;      /* hairline                 */
  --line-2: #2a323f;      /* stronger divider         */

  /* ---- THE semantic scale -------------------------------------------
     Four meanings, used identically on every page:
       pos   good / cheap / calm / rising-is-good
       warn  caution / fair / worth watching
       neg   bad / dear / disrupted / falling-is-bad
       flat  neutral / no reading available
     Nothing else may invent its own red or green.                        */
  --pos:#45d19a;  --pos-bg:#0d2a1f;  --pos-line:#1c5f45;  --pos-ink:#062016;
  --warn:#e8b53f; --warn-bg:#2c2211; --warn-line:#6a5321; --warn-ink:#211802;
  --neg:#f5796c;  --neg-bg:#2e1614;  --neg-line:#6d2f29;  --neg-ink:#2a0906;
  --flat:#848f9f; --flat-bg:#151a22; --flat-line:#2b333f; --flat-ink:#e8edf3;

  /* heat ramp, derived from the same two hues so it can never drift */
  --heat-pos-2:#1f7a52; --heat-pos-1:#215a43;
  --heat-flat:#2c333f;
  --heat-neg-1:#5d2a25; --heat-neg-2:#9e3a30;

  /* ---- spacing: 4px base --------------------------------------------- */
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:20px;
  --s6:24px; --s7:32px; --s8:40px; --s9:56px;

  /* ---- padding: how much air each kind of container gets -------------
     Declared once, here, for the same reason the colours are: so a chip on
     one page cannot be tighter than the same chip on another. A pill needs
     more side padding than a square box because the rounded ends eat into
     the usable width.                                                    */
  --pad-pill:4px var(--s3);
  --pad-chip:var(--s1) var(--s3);
  --pad-block:var(--s4) var(--s5);

  /* ---- type: size paired with its line-height ------------------------ */
  --t-display:34px;  --lh-display:1.16;
  --t-h2:23px;       --lh-h2:1.3;
  --t-h3:19px;       --lh-h3:1.36;
  --t-body:16px;     --lh-body:1.68;   /* generous — this is a reading site */
  --t-sm:14.5px;     --lh-sm:1.62;
  --t-xs:13px;       --lh-xs:1.55;
  --t-label:11px;    --lh-label:1.45;

  /* ---- shape & depth -------------------------------------------------- */
  --r-sm:8px; --r-md:12px; --r-lg:18px; --r-pill:999px;
  --sh-1:0 1px 2px rgb(0 0 0/.55), 0 2px 6px rgb(0 0 0/.4);
  --sh-2:2px 4px 12px rgb(0 0 0/.5), 1px 2px 4px rgb(0 0 0/.45);
  --sh-3:8px 16px 40px rgb(0 0 0/.55), 3px 6px 14px rgb(0 0 0/.45);
  --inset:inset 0 1px 3px rgb(0 0 0/.5);
  --lit:inset 1px 1px 0 rgb(255 255 255/.055);

  /* ---- motion --------------------------------------------------------- */
  --ease:cubic-bezier(.22,1,.36,1);
  --press:.14s cubic-bezier(.16,.84,.32,1);

  /* accent is replaced per page in section 3 */
  --accent:#5fa8ff;
}

/* ---- the semantic classes. Every status class on every page resolves to
   one of four meanings, and components read --sem / --sem-bg / --sem-line. */
.pos,.up,.good,.v-cheap,.st-calm,.cheap{
  --sem:var(--pos); --sem-bg:var(--pos-bg); --sem-line:var(--pos-line);
}
.warn,.v-fair,.st-watch,.fair,.mood-mixed{
  --sem:var(--warn); --sem-bg:var(--warn-bg); --sem-line:var(--warn-line);
}
.neg,.down,.bad,.v-exp,.st-alert,.expensive{
  --sem:var(--neg); --sem-bg:var(--neg-bg); --sem-line:var(--neg-line);
}
.flat,.v-none,.none{
  --sem:var(--flat); --sem-bg:var(--flat-bg); --sem-line:var(--flat-line);
}
.mood-on{--sem:var(--pos); --sem-bg:var(--pos-bg);}
.mood-off{--sem:var(--neg); --sem-bg:var(--neg-bg);}
/* older component code still reads these two names */
:root,.pos,.warn,.neg,.flat{--vc:var(--sem,var(--flat)); --sc:var(--sem,var(--flat));
  --vb:var(--sem-bg,var(--flat-bg));}
*{--vc:var(--sem,var(--ink-3)); --sc:var(--sem,var(--ink-3));
  --vb:var(--sem-bg,var(--surface-2));}

/* legacy aliases kept so page code need not change */
:root{
  --panel:var(--surface-1); --panel2:var(--surface-2);
  --ink2:var(--ink-2); --muted:var(--ink-3); --faint:var(--ink-4);
  --line2:var(--line-2); --brand:var(--ink); --link:var(--accent);
  --up:var(--pos); --up-bg:var(--pos-bg); --down:var(--neg); --down-bg:var(--neg-bg);
  --c-cheap:var(--pos); --c-fair:var(--warn); --c-exp:var(--neg); --c-none:var(--flat-line);
  --cb-cheap:var(--pos-bg); --cb-fair:var(--warn-bg); --cb-exp:var(--neg-bg);
  --st-calm:var(--pos); --st-watch:var(--warn); --st-alert:var(--neg);
  --stb-calm:var(--pos-bg); --stb-watch:var(--warn-bg); --stb-alert:var(--neg-bg);
  --map-base:#232c38; --map-none:#141a22;
  --tip-bg:#1d2430; --tip-ink:#f2f5f9;
  --top-bg:#1f1a10; --top-line:#4a3f22;
  --font-serif:var(--serif); --font-sans:var(--sans);
}

/* ------------------------------------------------------- 2 RESET & BASE */
*{box-sizing:border-box;}
html{-webkit-text-size-adjust:100%;overflow-x:hidden;}
body{
  margin:0;background:var(--bg);color:var(--ink-2);
  font-family:var(--sans);font-size:var(--t-body);line-height:var(--lh-body);
  -webkit-font-smoothing:antialiased;overflow-x:hidden;
  font-variant-numeric:tabular-nums;
}
img{max-width:100%;}
button{font:inherit;color:inherit;}
a{color:var(--accent);}
:where(a,button,summary,[tabindex]):focus-visible{
  outline:2px solid var(--accent);outline-offset:2px;border-radius:var(--r-sm);
}
::selection{background:color-mix(in srgb,var(--accent) 35%,transparent);color:#fff;}

/* ------------------------------------------------------------- 3 LAYOUT */
.wrap{max-width:760px;margin:0 auto;padding:var(--s7) var(--s5) var(--s9);
  position:relative;z-index:1;}
.wrap.wide{max-width:1180px;}

/* One accent per section, so you know where you are before reading a word.
   Every one of them is deliberately OUTSIDE the red/amber/green band. The
   semantic scale owns those hues: if a page accent were orange or green,
   an accented heading would read as a status, and the same colour would
   mean "you are on Supply Lines" here and "worth watching" there. Keeping
   accents cool means a warm or green pixel anywhere on the site is always
   a status and never decoration.                                          */
body.page-global{--accent:#36c7d8;}   /* cyan       */
body.page-news  {--accent:#5fa8ff;}   /* azure      */
body.page-supply{--accent:#8f9bff;}   /* periwinkle */
body.page-assets{--accent:#b388f9;}   /* violet     */
body.page-learn {--accent:#8fa3bd;}   /* steel - the quiet reference page */

/* atmosphere: a wash in the page's colour, and a whisper of graph paper.
   Both fixed and non-interactive so they can never intercept a click. */
body::before{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(1000px 560px at 10% -10%,
      color-mix(in srgb,var(--accent) 11%,transparent), transparent 70%),
    radial-gradient(760px 440px at 95% 0%,
      color-mix(in srgb,var(--accent) 6%,transparent), transparent 72%);
}
body::after{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgb(255 255 255/.028) 1px,transparent 1px),
    linear-gradient(90deg,rgb(255 255 255/.028) 1px,transparent 1px);
  background-size:72px 72px;
  -webkit-mask-image:radial-gradient(1200px 680px at 50% 0%,#000,transparent 76%);
  mask-image:radial-gradient(1200px 680px at 50% 0%,#000,transparent 76%);
}

/* ------------------------------------------------------- 4 TYPOGRAPHY */
h1,h2,h3,h4,h5{margin:0;color:var(--ink);font-weight:600;}
p{margin:0 0 var(--s3);}
p:last-child{margin-bottom:0;}

.mast{padding-bottom:var(--s6);margin-bottom:var(--s2);position:relative;
  border-bottom:1px solid var(--line);}
.brandrow{display:flex;align-items:center;gap:var(--s3);}
.brandrow svg{width:40px;height:40px;flex:none;border-radius:var(--r-md);
  box-shadow:var(--sh-2),0 0 22px color-mix(in srgb,var(--accent) 26%,transparent);
  transition:box-shadow .25s var(--ease);}
.brandrow svg rect{fill:#060910;}
.brandrow svg g{stroke:var(--accent);}
.brandrow:hover svg{box-shadow:var(--sh-2),
  0 0 30px color-mix(in srgb,var(--accent) 42%,transparent);}
.mast h1{font-family:var(--serif);font-size:var(--t-display);
  line-height:var(--lh-display);letter-spacing:-.02em;font-weight:700;}
@media (max-width:520px){.mast h1{font-size:27px;}
  .brandrow svg{width:33px;height:33px;}}

.kicker{display:inline-flex;align-items:center;gap:var(--s2);
  font-family:var(--mono);font-size:var(--t-label);font-weight:500;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-4);
  margin-bottom:var(--s3);}
.kicker::before{content:"";width:6px;height:6px;border-radius:2px;flex:none;
  background:var(--accent);
  box-shadow:0 0 9px color-mix(in srgb,var(--accent) 75%,transparent);}
.date{margin-top:var(--s3);font-size:var(--t-sm);line-height:var(--lh-sm);
  color:var(--ink-3);}
.date .engine,.engine{font-family:var(--mono);font-size:var(--t-xs);
  color:var(--ink-4);}

/* every small uppercase label on the site, one rule */
.section,.blocklabel,.pblock h4,.slhead,.alerthead,.pkind,.epwhen,.hkick,
.famhead h3,.secshead,.rotblk h5,.hchain h5,.rgblk h5,.eprow b,.wl h5,
.hpattern b,.hindia b,.hwatch b,.rgindia b,.thead span,.qk,.lbl-cap,
.heatkey .lbl,.gn,.rband,.rer,.chip b,.tag,.vlbl,.histscale,.count{
  font-family:var(--mono);font-size:var(--t-label);line-height:var(--lh-label);
  font-weight:600;letter-spacing:.09em;text-transform:uppercase;
}
.section{display:flex;align-items:center;gap:var(--s3);margin:var(--s7) 0 var(--s4);
  color:color-mix(in srgb,var(--accent) 70%,var(--ink-2));}
.section::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,
    color-mix(in srgb,var(--accent) 38%,transparent),transparent);}
.blocklabel,.pblock h4{color:color-mix(in srgb,var(--accent) 52%,var(--ink-3));
  margin:var(--s5) 0 var(--s3);}
.pblock h4{margin:0 0 var(--s3);padding-bottom:var(--s2);
  border-bottom:1px solid var(--line);}

/* ---------------------------------------------------------------- 5 KEYS */
.key,.tabs a,.gf-switch button,.alertchip,.mapctl button,.slrow,
details.tablefold>summary,details.gf-acc>summary,.cal>summary{
  background:linear-gradient(145deg,var(--surface-3),var(--surface-1));
  border:1px solid var(--line-2);
  box-shadow:var(--sh-1),var(--lit);
  transition:box-shadow var(--press),transform var(--press),
             filter var(--press),color .15s var(--ease),
             border-color .15s var(--ease);
}
.tabs a:hover,.gf-switch button:hover,.alertchip:hover,.mapctl button:hover,
details.tablefold>summary:hover,details.gf-acc>summary:hover,.cal>summary:hover{
  filter:brightness(1.18);border-color:color-mix(in srgb,var(--accent) 40%,var(--line-2));
}
.tabs a:active,.gf-switch button:active,.alertchip:active,.mapctl button:active,
details.tablefold>summary:active,details.gf-acc>summary:active,.cal>summary:active{
  transform:translateY(1px);box-shadow:inset 0 1px 2px rgb(0 0 0/.6);
}

.tabs{display:flex;gap:var(--s2);margin:var(--s4) 0 var(--s2);padding-bottom:var(--s1);
  overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;}
.tabs::-webkit-scrollbar{display:none;}
.tabs a{display:inline-flex;align-items:center;flex:none;white-space:nowrap;
  min-height:44px;padding:var(--s2) var(--s4);border-radius:var(--r-sm);
  font-size:var(--t-xs);font-weight:600;color:var(--ink-3);text-decoration:none;}
.tabs a.on{color:var(--ink);
  border-color:color-mix(in srgb,var(--accent) 55%,transparent);
  box-shadow:var(--sh-1),var(--lit),
    0 0 14px color-mix(in srgb,var(--accent) 18%,transparent);}
.tabs a.on::before{content:"";width:5px;height:5px;border-radius:50%;flex:none;
  margin-right:var(--s2);background:var(--accent);
  box-shadow:0 0 8px color-mix(in srgb,var(--accent) 80%,transparent);}

.gf-switch{display:inline-flex;gap:var(--s1);padding:var(--s1);
  margin:var(--s5) 0 var(--s3);border-radius:var(--r-md);
  background:var(--well);border:1px solid var(--line);box-shadow:var(--inset);}
.gf-switch button{border-radius:var(--r-sm);border:0;background:transparent;
  box-shadow:none;padding:var(--s2) var(--s4);cursor:pointer;
  font-size:var(--t-xs);font-weight:600;color:var(--ink-3);}
.gf-switch button.on{color:var(--bg);background:var(--ink);box-shadow:var(--sh-2);}
.gf-switch button.on:hover{filter:brightness(1.08);}
.gf-view[hidden]{display:none;}

.mapctl{position:absolute;top:var(--s3);right:var(--s3);display:flex;
  flex-direction:column;gap:var(--s1);z-index:5;}
.mapctl button{width:30px;height:30px;border-radius:var(--r-sm);cursor:pointer;
  font-size:15px;font-weight:700;line-height:1;color:var(--ink-2);
  backdrop-filter:blur(8px);}

/* ------------------------------------------------------- 6/7 SURFACES */
.card,.panel,.histcard,.gauge,.regime,.rec,.alertbar,.sllist,.ctable,
.rot-now,.cal,.deeper .dr,.gf-note,.scenarios,.records .rec{
  background:var(--surface-1);
  border:1px solid var(--line);
  border-radius:var(--r-lg);
  box-shadow:var(--sh-1);
}
/* a lit top edge in the page's colour — the clearest "you are here" signal */
.card,.panel,.histcard,.gauge,.regime,.alertbar{
  border-top-color:color-mix(in srgb,var(--accent) 34%,var(--line));
}
.card{padding:var(--s6);margin-bottom:var(--s5);}
.card:hover{box-shadow:var(--sh-2);
  border-top-color:color-mix(in srgb,var(--accent) 58%,var(--line));}
.card.top{background:linear-gradient(180deg,var(--top-bg),var(--surface-1));
  border-color:var(--top-line);}
@media (max-width:520px){.card{padding:var(--s5) var(--s4);border-radius:var(--r-md);}}

.panel{padding:var(--s6);}
/* blocks nested inside a card step up one level, never down */
.pblock{margin:0 0 var(--s5);}
.pblock:last-child{margin-bottom:0;}
.tldr,.verdict,.analogy,.explain,.gf-india,.hpattern,.hindia,.hwatch,
.rgindia,.rotlesson,.gmean,.reading,.caveat,.qrows,.kv .k,.route,.episode,
.rh,.gn,.comchip,.chip,.supply,.impact,.heatkey,.maplegend,.gf-legend{
  background:var(--surface-2);border:1px solid var(--line);
  border-radius:var(--r-md);padding:var(--pad-block);
}
.tldr,.verdict,.gf-india,.hpattern,.hindia,.hwatch,.rgindia,.rotlesson,.gmean{
  border-left:3px solid var(--sem,var(--accent));
  border-radius:0 var(--r-md) var(--r-md) 0;
  padding:var(--s4) var(--s5);margin:0 0 var(--s4);
}
.tldr{border-left-color:var(--accent);}
.tldr .lbl,.verdict b,.hpattern b,.hindia b,.hwatch b,.rgindia b,.rotlesson b{
  display:block;font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.09em;text-transform:uppercase;margin-bottom:var(--s2);
  color:var(--sem,var(--accent));
}
.tldr .lbl{color:var(--accent);}
.tldr p,.verdict{color:var(--ink);font-size:var(--t-body);line-height:var(--lh-body);}
.tldr p{margin:0;}
.explain,.analogy,.caveat{border-radius:var(--r-md);padding:var(--s4);
  margin:var(--s3) 0 0;font-size:var(--t-xs);line-height:var(--lh-xs);
  color:var(--ink-3);}
.explain b,.analogy b,.caveat b{color:var(--ink-2);}
.what,.pnote,.hlede,.rotblk p,.rgblk p,.hchain p,.gauge p{
  color:var(--ink-2);font-size:var(--t-sm);line-height:var(--lh-sm);margin:0 0 var(--s3);}
.hlede{font-size:var(--t-body);line-height:var(--lh-body);}

.tags{display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center;
  margin-bottom:var(--s3);}
.tag{color:var(--ink-4);}
.tag.dot::before{content:"•";margin-right:var(--s2);color:var(--line-2);}
.card h2{font-family:var(--serif);font-size:var(--t-h2);line-height:var(--lh-h2);
  letter-spacing:-.01em;margin:0 0 var(--s4);}
.panel h3,.gauge h4,.regime h4,.histcard h3,.rotline{
  font-family:var(--serif);font-size:var(--t-h3);line-height:var(--lh-h3);
  margin:0 0 var(--s2);}
.histcard h3{font-size:25px;}
.sub{color:var(--ink-4);font-size:var(--t-xs);margin:0 0 var(--s4);}
.hint{color:var(--ink-3);font-size:var(--t-sm);margin:0;}

/* lists of statements */
.chain,.plist,.story,.scenarios ul,.wl ul{list-style:none;margin:0 0 var(--s4);padding:0;}
.chain li,.plist li,.story li,.scenarios li,.wl li{
  position:relative;padding:var(--s2) 0 var(--s2) var(--s5);
  color:var(--ink-2);font-size:var(--t-sm);line-height:var(--lh-sm);}
.chain li::before,.plist li::before,.scenarios li::before,.wl li::before{
  content:"";position:absolute;left:3px;top:calc(var(--s2) + .62em);
  width:6px;height:6px;border-radius:50%;background:var(--sem,var(--accent));}
.story li::before{content:"";position:absolute;left:3px;
  top:calc(var(--s2) + .6em);width:6px;height:6px;border-radius:2px;
  background:var(--ink-4);}
.story li{color:var(--ink);font-size:var(--t-body);line-height:var(--lh-body);}
.plist.good li::before{background:var(--pos);}
.plist.bad li::before{background:var(--neg);}

/* key/value stat tiles */
.kv{display:flex;flex-wrap:wrap;gap:var(--s2);}
.kv .k{flex:1 1 120px;border-radius:var(--r-md);padding:var(--s3) var(--s4);
  font-family:var(--mono);font-size:var(--t-label);letter-spacing:.07em;
  text-transform:uppercase;color:var(--ink-4);}
.kv .k b{display:block;margin-top:var(--s1);font-family:var(--sans);
  font-size:17px;font-weight:600;letter-spacing:0;text-transform:none;
  color:var(--ink);}
.kv .k.wide{flex:1 1 100%;}

/* prose facts, label beside value */
.qrows{border-radius:var(--r-md);padding:var(--s2) var(--s4);margin-top:var(--s3);}
.qrow{display:flex;gap:var(--s4);padding:var(--s3) 0;
  border-bottom:1px solid var(--line);}
.qrow:last-child{border-bottom:0;}
.qk{flex:0 0 136px;color:var(--ink-4);padding-top:2px;}
.qv{flex:1;min-width:0;color:var(--ink-2);font-size:var(--t-xs);
  line-height:var(--lh-xs);}
@media (max-width:560px){.qrow{flex-direction:column;gap:var(--s1);}
  .qk{flex:none;}}

/* --------------------------------------------- 8 METERS, PILLS, CHIPS */
.badge,.gf-vpill,.stpill,.livepill,.conf,.mood-tag,.rband,.lvl{
  display:inline-flex;align-items:center;gap:var(--s1);
  font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.07em;text-transform:uppercase;white-space:nowrap;
  padding:var(--pad-pill);border-radius:var(--r-pill);
  color:var(--sem,var(--ink-3));background:var(--sem-bg,var(--surface-3));
  border:1px solid color-mix(in srgb,var(--sem,var(--line-2)) 30%,transparent);
}
.badge{color:var(--warn);background:var(--warn-bg);border-color:var(--warn-line);}
.badge.dev{color:var(--accent);
  background:color-mix(in srgb,var(--accent) 14%,transparent);
  border-color:color-mix(in srgb,var(--accent) 34%,transparent);}
.gf-vpill,.stpill{margin-left:var(--s2);vertical-align:middle;}
.livepill.on{color:var(--pos);background:var(--pos-bg);border-color:var(--pos-line);}
.livepill.off{color:var(--ink-4);background:var(--surface-3);}
.livepill.on::before{content:"";width:6px;height:6px;border-radius:50%;
  background:var(--pos);}

.chip,.comchip,.rh{display:inline-flex;align-items:baseline;gap:var(--s1);
  border-radius:var(--r-sm);padding:var(--s1) var(--s3);
  font-size:var(--t-xs);color:var(--ink-2);}
.chip b,.rh b{color:var(--ink-4);margin-right:var(--s1);}

/* meters: a recessed track with a lit fill */
.track,.secbar,.hist,.meter{background:var(--well);border-radius:var(--r-pill);
  box-shadow:var(--inset);position:relative;}
.erow{display:flex;align-items:center;gap:var(--s3);margin-bottom:var(--s2);
  font-size:var(--t-xs);}
.erow .lbl{flex:0 0 118px;color:var(--ink-3);line-height:1.4;}
.erow .track{flex:1;height:8px;overflow:visible;}
.erow .fill{position:absolute;top:0;bottom:0;border-radius:var(--r-pill);}
.erow .fill.pos{background:var(--pos);box-shadow:0 0 10px color-mix(in srgb,var(--pos) 45%,transparent);}
.erow .fill.neg{background:var(--neg);box-shadow:0 0 10px color-mix(in srgb,var(--neg) 45%,transparent);}
.erow .num{flex:0 0 58px;text-align:right;font-weight:600;color:var(--ink);}
.erow.total{border-top:1px solid var(--line);padding-top:var(--s3);
  margin-top:var(--s3);}
.erow.total .lbl,.erow.total .num{font-weight:700;color:var(--ink);}
.erbar{display:flex;flex-direction:column;gap:var(--s1);margin-top:var(--s3);}

.secs{margin-top:var(--s4);}
.sec{display:flex;gap:var(--s3);align-items:flex-start;margin-bottom:var(--s3);}
.secbar{flex:0 0 48px;height:7px;margin-top:7px;overflow:hidden;}
.secbar span{display:block;height:100%;border-radius:var(--r-pill);
  background:var(--sem,var(--accent));
  box-shadow:0 0 8px color-mix(in srgb,var(--sem,var(--accent)) 50%,transparent);}
.sectxt{flex:1;min-width:0;}
.sectxt b{color:var(--ink);font-size:var(--t-sm);font-weight:600;}
.sectxt .pct{color:var(--ink-4);font-size:var(--t-xs);margin-left:var(--s2);}
.sectxt p{margin:2px 0 0;color:var(--ink-3);font-size:var(--t-xs);
  line-height:var(--lh-xs);}

.hist{display:block;width:100%;height:6px;margin-top:var(--s3);}
.hist .tick{position:absolute;left:50%;top:-3px;bottom:-3px;width:2px;
  margin-left:-1px;background:var(--line-2);border-radius:2px;}
.hist .pin{position:absolute;top:-3px;width:12px;height:12px;border-radius:50%;
  background:var(--sem,var(--accent));border:2px solid var(--surface-1);
  transform:translateX(-50%);
  box-shadow:0 0 10px color-mix(in srgb,var(--sem,var(--accent)) 55%,transparent);}
.hist.none{background:repeating-linear-gradient(90deg,
  var(--line) 0 5px,transparent 5px 10px);box-shadow:none;}
/* the caption under a history bar. Sentence case, not a tracked-out label:
   at 11px uppercase these three phrases collide in a narrow column, and
   they read as a sentence rather than a heading anyway. */
.histscale{display:flex;justify-content:space-between;gap:var(--s2);
  margin-top:var(--s2);color:var(--ink-3);font-size:var(--t-label);
  line-height:var(--lh-label);letter-spacing:0;text-transform:none;
  font-weight:500;}
.histscale span:nth-child(2){text-align:center;}
.histscale span:last-child{text-align:right;}

.dots{display:inline-flex;gap:3px;}
.dots i{width:5px;height:5px;border-radius:50%;background:var(--line-2);}
.dots i.on{background:var(--ink-3);}

/* ------------------------------------------------ 9 TABLES, LISTS, GRID */
/* Both columns are the same height and scroll inside themselves, so the two
   panes line up instead of one running on past the other. */
.gf-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,460px);
  gap:var(--s4);margin-top:var(--s4);align-items:stretch;}
@media (min-width:901px){
  .gf-grid{--pane:calc(100vh - var(--s9));}
  .gf-panelwrap{position:sticky;top:var(--s4);height:var(--pane);}
  .panel{height:100%;overflow-y:auto;overflow-x:hidden;}
  .sllist,.ctable{max-height:var(--pane);overflow-y:auto;overflow-x:hidden;}
}
/* With the table folded away the left column holds one small button, which
   left a large hole beside a very tall panel. Give the panel the full width
   until the table is opened. */
.gf-grid:has(details.tablefold:not([open])){grid-template-columns:minmax(0,1fr);}
@media (max-width:900px){
  .gf-grid{grid-template-columns:1fr;}
  .gf-panelwrap{position:static;order:-1;height:auto;}
  .gf-panelwrap .panel{height:auto;max-height:none;overflow:visible;}
  .sllist,.ctable{max-height:none;overflow:visible;}
}

.ctable{overflow:hidden;}
.ctable .thead,.ctable .row{display:grid;align-items:center;
  grid-template-columns:minmax(0,1fr) 92px 62px 104px;}
.ctable.acols .thead,.ctable.acols .row{
  grid-template-columns:minmax(0,1fr) 92px 92px 100px;}
.ctable .thead{position:sticky;top:0;z-index:2;background:var(--well);
  border-bottom:1px solid var(--line-2);color:var(--ink-4);}
.ctable .thead span{padding:var(--s3) var(--s3);cursor:pointer;user-select:none;
  min-width:0;align-self:end;}
.ctable .thead span:hover{color:var(--ink-2);}
.ctable .thead span.sorted{color:var(--accent);}
.ctable .row{border-bottom:1px solid var(--line);cursor:pointer;
  font-size:var(--t-xs);}
.ctable .row:last-child{border-bottom:0;}
.ctable .row:hover{background:color-mix(in srgb,var(--accent) 7%,transparent);}
.ctable .row.sel{background:color-mix(in srgb,var(--accent) 10%,transparent);
  box-shadow:inset 3px 0 0 var(--sem,var(--accent));}
.ctable .row>span{padding:var(--s3);min-width:0;}
.c-name{display:flex;align-items:center;gap:var(--s2);color:var(--ink);
  font-weight:600;}
.c-name .sw{width:9px;height:9px;border-radius:3px;flex:none;
  background:var(--sem,var(--flat));}
.c-name i{font-style:normal;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;}
.c-val{color:var(--sem,var(--ink-3));font-family:var(--mono);
  font-size:var(--t-label);letter-spacing:.06em;text-transform:uppercase;}
.c-cape,.c-met{color:var(--ink-3);text-align:right;}
.c-er{text-align:right;font-weight:600;}
@media (max-width:560px){
  .ctable .thead,.ctable .row{grid-template-columns:minmax(0,1fr) 58px 84px;}
  .ctable.acols .thead,.ctable.acols .row{
    grid-template-columns:minmax(0,1fr) 78px 84px;}
  .c-val{display:none;}
}

details.tablefold{margin:0;}
details.tablefold>summary{list-style:none;cursor:pointer;display:inline-flex;
  align-items:center;gap:var(--s2);padding:var(--s3) var(--s4);
  border-radius:var(--r-md);font-size:var(--t-xs);font-weight:600;
  color:var(--ink-2);}
details.tablefold>summary::-webkit-details-marker{display:none;}
details.tablefold>summary::marker{content:"";font-size:0;}
details.tablefold>summary::after{content:"";width:6px;height:6px;
  border-right:1.5px solid var(--ink-4);border-bottom:1.5px solid var(--ink-4);
  transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s var(--ease);}
details.tablefold[open]>summary::after{transform:rotate(-135deg) translate(-2px,-2px);}
details.tablefold .ctable{margin-top:var(--s3);}

.sllist{overflow:hidden;}
.slhead{padding:var(--s3) var(--s4);background:var(--well);
  color:var(--ink-4);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2;}
.slhead:not(:first-child){border-top:1px solid var(--line);}
.slrow{display:flex;align-items:center;gap:var(--s3);width:100%;
  text-align:left;cursor:pointer;background:transparent;border:0;
  border-bottom:1px solid var(--line);box-shadow:none;
  padding:var(--s3) var(--s4);}
.slrow:last-child{border-bottom:0;}
.slrow:hover{background:color-mix(in srgb,var(--accent) 7%,transparent);}
.slrow.sel{background:color-mix(in srgb,var(--accent) 11%,transparent);
  box-shadow:inset 3px 0 0 var(--sem,var(--accent));}
.sldot{width:9px;height:9px;border-radius:50%;flex:none;
  background:var(--sem,var(--flat));
  box-shadow:0 0 8px color-mix(in srgb,var(--sem,var(--flat)) 55%,transparent);}
.sltext{flex:1;min-width:0;}
.sltext b{display:block;font-size:var(--t-sm);font-weight:600;color:var(--ink);
  line-height:1.35;}
.sltext em{display:block;font-style:normal;font-size:var(--t-xs);
  color:var(--ink-3);line-height:1.45;margin-top:2px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.slemoji{flex:none;font-size:15px;letter-spacing:1px;}

/* ------------------------------------------------- 10 MAPS & CHARTS */
.map-wrap,.heatwrap{position:relative;background:var(--well);
  border-radius:var(--r-lg);overflow:hidden;
  box-shadow:var(--inset),inset 0 0 0 1px var(--line);}
.map-wrap svg{display:block;width:100%;height:auto;cursor:grab;
  touch-action:none;background:transparent;}
.map-wrap svg.drag{cursor:grabbing;}
.cty{fill:var(--map-none);stroke:var(--well);stroke-width:.45;
  transition:fill .15s ease,opacity .15s ease;}
.cty.has{cursor:pointer;fill:var(--map-base);}
.cty.cheap,.cty.st-calm{fill:var(--pos);fill-opacity:.6;}
.cty.fair,.cty.st-watch{fill:var(--warn);fill-opacity:.62;}
.cty.expensive,.cty.st-alert{fill:var(--neg);fill-opacity:.7;}
.cty.has:hover{fill-opacity:.95;}
.cty.sel{stroke:var(--ink);stroke-width:1.4;fill-opacity:1;}
#smap{--mz:1;}
#smap .route{fill:none;stroke:var(--sem,var(--flat));
  stroke-width:calc(2.2*var(--mz));stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:calc(7*var(--mz)) calc(4*var(--mz));}
#smap .route.st-alert{stroke-dasharray:none;stroke-width:calc(3*var(--mz));}
#smap .routehit{fill:none;stroke:transparent;stroke-width:calc(13*var(--mz));
  cursor:pointer;stroke-linecap:round;}
#smap .route.sel{stroke-dasharray:none;stroke-width:calc(3.6*var(--mz));}
#smap .rlabel{font-family:var(--mono);font-size:calc(9px*var(--mz));
  font-weight:600;fill:var(--sem,var(--flat));text-anchor:middle;cursor:pointer;
  paint-order:stroke;stroke:var(--well);stroke-width:calc(2.5px*var(--mz));}
#smap .mark{cursor:pointer;}
#smap .mark rect{fill:var(--surface-1);stroke:var(--sem,var(--flat));
  stroke-width:calc(1.4*var(--mz));}
#smap .mark text{font-size:calc(13px*var(--mz));text-anchor:middle;
  dominant-baseline:central;pointer-events:none;}
#smap .mark .more{font-family:var(--mono);font-size:calc(9.5px*var(--mz));
  font-weight:700;fill:var(--sem,var(--ink-3));}
#smap .mark.sel rect,#smap .mark:hover rect{stroke:var(--ink);
  stroke-width:calc(2.2*var(--mz));}

.maptip{position:absolute;pointer-events:none;z-index:30;opacity:0;
  background:var(--tip-bg);color:var(--tip-ink);border:1px solid var(--line-2);
  font-size:var(--t-xs);line-height:1.45;padding:var(--s2) var(--s3);
  border-radius:var(--r-md);box-shadow:var(--sh-3);
  transition:opacity .12s ease;white-space:nowrap;max-width:280px;}
.maptip.on{opacity:1;}
.maptip b{display:block;color:#fff;}
.maptip .wrapline{display:block;white-space:normal;margin-top:2px;font-weight:400;}

.maplegend,.gf-legend,.heatkey,.heatlegend{display:flex;flex-wrap:wrap;
  gap:var(--s2);align-items:center;margin:0 0 var(--s3);
  background:transparent;border:0;padding:0;}
.lg,.sc{display:inline-flex;align-items:center;gap:var(--s2);
  font-size:var(--t-xs);color:var(--ink-2);background:var(--surface-2);
  border:1px solid var(--line);border-radius:var(--r-pill);
  padding:var(--s1) var(--s3);}
.lg .sw,.sc .box{width:11px;height:11px;border-radius:3px;
  background:var(--sem,var(--flat));}
.hintx{color:var(--ink-4);font-size:var(--t-xs);}
.heatkey .bar{display:flex;border-radius:var(--r-sm);overflow:hidden;}
.heatkey .bar i{width:26px;height:12px;display:block;}

/* valuation heat grid */
.heatgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));
  gap:var(--s1);}
.hcell{display:flex;flex-direction:column;justify-content:center;min-height:78px;
  padding:var(--s3);border:1px solid rgb(255 255 255/.06);
  border-radius:var(--r-sm);cursor:pointer;text-align:left;
  transition:transform .1s ease,box-shadow .1s ease;
  outline:2px solid transparent;outline-offset:-2px;}
.hcell:hover{transform:scale(1.03);z-index:3;box-shadow:var(--sh-2);}
.hcell.sel{outline-color:var(--ink);z-index:2;}
.hcell.c2{background:var(--heat-pos-2);color:#eafff5;}
.hcell.c1{background:var(--heat-pos-1);color:#dcf2e7;}
.hcell.n {background:var(--heat-flat); color:#d5dce6;}
.hcell.d1{background:var(--heat-neg-1); color:#f6d9d4;}
.hcell.d2{background:var(--heat-neg-2); color:#ffeae6;}
.hcell.na{background:repeating-linear-gradient(135deg,
  var(--heat-flat) 0 6px,#232a35 6px 12px);color:#d5dce6;}
.hname{display:block;font-size:var(--t-xs);font-weight:600;line-height:1.3;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.hval{display:block;font-size:16px;font-weight:700;line-height:1.2;
  margin-top:3px;}
.hgap{display:block;font-size:var(--t-label);line-height:1.35;margin-top:2px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
@media (max-width:520px){
  .heatgrid{grid-template-columns:repeat(auto-fill,minmax(102px,1fr));}
  .hcell{min-height:70px;padding:var(--s2);}
}

/* rotation heat table */
.heatwrap{padding:var(--s4);overflow-x:auto;}
.heat{border-collapse:separate;border-spacing:3px;width:100%;min-width:640px;}
.heat th{font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  color:var(--ink-4);text-align:left;padding:var(--s1) var(--s2);
  white-space:nowrap;}
.heat td{height:30px;border-radius:7px;cursor:pointer;position:relative;
  transition:transform .1s ease;}
.heat td:hover{transform:scale(1.1);z-index:5;box-shadow:var(--sh-2);}
.heat .rowlbl{position:sticky;left:0;z-index:3;background:var(--well);
  color:var(--ink-2);font-size:var(--t-xs);font-weight:600;
  padding:0 var(--s3) 0 2px;width:1%;
  box-shadow:-16px 0 0 var(--well),1px 0 0 var(--line);}
.heat thead th:first-child{position:sticky;left:0;z-index:4;
  background:var(--well);box-shadow:-16px 0 0 var(--well);}
.heat .rowlbl.gold{color:var(--warn);}
.s2{background:var(--heat-pos-2);} .s1{background:var(--heat-pos-1);}
.s0{background:var(--heat-flat);}
.sm1{background:var(--heat-neg-1);} .sm2{background:var(--heat-neg-2);}

/* ------------------------------------------- 11 PAGE-SPECIFIC BLOCKS */

/* --- news: impacts ---------------------------------------------------- */
.impacts{display:flex;flex-direction:column;gap:var(--s2);}
.impact{display:flex;gap:var(--s3);align-items:flex-start;
  border-radius:var(--r-md);padding:var(--s3) var(--s4);}
.dir{flex:none;display:inline-flex;align-items:center;gap:var(--s1);
  font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;
  padding:var(--pad-pill);border-radius:var(--r-sm);
  color:var(--sem);background:var(--sem-bg);
  border:1px solid color-mix(in srgb,var(--sem) 32%,transparent);}
.impact-body{flex:1;min-width:0;}
.impact-target{color:var(--ink);font-size:var(--t-sm);font-weight:600;
  line-height:1.4;}
.impact-why{color:var(--ink-3);font-size:var(--t-xs);line-height:var(--lh-xs);
  margin-top:2px;}
.impact-side{display:grid;grid-template-columns:112px minmax(0,1fr);
  align-items:center;gap:var(--s2);flex:none;width:200px;
  font-size:var(--t-xs);color:var(--ink-3);}
.lvl{background:transparent;border:0;padding:0;color:var(--ink-3);}
/* The confidence capsule in an impact row. It used to carry class="meter",
   which section 8 styles as a recessed TRACK - a track needs no padding
   because its fill is absolutely positioned, so the dots and the word ended
   up flush against the capsule edge. It is a chip, so it is styled as one.
   The fixed width keeps LOW / MEDIUM / HIGH aligned down the column instead
   of each capsule sizing itself to its own word. */
.plevel{display:inline-flex;align-items:center;gap:var(--s2);flex:none;
  width:112px;padding:var(--pad-pill);border-radius:var(--r-pill);
  font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.07em;text-transform:uppercase;white-space:nowrap;
  color:var(--ink-3);background:var(--surface-3);
  border:1px solid var(--line-2);}
@media (max-width:520px){.plevel{width:auto;}}
@media (max-width:520px){
  .impact{flex-wrap:wrap;}
  .impact-side{margin-left:0;width:100%;
    grid-template-columns:auto auto;justify-content:start;}
}

/* --- news: calendar --------------------------------------------------- */
.cal{overflow:hidden;margin-top:var(--s4);}
.cal>summary{list-style:none;cursor:pointer;display:flex;align-items:center;
  gap:var(--s3);padding:var(--s4) var(--s5);border-radius:var(--r-lg);
  font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);}
.cal>summary::-webkit-details-marker{display:none;}
.cal>summary::marker{content:"";font-size:0;}
.cal>summary:hover{color:var(--ink);}
.cal .chev{margin-left:auto;width:7px;height:7px;flex:none;
  border-right:1.5px solid var(--ink-4);border-bottom:1.5px solid var(--ink-4);
  transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s var(--ease);}
.cal[open] .chev{transform:rotate(-135deg) translate(-2px,-2px);}
/* the bell badge must never wrap — it was breaking onto two lines */
.cal .alert{display:inline-flex;align-items:center;gap:var(--s1);flex:none;
  white-space:nowrap;color:var(--warn);background:var(--warn-bg);
  border:1px solid var(--warn-line);border-radius:var(--r-pill);
  padding:var(--pad-pill);letter-spacing:.04em;}
.cal .lead{max-height:360px;overflow-y:auto;padding:0 var(--s5) var(--s4);}
.calmonth{position:sticky;top:0;background:var(--surface-1);z-index:1;
  font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.09em;text-transform:uppercase;color:var(--ink-4);
  /* pulled out to the card edge so rows scroll UNDER it rather than through
     the 20px gutter .lead leaves on either side */
  margin:0 calc(var(--s5) * -1);padding:var(--s3) var(--s5) var(--s2);
  border-bottom:1px solid var(--line);}
.cal .ev{display:flex;gap:var(--s3);padding:var(--s3) 0;
  border-bottom:1px solid var(--line);}
.cal .ev:last-child{border-bottom:0;}
.cal .when{flex:0 0 92px;font-family:var(--mono);font-size:var(--t-xs);
  color:var(--ink-3);}
.cal .what{flex:1;min-width:0;font-size:var(--t-sm);color:var(--ink-2);
  line-height:var(--lh-sm);}
.cal .ev.soon .when{color:var(--warn);}

/* --- news: macro strip, deeper reads --------------------------------- */
.macro{display:flex;flex-wrap:wrap;gap:var(--s2);margin-top:var(--s4);}
.macro .m{background:var(--surface-2);border:1px solid var(--line);
  border-radius:var(--r-md);padding:var(--s2) var(--s3);
  font-size:var(--t-xs);color:var(--ink-3);}
.macro .m b{color:var(--ink);font-weight:600;}
.deeper{display:flex;flex-direction:column;gap:var(--s2);}
.deeper .dr{display:flex;flex-wrap:wrap;gap:var(--s2) var(--s4);
  align-items:baseline;padding:var(--s3) var(--s4);text-decoration:none;
  border-radius:var(--r-md);}
.deeper .dr:hover{border-color:color-mix(in srgb,var(--accent) 45%,var(--line));}
.deeper .src{font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.06em;text-transform:uppercase;color:var(--accent);
  white-space:nowrap;}
.deeper .t{color:var(--ink-2);font-size:var(--t-sm);}
.deeper .dr:hover .t{color:var(--ink);}
.readsrc{display:inline-block;margin:2px 0 var(--s2);font-family:var(--mono);
  font-size:var(--t-xs);color:var(--accent);text-decoration:none;}
.readsrc:hover{text-decoration:underline;}

/* --- news: history card ---------------------------------------------- */
.histcard{padding:var(--s6);border-top-color:var(--warn-line);}
.hkick{color:var(--warn);}
.hchain{list-style:none;margin:var(--s5) 0 0;padding:0;counter-reset:hstep;}
.hchain li{position:relative;padding:0 0 var(--s4) var(--s8);counter-increment:hstep;}
.hchain li::before{content:counter(hstep);position:absolute;left:0;top:0;
  width:26px;height:26px;border-radius:50%;background:var(--surface-2);
  border:1px solid var(--line-2);color:var(--ink-4);font-family:var(--mono);
  font-size:var(--t-label);font-weight:700;display:flex;align-items:center;
  justify-content:center;}
.hchain li::after{content:"";position:absolute;left:13px;top:28px;bottom:2px;
  width:1px;background:var(--line);}
.hchain li:last-child{padding-bottom:0;}
.hchain li:last-child::after{display:none;}
.hchain h5{color:var(--ink-4);margin:var(--s1) 0 var(--s2);}
.hpattern{border-left-color:var(--warn);background:var(--warn-bg);}
.hpattern b{color:var(--warn);}
.hindia{border-left-color:var(--accent);}
.hindia b{color:var(--accent);}
.hwatch b{color:var(--ink-3);}

/* --- global finance: rotation ---------------------------------------- */
.rot-now{padding:var(--s5);margin-bottom:var(--s4);}
.rot-now .mood{font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;color:var(--accent);}
.rot-now p{margin:var(--s2) 0 0;color:var(--ink-2);font-size:var(--t-body);}
.scenarios{padding:var(--s4) var(--s5);margin-bottom:var(--s3);
  border-radius:var(--r-md);}
.scenarios h4{font-family:var(--mono);font-size:var(--t-label);font-weight:600;
  letter-spacing:.09em;text-transform:uppercase;color:var(--accent);
  margin:0 0 var(--s2);}
.scenarios.watch h4{color:var(--warn);}
.scenarios li::before{background:var(--accent);}
.scenarios.watch li::before{background:var(--warn);}
.rot{list-style:none;margin:0;padding:0;}
.rot li{position:relative;padding:0 0 var(--s6) var(--s6);}
.rot li::before{content:"";position:absolute;left:4px;top:6px;width:9px;height:9px;
  border-radius:50%;background:var(--accent);}
.rot li::after{content:"";position:absolute;left:8px;top:18px;bottom:0;width:1px;
  background:var(--line);}
.rot li:last-child::after{display:none;}
.rot li.hl::before{background:var(--warn);
  box-shadow:0 0 0 4px var(--warn-bg);}
.rothead{display:flex;align-items:center;gap:var(--s2);flex-wrap:wrap;}
.rot .per{font-family:var(--mono);font-weight:700;color:var(--ink);
  font-size:var(--t-sm);}
.rotline{margin:var(--s2) 0 var(--s3);}
.rot .flows{display:flex;flex-wrap:wrap;gap:var(--s1);margin:var(--s2) 0;}
.into,.outof{font-size:var(--t-xs);padding:3px var(--s2);border-radius:var(--r-sm);}
.into{color:var(--pos);background:var(--pos-bg);}
.outof{color:var(--neg);background:var(--neg-bg);}
.into.gold{color:var(--warn);background:var(--warn-bg);font-weight:600;}
.rotblk{margin:0 0 var(--s3);}
.rotlesson{border-left-color:var(--warn);}
.rotlesson b{color:var(--warn);}

/* --- assets: valuation board & panel --------------------------------- */
.board{display:flex;flex-direction:column;}
.fam{margin-top:var(--s2);}
.famhead{display:flex;align-items:baseline;gap:var(--s3);flex-wrap:wrap;
  margin:var(--s5) 0 var(--s1);}
.famhead h3{color:var(--ink-2);}
.count{color:var(--ink-4);}
.famnote{color:var(--ink-3);font-size:var(--t-xs);line-height:var(--lh-xs);
  margin:0 0 var(--s3);max-width:76ch;}
.vsnow{display:flex;align-items:center;gap:var(--s4);background:var(--surface-2);
  border:1px solid var(--line);border-radius:var(--r-md);
  padding:var(--s4);margin:0 0 var(--s4);}
.vbig{font-family:var(--serif);font-size:32px;font-weight:600;line-height:1;
  color:var(--sem,var(--ink));letter-spacing:-.01em;}
.vmid{flex:1;min-width:0;}
.vhead{display:flex;align-items:center;gap:var(--s2);flex-wrap:wrap;}
.vlbl{color:var(--ink-4);}
.vavg{font-size:var(--t-xs);color:var(--ink-2);line-height:1.5;margin-top:2px;}
.vavg b{color:var(--ink);font-weight:600;}
.reading{border-left:3px solid var(--accent);border-radius:0 var(--r-md) var(--r-md) 0;
  padding:var(--s3) var(--s4);margin:0 0 var(--s3);font-size:var(--t-xs);
  color:var(--ink-2);}
.howto{display:flex;flex-direction:column;gap:var(--s2);}
.route{border-radius:var(--r-md);padding:var(--s3) var(--s4);}
.rname{font-size:var(--t-sm);font-weight:600;color:var(--ink);}
.rex{display:block;font-size:var(--t-xs);color:var(--ink-3);margin-top:2px;}
.rchips{display:flex;flex-wrap:wrap;gap:var(--s1);margin:var(--s2) 0;}
.route p{margin:0;font-size:var(--t-xs);line-height:var(--lh-xs);
  color:var(--ink-2);}
.gauges{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:var(--s3);}
.gauge{padding:var(--s5);}
.gmet{display:block;font-size:var(--t-xs);color:var(--ink-3);
  line-height:1.45;margin-bottom:var(--s3);}
.gnums{display:flex;flex-wrap:wrap;gap:var(--s2);margin:var(--s3) 0;}
.gn{flex:1 1 130px;border-radius:var(--r-md);padding:var(--s3);
  color:var(--ink-4);}
.gn span{display:block;font-family:var(--sans);font-size:var(--t-sm);
  font-weight:600;letter-spacing:0;text-transform:none;margin-top:2px;
  color:var(--ink);}
.gn.now span{color:var(--sem,var(--accent));}
.records{display:flex;flex-direction:column;gap:var(--s2);}
.rec{padding:var(--s4);border-left:3px solid var(--sem,var(--flat));}
.rtop{display:flex;align-items:baseline;gap:var(--s3);flex-wrap:wrap;}
.rname,.rec .rname{font-size:var(--t-sm);font-weight:600;color:var(--ink);}
.rband{color:var(--sem,var(--ink-3));background:transparent;border:0;padding:0;}
.rer{margin-left:auto;color:var(--ink-4);background:transparent;border:0;padding:0;}
.rer b{font-family:var(--sans);font-size:var(--t-sm);font-weight:600;
  letter-spacing:0;text-transform:none;color:var(--ink-2);margin-left:var(--s1);}
.rhist{display:flex;flex-wrap:wrap;gap:var(--s1);margin-top:var(--s3);}
.rfall{margin:var(--s3) 0 0;font-size:var(--t-xs);color:var(--ink-3);
  line-height:var(--lh-xs);}
.rfall b{color:var(--neg);font-weight:600;}

/* --- supply lines ----------------------------------------------------- */
.alertbar{padding:var(--s4) var(--s5);margin:var(--s4) 0 var(--s3);
  border-color:var(--neg-line);background:var(--neg-bg);}
.alerthead{color:var(--neg);margin-bottom:var(--s3);}
.alertlist{display:flex;flex-wrap:wrap;gap:var(--s2);}
.alertchip{display:inline-flex;align-items:center;gap:var(--s2);
  text-align:left;cursor:pointer;border-radius:var(--r-md);
  padding:var(--s2) var(--s3);}
.alertchip b{font-size:var(--t-xs);color:var(--ink);font-weight:600;}
.alertchip span{font-size:var(--t-xs);color:var(--ink-3);}
.livedot{width:7px;height:7px;border-radius:50%;flex:none;background:var(--neg);
  box-shadow:0 0 0 3px var(--neg-bg);}
@media (max-width:520px){.alertchip{width:100%;}}
.pkind{color:var(--sem,var(--accent));margin-bottom:var(--s1);}
.comchips{display:flex;flex-wrap:wrap;gap:var(--s1);margin-top:var(--s3);}
.supply{border:0;border-top:1px solid var(--line);background:transparent;
  border-radius:0;margin-top:var(--s5);padding:var(--s4) 0 0;}
.supply:first-of-type{border-top:0;margin-top:var(--s2);padding-top:0;}
.suphead{display:flex;align-items:flex-start;gap:var(--s3);
  margin-bottom:var(--s2);}
.supemoji{font-size:27px;line-height:1.1;flex:none;}
.suphead b{font-family:var(--serif);font-size:var(--t-h3);font-weight:600;
  color:var(--ink);}
.supshare{display:block;font-size:var(--t-xs);color:var(--ink-3);margin-top:2px;}
.episode{border-radius:var(--r-md);padding:var(--s4);margin-bottom:var(--s2);}
.epwhen{color:var(--sem,var(--accent));}
.epwhat{margin:var(--s2) 0 var(--s3);font-size:var(--t-sm);
  line-height:var(--lh-sm);color:var(--ink);}
.eprow{font-size:var(--t-xs);line-height:var(--lh-xs);color:var(--ink-2);
  margin-bottom:var(--s2);}
.eprow b{display:block;color:var(--ink-4);margin-bottom:1px;}
.eplesson{margin-top:var(--s3);padding-top:var(--s3);
  border-top:1px solid var(--line);font-size:var(--t-xs);
  line-height:var(--lh-xs);color:var(--ink);}
.eplesson::before{content:"The pattern · ";font-family:var(--mono);
  font-size:var(--t-label);font-weight:600;letter-spacing:.07em;
  text-transform:uppercase;color:var(--sem,var(--accent));}
.regimes{display:flex;flex-direction:column;gap:var(--s3);}
.regime{padding:var(--s5);}
.regime.on{border-color:var(--accent);
  box-shadow:var(--sh-1),0 0 0 1px var(--accent);}
.rgtop{display:flex;align-items:baseline;justify-content:space-between;
  gap:var(--s3);flex-wrap:wrap;}
.regime .now{color:var(--bg);background:var(--accent);border:0;}
.tell{display:block;font-size:var(--t-xs);color:var(--ink-3);
  margin-top:var(--s2);line-height:var(--lh-xs);}
.tell b{color:var(--ink-2);}
.wl{display:grid;grid-template-columns:1fr 1fr;gap:var(--s2) var(--s5);
  margin:var(--s4) 0 0;}
@media (max-width:640px){.wl{grid-template-columns:1fr;}}
.wl h5{margin:0 0 var(--s2);padding-bottom:var(--s1);
  border-bottom:1px solid var(--line);}
.wl .w h5{color:var(--pos);}
.wl .l h5{color:var(--neg);}
.rgblk{margin-top:var(--s4);}
.rgblk h5{color:var(--ink-4);margin-bottom:var(--s1);}

/* --- learn / patterns page ------------------------------------------- */
.guide{margin:var(--s5) 0 var(--s1);padding:var(--s3) var(--s4);
  background:var(--surface-2);border:1px solid var(--line);
  border-radius:var(--r-md);font-size:var(--t-xs);color:var(--ink-2);}
.guide b{color:var(--ink);}
.guide .flow{color:var(--ink-3);}
.ev .lead,.trig,.triggers{font-size:var(--t-sm);}
.triggers{display:flex;flex-wrap:wrap;gap:var(--s1);margin-top:var(--s2);}
.trig{background:var(--surface-2);border:1px solid var(--line);
  border-radius:var(--r-sm);padding:var(--pad-chip);font-size:var(--t-xs);
  color:var(--ink-3);}

/* the strip at the foot of a news card: confidence, sources, source link */
.card .foot{display:flex;flex-wrap:wrap;gap:var(--s2) var(--s4);
  align-items:center;margin-top:var(--s5);padding-top:var(--s3);
  border-top:1px solid var(--line);font-size:var(--t-xs);color:var(--ink-4);}
.card .foot a{color:var(--accent);text-decoration:none;margin-left:auto;}
.card .foot a:hover{text-decoration:underline;}
.conf{display:inline-flex;align-items:center;gap:var(--s2);}
.conf b{color:var(--ink-3);font-weight:600;}

/* the reason behind a status badge — stated, not implied */
.whynow{border-left:3px solid var(--sem,var(--warn));
  background:var(--sem-bg,var(--warn-bg));border-radius:0 var(--r-md) var(--r-md) 0;
  padding:var(--s4) var(--s5);margin:0 0 var(--s4);
  font-size:var(--t-sm);line-height:var(--lh-sm);color:var(--ink);}
.whynow b{display:block;font-family:var(--mono);font-size:var(--t-label);
  font-weight:600;letter-spacing:.09em;text-transform:uppercase;
  color:var(--sem,var(--warn));margin-bottom:var(--s2);}

/* --- shared notes, accordions, footer -------------------------------- */
.gf-note{padding:var(--s4) var(--s5);color:var(--ink-3);font-size:var(--t-xs);
  line-height:var(--lh-xs);margin:var(--s4) 0 var(--s3);
  border-style:dashed;border-radius:var(--r-md);}
.gf-note b{color:var(--ink-2);}
.freshness{display:block;margin-top:var(--s3);padding-top:var(--s3);
  border-top:1px solid var(--line);}
details.gf-acc{padding:0;}
details.gf-acc>summary{list-style:none;cursor:pointer;display:flex;
  align-items:center;gap:var(--s3);padding:var(--s3) var(--s4);
  border-radius:var(--r-md);font-size:var(--t-xs);font-weight:600;
  color:var(--ink-2);}
details.gf-acc>summary::-webkit-details-marker{display:none;}
details.gf-acc>summary::marker{content:"";font-size:0;}
details.gf-acc>summary .more{font-weight:400;color:var(--ink-4);}
details.gf-acc>summary::after{content:"";flex:none;width:7px;height:7px;
  margin-left:auto;border-right:1.5px solid var(--ink-4);
  border-bottom:1.5px solid var(--ink-4);
  transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s var(--ease);}
details.gf-acc[open]>summary::after{transform:rotate(-135deg) translate(-2px,-2px);}
.acc-body{padding:var(--s1) var(--s4) var(--s4);}
.gf-news a{display:block;color:var(--accent);text-decoration:none;
  font-size:var(--t-xs);padding:var(--s1) 0;line-height:1.45;}
.gf-news a:hover{text-decoration:underline;}
.disclaimer{background:var(--well);border:1px dashed var(--line-2);
  border-radius:var(--r-md);padding:var(--s4) var(--s5);color:var(--ink-3);
  font-size:var(--t-xs);margin-top:var(--s7);}
.disclaimer b{color:var(--ink-2);}
.pagefoot{margin-top:var(--s7);padding-top:var(--s5);
  border-top:1px solid var(--line);color:var(--ink-4);font-size:var(--t-xs);}
.archive{margin-bottom:var(--s3);}
.archive b{color:var(--ink-3);}
.archive a{color:var(--accent);text-decoration:none;
  margin:0 var(--s3) var(--s2) 0;display:inline-block;}
.archive a:hover{text-decoration:underline;}

/* --- glossary terms: the tooltip is a fixed layer, never clipped ------ */
.term{border-bottom:1.5px dotted var(--ink-4);cursor:help;color:inherit;
  transition:border-color .15s var(--ease),color .15s var(--ease);}
.term:hover,.term:focus{border-bottom-color:var(--accent);color:var(--accent);
  outline:none;}
#tipbox{position:fixed;z-index:9999;max-width:300px;pointer-events:none;
  opacity:0;visibility:hidden;transform:translateY(-3px);
  background:var(--tip-bg);color:var(--tip-ink);border:1px solid var(--line-2);
  font-family:var(--sans);font-size:var(--t-xs);line-height:1.5;font-weight:400;
  padding:var(--s3) var(--s4);border-radius:var(--r-md);box-shadow:var(--sh-3);
  transition:opacity .15s var(--ease),transform .15s var(--ease);}
#tipbox.on{opacity:1;visibility:visible;transform:none;}

/* ------------------------------------------------- 12 MOTION */
@keyframes rise{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
@keyframes grow{from{transform:scaleX(0);}to{transform:scaleX(1);}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 3px var(--neg-bg);}
  50%{box-shadow:0 0 0 7px color-mix(in srgb,var(--neg) 16%,transparent);}}
.card,.histcard,.gauge,.regime,.rec{animation:rise .5s var(--ease) both;}
.card:nth-of-type(1){animation-delay:.02s}
.card:nth-of-type(2){animation-delay:.06s}
.card:nth-of-type(3){animation-delay:.10s}
.card:nth-of-type(n+4){animation-delay:.14s}
.secbar span,.erow .fill{transform-origin:left center;
  animation:grow .7s var(--ease) both .15s;}
.erow .fill.neg{transform-origin:right center;}
.livedot{animation:pulse 2.4s ease-in-out infinite;}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition-duration:.01ms!important;}
}

"""

# One event card (used by web + email). `gloss` and `dots` are Jinja filters.
# ---------------------------------------------------------------------------
# Shared behaviour for the tap-to-define labels. The tooltip is a ::after on
# .term, so CSS cannot know how much room is left inside the detail panel —
# this measures it and flips the tooltip to right-anchored when it would be
# clipped. Included by the two data pages, which have narrow panels.
# ---------------------------------------------------------------------------
TIP_FIT_JS = ""


# ---------------------------------------------------------------------------
# Light / dark toggle, shared by every page. THEME_BOOT runs in <head> before
# the body paints so a stored choice never flashes the wrong colours first.
# ---------------------------------------------------------------------------
THEME_BOOT = ""

THEME_BTN = ""

# ---------------------------------------------------------------------------
# Glossary tooltips. Rendered into a single fixed element appended to <body>
# rather than an ::after on each term: the detail panels and the calendar are
# scroll containers, and an absolutely-positioned child of one gets clipped at
# its edge. A fixed layer cannot be clipped by anything, and it can flip above
# the term when there is no room below.
# ---------------------------------------------------------------------------
THEME_JS = """
(function(){
  if(window.__tipbox)return; window.__tipbox=1;
  var box=document.createElement('div');
  box.id='tipbox'; box.setAttribute('role','tooltip');
  document.body.appendChild(box);
  var cur=null;
  function show(t){
    var d=t.getAttribute('data-def'); if(!d)return;
    box.textContent=d;
    var w=Math.min(300,window.innerWidth-24);
    box.style.maxWidth=w+'px';
    box.classList.add('on');
    var r=t.getBoundingClientRect(), h=box.offsetHeight;
    var left=Math.min(Math.max(12,r.left),window.innerWidth-w-12);
    var top=r.bottom+8;
    if(top+h>window.innerHeight-12){top=r.top-h-8;}
    box.style.left=left+'px';
    box.style.top=Math.max(12,top)+'px';
    cur=t;
  }
  function hide(){box.classList.remove('on');cur=null;}
  document.addEventListener('pointerover',function(e){
    var t=e.target.closest&&e.target.closest('.term');
    if(t){show(t);}else if(cur){hide();}
  },true);
  document.addEventListener('focusin',function(e){
    var t=e.target.closest&&e.target.closest('.term');
    if(t){show(t);}else{hide();}
  },true);
  document.addEventListener('scroll',hide,true);
  window.addEventListener('resize',hide);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')hide();});
})();
"""


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

  {% if ev.analysis.the_story %}
    <div class="blocklabel">What the article actually says</div>
    <ul class="story">
      {% for point in ev.analysis.the_story %}<li>{{ point|gloss }}</li>{% endfor %}
    </ul>
    {% if ev.article_url %}
      <a class="readsrc" href="{{ ev.article_url }}" target="_blank" rel="noopener">Read the full article →</a>
    {% endif %}
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
          <span class="plevel">{{ im.probability|dots }}<span class="lvl">{{ im.probability }}</span></span>
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
<title>{{ brief.date_human }} — India Impact Brief</title>
<meta name="description" content="What happened in the world today and how it reaches Indian inflation, the rupee, sectors and gold — in plain language.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
{{ icon }}{{ themeboot }}
<style>{{ css }}</style>
</head><body class="page-news"><div class="wrap">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <div class="brandrow">{{ logo }}<h1>The India Impact Brief</h1></div>
  {{ themebtn }}
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

{% if brief.history %}
<div class="section">Pattern from history</div>
<article class="histcard">
  <div class="hkick">{{ brief.history.when }} · {{ brief.history.where }}</div>
  <h3>{{ brief.history.title }}</h3>
  <p class="hlede">{{ brief.history.what }}</p>
  <ol class="hchain">
    <li><h5>Why it happened</h5><p>{{ brief.history.why|gloss }}</p></li>
    <li><h5>What it hit</h5><p>{{ brief.history.impact|gloss }}</p></li>
    <li><h5>The policy brought in to fix it</h5><p>{{ brief.history.policy|gloss }}</p></li>
    <li><h5>And what that policy led to</h5><p>{{ brief.history.consequence|gloss }}</p></li>
  </ol>
  <div class="hpattern"><b>The pattern to remember</b>{{ brief.history.pattern|gloss }}</div>
  {% if brief.history.india_echo %}
  <div class="hindia"><b>The India echo</b>{{ brief.history.india_echo|gloss }}</div>
  {% endif %}
  {% if brief.history.watch_for %}
  <div class="hwatch"><b>The modern tell</b>{{ brief.history.watch_for|gloss }}</div>
  {% endif %}
</article>
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

<script>{{ themejs }}</script>
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
{{ icon }}{{ themeboot }}
<style>{{ css }}</style>
</head><body class="page-learn"><div class="wrap">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <div class="brandrow">{{ logo }}<h1>The Pattern Library</h1></div>
  {{ themebtn }}
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
          <span class="plevel">{{ im.probability|dots }}<span class="lvl">{{ im.probability }}</span></span>
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

<script>{{ themejs }}</script>
</div></body></html>
"""


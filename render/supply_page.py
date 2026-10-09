"""
render/supply_page.py — the Supply Lines page.

A map of where the world's essentials come from and the narrow places they
travel through, with today's news raising alerts on top of it.

The reader's path is meant to be: see what is red -> click it -> understand who
depends on it, what could break it, what that does to prices, what it means for
India, and when it has happened before.
"""

SUPPLY_PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Supply Lines — India Impact Brief</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
{{ icon }}{{ themeboot }}
<style>{{ css }}</style>
</head><body class="page-supply"><div class="wrap wide">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <div class="brandrow">{{ logo }}<h1>Supply Lines</h1></div>
  {{ themebtn }}
  <div class="date">Where the things you buy actually come from, and what could
    interrupt them — because almost every price rise starts as a problem
    somewhere else · <span class="engine">updated {{ s.updated_human }}</span></div>
</header>

{{ nav }}

<div class="gf-switch" role="tablist">
  <button id="sw-map" class="on" role="tab">The map</button>
  <button id="sw-learn" role="tab">How a shock reaches you</button>
</div>

<!-- ==================== VIEW 1: THE MAP ==================== -->
<section id="view-map" class="gf-view">
  <details class="gf-note gf-acc">
    <summary>What this page is for
      <span class="more">· and which parts are live</span></summary>
    <div class="acc-body">
      Two things cause most price shocks: a country that supplies a large share of
      something stops, or a narrow stretch of water that most of it travels through
      closes. This map shows both. A country appears here only if it produces enough
      of something — roughly
      <span class="term" tabindex="0" role="button" data-def="Below about 15% of world output, other producers can usually cover a problem without the price moving much. Above it, there is no spare capacity to absorb a failure, so the whole world feels it.">15% of world output</span>
      — that the world notices when it stumbles. A few qualify on
      <span class="term" tabindex="0" role="button" data-def="Some countries grow a modest share of a crop but export most of it, which makes them far more important to the world market than their production share suggests. Kenya grows about 8% of the world's tea and supplies a quarter of all tea traded. Nigeria is included for the grade of its crude rather than the volume.">exports rather than production</span>,
      which is often what actually matters.
      <span class="freshness"><b>Live every morning:</b> the alert colours. Each
      morning's news is matched against every commodity and route on this map, so a
      disruption shows up the day it is reported{% if s.stats.live_today %} —
      <b>{{ s.stats.live_today }} of today's alerts came from today's news</b>{% endif %}.
      An alert never clears itself on a quiet news day; only a deliberate edit does
      that, because silence is not the same as resolution.
      <b>Hand-curated:</b> production shares, who depends on whom, and the historical
      episodes — last reviewed <b>{{ s.as_of }}</b>.</span>
    </div>
  </details>

  {% if s.alerts %}
  <div class="alertbar">
    <div class="alerthead">⚠ Happening now · {{ s.alerts|length }}</div>
    <div class="alertlist">
      {% for a in s.alerts %}
      <button class="alertchip" data-kind="{{ a.kind }}" data-id="{{ a.id }}" type="button">
        <b>{{ a.name }}</b><span>{{ a.what }}</span>
        {% if a.live %}<i class="livedot" title="Raised by today's news"></i>{% endif %}
      </button>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <div class="maplegend">
    <span class="lg st-calm"><span class="sw"></span>Running normally</span>
    <span class="lg st-watch"><span class="sw"></span>Worth watching</span>
    <span class="lg st-alert"><span class="sw"></span>Disrupted now</span>
    <span class="hintx">Emojis show what a country supplies the world · lines are
      shipping routes · click anything</span>
  </div>

  <div class="map-wrap">
    <svg id="smap" viewBox="0 0 1000 500" role="img" aria-label="World supply map">
      <g id="smapg">
        {% for c in map_countries %}<path class="cty {{ c.cls }}" d="{{ c.d }}"{% if c.code %} data-kind="country" data-id="{{ c.code }}"{% endif %}></path>{% endfor %}
        {% for r in map_routes %}
        <polyline class="route {{ r.cls }}" points="{{ r.points }}" data-kind="route" data-id="{{ r.id }}"></polyline>
        <polyline class="routehit" points="{{ r.points }}" data-kind="route" data-id="{{ r.id }}"></polyline>
        {% endfor %}
        {% for r in map_routes %}
        <text class="rlabel {{ r.cls }}" x="{{ r.lx }}" y="{{ r.ly }}" data-kind="route" data-id="{{ r.id }}">{{ r.short }}</text>
        {% endfor %}
        {% for m in map_marks %}
        <g class="mark {{ m.cls }}" data-kind="country" data-id="{{ m.code }}">
          <rect x="{{ m.x }}" y="{{ m.y }}" width="{{ m.w }}" height="{{ m.h }}" rx="9"></rect>
          <text x="{{ m.cx }}" y="{{ m.cy }}"><tspan class="em">{{ m.emojis }}</tspan>{% if m.more %}<tspan class="more" dx="2">{{ m.more }}</tspan>{% endif %}</text>
        </g>
        {% endfor %}
      </g>
    </svg>
    <div class="mapctl">
      <button id="szin" title="Zoom in">+</button>
      <button id="szout" title="Zoom out">−</button>
      <button id="szres" title="Reset view" style="font-size:12px">⤢</button>
    </div>
    <div class="maptip" id="stip"></div>
  </div>

  <div class="gf-grid">
    <div class="sllist">
      <div class="slhead">Shipping routes</div>
      {% for r in s.routes %}
      <button class="slrow st-{{ r.status }}" data-kind="route" data-id="{{ r.id }}" type="button">
        <span class="sldot"></span>
        <span class="sltext"><b>{{ r.name }}</b><em>{{ r.headline }}</em></span>
        <span class="slemoji">{% for c in r.carries_detail %}{{ c.emoji }}{% endfor %}</span>
      </button>
      {% endfor %}
      <div class="slhead">Countries the world depends on</div>
      {% for c in s.countries %}
      <button class="slrow st-{{ c.status }}" data-kind="country" data-id="{{ c.code }}" type="button">
        <span class="sldot"></span>
        <span class="sltext"><b>{{ c.name }}</b><em>{% for sup in c.supplies %}{{ sup.info.name }}{{ ", " if not loop.last }}{% endfor %}</em></span>
        <span class="slemoji">{% for e in c.emojis %}{{ e }}{% endfor %}</span>
      </button>
      {% endfor %}
    </div>
    <div class="gf-panelwrap">
      <div class="panel" id="spanel">
        <p class="hint">Pick a country or a shipping route — on the map or in the list —
        to see who depends on it, what could break it, what that would do to prices
        here, and the last time it actually happened.</p>
      </div>
    </div>
  </div>
</section>

<!-- ============ VIEW 2: HOW A SHOCK REACHES YOU ============ -->
<section id="view-learn" class="gf-view" hidden>
  <div class="gf-note">
    <b>The whole point of this page in one page.</b> A price rise almost never
    starts in your shop. It starts somewhere else, travels along a known path, and
    arrives weeks or months later. Once you can see the path, the news stops being
    random events and starts being a system you recognise.
  </div>

  <div class="section">The five steps, every time</div>
  <ol class="hchain">
    <li><h5>1 · Something interrupts supply</h5><p>A drought, a strike, an export
      ban, an attack on shipping, a drone hitting a processing plant. Note how
      often it is a decision rather than a disaster — governments protecting their
      own consumers cause as many shortages as weather does.</p></li>
    <li><h5>2 · Buyers discover there is no spare</h5><p>This is the step that
      decides whether it matters. If other producers have slack, the price barely
      moves. If one country holds most of the supply, there is nothing to switch to
      and the price has to do the rationing instead.</p></li>
    <li><h5>3 · The price rises to force someone to go without</h5><p>A price is
      not a punishment, it is a rationing device. It climbs until enough buyers
      drop out that supply and demand match again. For something nobody can give up
      — cooking oil, diesel, bread — it has to climb a very long way.</p></li>
    <li><h5>4 · It spreads to substitutes and neighbours</h5><p>Palm oil rises, so
      buyers switch to sunflower and soy, so those rise too. Expensive gas means
      expensive fertiliser, which means a smaller harvest next season. The second
      wave is usually bigger and slower than the first.</p></li>
    <li><h5>5 · It reaches India, and then your month</h5><p>A higher import bill
      widens the trade gap, which weakens the rupee, which makes every import dearer
      still. Inflation rises, so the RBI cannot cut interest rates, so loans stay
      expensive. A drought in West Africa ends up in your EMI.</p></li>
  </ol>

  <div class="section">Why shares of world supply matter more than size</div>
  <div class="gf-note">
    A country producing 5% of something is interesting. A country producing 40% is a
    systemic risk, because nobody can replace it. That is the only reason the 15%
    threshold on this map exists — below it the world has options, above it the world
    has a problem. It is also why
    <span class="term" tabindex="0" role="button" data-def="Spare capacity is production that exists but is switched off, and can be turned on within weeks. Saudi Arabia holds most of the world's spare oil capacity. It is the difference between a supply loss being a headline and being a crisis.">spare capacity</span>
    is the most important number in commodities that almost nobody follows.
  </div>

  <div class="section">What to watch, in order of how fast it bites</div>
  <div class="qrows">
    <div class="qrow"><span class="qk">Within days</span><span class="qv">War-risk
      insurance premiums for a shipping route. These move before any ship is stopped,
      and they are what actually reroutes trade.</span></div>
    <div class="qrow"><span class="qk">Within weeks</span><span class="qv">Export
      bans and levies announced by producing countries. Almost always triggered by
      domestic price protests, so unrest in a producing country is the early warning.</span></div>
    <div class="qrow"><span class="qk">Within months</span><span class="qv">Freight
      rates and shipping times. A longer route removes capacity from the world fleet
      and raises costs on routes that were never disrupted.</span></div>
    <div class="qrow"><span class="qk">Next season</span><span class="qv">Fertiliser
      prices. Expensive fertiliser now is a smaller harvest later — the slowest and
      most underestimated chain on this page.</span></div>
    <div class="qrow"><span class="qk">Next decade</span><span class="qv">Mine and
      chip plant investment. Both take 5-15 years, so today's under-investment is a
      shortage that is already locked in.</span></div>
  </div>

  <div class="gf-note">{{ s.note }}</div>
</section>

<div class="disclaimer">
  <b>Learning tool, not advice.</b> Production shares are curated, rounded estimates
  meant to teach proportion, and the historical accounts are summaries. Alert states
  are generated by matching news headlines to keywords, so they can both miss things
  and over-flag them. Nothing here is a recommendation to buy or sell anything.
</div>

<footer class="pagefoot">
  <div class="archive"><a href="index.html">← Back to today's brief</a>
    <a href="assets.html">What you can invest in →</a></div>
  <p>News Finance Hub · Supply Lines</p>
</footer>

<script>{{ tipjs }}{{ themejs }}
var SL = {{ s_json }};
(function(){
  var $=function(id){return document.getElementById(id);};
  function esc(s){var d=document.createElement('div');d.textContent=(s==null?'':String(s));return d.innerHTML;}
  var STATUS={calm:'Running normally',watch:'Worth watching',alert:'Disrupted now'};
  var cur=null;

  function view(v){
    $('view-map').hidden=!v; $('view-learn').hidden=v;
    $('sw-map').classList.toggle('on',v); $('sw-learn').classList.toggle('on',!v);
  }
  $('sw-map').onclick=function(){view(true);};
  $('sw-learn').onclick=function(){view(false);};

  function tdef(label,def){
    if(!def)return esc(label);
    return '<span class="term" tabindex="0" role="button" aria-label="'+esc(def)+'" '
      +'data-def="'+esc(def)+'">'+esc(label)+'</span>';
  }
  function block(title,inner){return inner?'<div class="pblock"><h4>'+title+'</h4>'+inner+'</div>':'';}
  /* A status badge is a claim. This is the evidence for it, placed before
     anything else so "Disrupted now" is never just a colour. */
  function whyNow(rec){
    if(!rec.why_now||rec.status==='calm')return '';
    var head=rec.status==='alert'?'Why it is disrupted right now'
                                 :'Why this is worth watching right now';
    return '<div class="whynow st-'+rec.status+'"><b>'+esc(head)+'</b>'
      +esc(rec.why_now)+'</div>';
  }
  function list(arr,cls){if(!arr||!arr.length)return '';
    return '<ul class="plist '+(cls||'')+'">'+arr.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';}
  function pill(st){return '<span class="stpill st-'+st+'">'+esc(STATUS[st]||st)+'</span>';}
  function newsBlock(news){
    if(!news||!news.length)return '';
    return block('In today\\u2019s news','<div class="gf-news">'+news.map(function(n){
      return '<a href="'+esc(n.url)+'" target="_blank" rel="noopener">'+esc(n.title)+'</a>';
    }).join('')+'</div>');
  }
  /* The same five-part story for every past episode, so the shape becomes familiar. */
  function history(items){
    if(!items||!items.length)return '';
    return block('When this happened before', items.map(function(h){
      return '<div class="episode"><div class="epwhen">'+esc(h.when)+'</div>'
        +'<p class="epwhat">'+esc(h.what)+'</p>'
        +'<div class="eprow"><b>Why it happened</b>'+esc(h.why)+'</div>'
        +'<div class="eprow"><b>How long it lasted</b>'+esc(h.how_long)+'</div>'
        +'<div class="eprow"><b>What was done about it</b>'+esc(h.response)+'</div>'
        +'<div class="eplesson">'+esc(h.lesson)+'</div></div>';
    }).join(''));
  }

  function showRoute(id,scroll){
    var r=null,i;
    for(i=0;i<SL.routes.length;i++){if(SL.routes[i].id===id)r=SL.routes[i];}
    if(!r)return; cur='route:'+id;
    var carries=(r.carries_detail||[]).map(function(c){
      return '<span class="comchip">'+esc(c.emoji)+' '+esc(c.name)+'</span>';
    }).join('');
    var deps=(r.carries_detail||[]).map(function(c){
      return '<div class="qrow"><span class="qk">'+esc(c.emoji)+' '+esc(c.name)
        +'</span><span class="qv">'+esc(c.everyday)+'</span></div>';
    }).join('');

    $('spanel').className='panel st-'+r.status;
    $('spanel').innerHTML='<div class="pkind">Shipping route</div>'
      +'<h3>'+esc(r.name)+pill(r.status)+'</h3>'
      +'<div class="sub">'+esc(r.region)+'</div>'
      +'<div class="verdict"><b>Why it matters</b>'+esc(r.headline)+'</div>'
      +whyNow(r)
      +newsBlock(r.news)
      +block('How much goes through','<p class="pnote">'+esc(r.volume)+'</p>'
        +(carries?'<div class="comchips">'+carries+'</div>':'')
        +(deps?'<div class="qrows">'+deps+'</div>':''))
      +block('Why there is no easy way around it','<p class="pnote">'+esc(r.why_it_matters)+'</p>')
      +block('What happens if it closes','<p class="pnote">'+esc(r.if_blocked)+'</p>')
      +block('What it means for India','<div class="gf-india">'+esc(r.india)+'</div>')
      +block('The alternatives','<p class="pnote">'+esc(r.alternatives)+'</p>')
      +block('What to watch',list(r.watch))
      +history(r.history);
    mark('route',id,scroll);
  }

  function showCountry(code,scroll){
    var c=null,i;
    for(i=0;i<SL.countries.length;i++){if(SL.countries[i].code===code)c=SL.countries[i];}
    if(!c)return; cur='country:'+code;

    var body=(c.supplies||[]).map(function(s){
      var info=s.info||{};
      var deps=(s.dependents||[]).map(function(d){
        return '<div class="qrow"><span class="qk">'+esc(d.who)+'</span>'
          +'<span class="qv">'+esc(d.detail)+'</span></div>';
      }).join('');
      return '<div class="supply st-'+s.status+'">'
        +'<div class="suphead"><span class="supemoji">'+esc(info.emoji||'')+'</span>'
        +'<div><b>'+esc(info.name||s.commodity)+'</b>'+pill(s.status)
        +'<span class="supshare">'+esc(s.share)+' · '+esc(s.rank)+'</span></div></div>'
        +'<p class="explain"><b>What this turns into in your life.</b> '+esc(info.everyday||'')+'</p>'
        +whyNow(s)
        +newsBlock(s.news)
        +block('What is actually going on here','<p class="pnote">'+esc(s.what)+'</p>')
        +block('Who depends on it',(deps?'<div class="qrows">'+deps+'</div>':''))
        +block('What could break it',list(s.risks,'bad'))
        +block('What happens to prices if it does','<p class="pnote">'+esc(s.if_disrupted)+'</p>')
        +block('What it means for India','<div class="gf-india">'+esc(s.india)+'</div>')
        +history(s.history)
        +'</div>';
    }).join('');

    $('spanel').className='panel st-'+c.status;
    $('spanel').innerHTML='<div class="pkind">Producer country</div>'
      +'<h3>'+esc(c.name)+pill(c.status)+'</h3>'
      +'<div class="sub">Supplies the world with '
      +(c.supplies||[]).map(function(s){return esc((s.info||{}).name||'');}).join(', ')+'</div>'
      +body;
    mark('country',code,scroll);
  }

  function show(kind,id,scroll){
    if(kind==='route')showRoute(id,scroll); else showCountry(id,scroll);
  }

  function mark(kind,id,scroll){
    var key=kind+':'+id;
    var nodes=document.querySelectorAll('[data-kind]');
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      n.classList.toggle('sel',
        n.getAttribute('data-kind')+':'+n.getAttribute('data-id')===key);
    }
    if(scroll&&window.innerWidth<=900){$('spanel').scrollIntoView({behavior:'smooth',block:'start'});}
  }

  /* Size each marker to the text the browser actually drew. Emoji are wider
     than their font-size and by different amounts on different platforms, so
     a width computed on the server is always wrong somewhere. */
  function sizeMarkers(){
    var marks=document.querySelectorAll('#smap .mark');
    for(var i=0;i<marks.length;i++){
      var g=marks[i],t=g.querySelector('text'),r=g.querySelector('rect');
      if(!t||!r)continue;
      var b;
      try{b=t.getBBox();}catch(e){continue;}
      if(!b||!b.width)continue;
      var padX=7,h=Math.max(b.height+5,17);
      var w=b.width+padX*2;
      r.setAttribute('x',(b.x-padX).toFixed(1));
      r.setAttribute('y',(b.y-(h-b.height)/2).toFixed(1));
      r.setAttribute('width',w.toFixed(1));
      r.setAttribute('height',h.toFixed(1));
      r.setAttribute('rx',(h/2).toFixed(1));
    }
  }
  /* Zooming rescales the marker font, so the pills need re-measuring —
     debounced, because a wheel gesture fires this many times a second. */
  var sizeT=null;
  function resize(){clearTimeout(sizeT);sizeT=setTimeout(sizeMarkers,90);}

  /* Emoji fonts can load late, which changes the measurement. */
  sizeMarkers();
  if(document.fonts&&document.fonts.ready){document.fonts.ready.then(sizeMarkers);}
  window.addEventListener('load',sizeMarkers);
  window.addEventListener('resize',resize);

  /* ---------- map: hover, click, zoom, pan ---------- */
  var svg=$('smap'),tip=$('stip'),VB={x:0,y:0,w:1000,h:500};
  function applyVB(){svg.setAttribute('viewBox',VB.x+' '+VB.y+' '+VB.w+' '+VB.h);}
  function clampVB(){
    VB.x=Math.max(-60,Math.min(1000-VB.w+60,VB.x));
    VB.y=Math.max(-40,Math.min(500-VB.h+40,VB.y));
  }
  function zoom(f,cx,cy){
    var nw=Math.max(140,Math.min(1000,VB.w*f)),nh=nw/2;
    if(cx==null){cx=VB.x+VB.w/2;cy=VB.y+VB.h/2;}
    VB.x=cx-(cx-VB.x)*(nw/VB.w);VB.y=cy-(cy-VB.y)*(nh/VB.h);
    VB.w=nw;VB.h=nh;clampVB();applyVB();
    /* keep markers and labels legible as the map scales */
    svg.style.setProperty('--mz',(VB.w/1000).toFixed(3));
    resize();
  }
  function svgPt(e){
    var r=svg.getBoundingClientRect();
    return {x:VB.x+(e.clientX-r.left)/r.width*VB.w, y:VB.y+(e.clientY-r.top)/r.height*VB.h};
  }
  $('szin').onclick=function(){zoom(0.7);};
  $('szout').onclick=function(){zoom(1.4);};
  $('szres').onclick=function(){VB={x:0,y:0,w:1000,h:500};applyVB();svg.style.setProperty('--mz','1');resize();};
  svg.addEventListener('wheel',function(e){e.preventDefault();var p=svgPt(e);zoom(e.deltaY>0?1.18:0.85,p.x,p.y);},{passive:false});
  var drag=false,last=null,moved=false;
  svg.addEventListener('pointerdown',function(e){drag=true;moved=false;last=svgPt(e);svg.classList.add('drag');});
  svg.addEventListener('pointerup',function(){drag=false;svg.classList.remove('drag');});
  svg.addEventListener('pointerleave',function(){drag=false;svg.classList.remove('drag');tip.classList.remove('on');});
  svg.addEventListener('pointermove',function(e){
    if(drag&&last){
      var p=svgPt(e),dx=p.x-last.x,dy=p.y-last.y;
      if(Math.abs(dx)>1||Math.abs(dy)>1){moved=true;}
      VB.x-=dx;VB.y-=dy;clampVB();applyVB();tip.classList.remove('on');return;
    }
    var t=e.target.closest?e.target.closest('[data-kind]'):null;
    if(t){
      var kind=t.getAttribute('data-kind'),id=t.getAttribute('data-id'),label='',sub='';
      if(kind==='route'){
        for(var i=0;i<SL.routes.length;i++)if(SL.routes[i].id===id){
          label=SL.routes[i].name;sub=SL.routes[i].headline;}
      }else{
        for(var j=0;j<SL.countries.length;j++)if(SL.countries[j].code===id){
          label=SL.countries[j].name;
          sub=SL.countries[j].supplies.map(function(s){
            return (s.info||{}).emoji+' '+((s.info||{}).name||'');}).join(' · ');}
      }
      if(label){
        var r2=svg.parentNode.getBoundingClientRect();
        tip.innerHTML='<b>'+esc(label)+'</b><span class="wrapline">'+esc(sub)+'</span>';
        tip.style.left=Math.min(e.clientX-r2.left+14,r2.width-230)+'px';
        tip.style.top=(e.clientY-r2.top+14)+'px';
        tip.classList.add('on');
        return;
      }
    }
    tip.classList.remove('on');
  });

  document.addEventListener('click',function(e){
    if(moved){moved=false;return;}
    var t=e.target.closest('[data-kind]');
    if(t){show(t.getAttribute('data-kind'),t.getAttribute('data-id'),true);}
  });

  /* Open on whatever is actually wrong today, else on Hormuz. */
  if(SL.alerts&&SL.alerts.length){show(SL.alerts[0].kind,SL.alerts[0].id,false);}
  else{showRoute('hormuz',false);}
})();
</script>
</div></body></html>
"""

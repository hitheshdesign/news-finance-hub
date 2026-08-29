"""
render/global_page.py — the Global Finance page template.

Two views behind one switch:
  * Country valuations — a real choropleth world map (zoom/pan/click) plus a
    sortable table and a rich, sticky detail panel per country.
  * Market movers' money — an interactive heat-map of where money rotated in
    each period (gold included), with the story behind each shift.

Kept in its own module because it carries a fair amount of inline JS.
"""

GLOBAL_PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Global Finance — India Impact Brief</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
<style>{{ css }}</style>
</head><body><div class="wrap">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <h1>Global Finance</h1>
  <div class="date">Where the world's markets are cheap or expensive, and where the
    big money has been moving · <span class="engine">updated {{ g.updated_human }}</span></div>
</header>

{{ nav }}

<div class="gf-switch" role="tablist">
  <button id="sw-val" class="on" role="tab">Country valuations</button>
  <button id="sw-mov" role="tab">Market movers' money</button>
</div>

<!-- ==================== VIEW 1: VALUATIONS ==================== -->
<section id="view-val" class="gf-view">
  <div class="gf-note">
    <b>Indicative &amp; educational — not trading advice.</b> Colours show how each market is
    priced on
    <span class="term" tabindex="0" role="button" data-def="Cyclically-Adjusted PE: a market's price divided by its average inflation-adjusted earnings over 10 years. Compared with its OWN long-run average, it shows whether a market is dear or cheap.">CAPE</span>
    versus its own long-run average. Curated data, refreshed periodically; the news inside each
    country is live from today's brief.
  </div>

  <div class="gf-legend">
    <span class="lg v-cheap"><span class="sw"></span>Cheap · {{ g.stats.cheap }}</span>
    <span class="lg v-fair"><span class="sw"></span>Fair · {{ g.stats.fair }}</span>
    <span class="lg v-exp"><span class="sw"></span>Expensive · {{ g.stats.expensive }}</span>
    <span class="hintx">Click a country · scroll to zoom · drag to pan</span>
  </div>

  <div class="map-wrap">
    <svg id="map" viewBox="0 0 1000 500" role="img" aria-label="World valuation map">
      <g id="mapg">
        {% for c in map_countries %}<path class="cty {{ c.cls }}" d="{{ c.d }}"{% if c.code %} data-code="{{ c.code }}"{% endif %}></path>{% endfor %}
        {% for d in map_dots %}<circle class="cty has {{ d.cls }}" data-code="{{ d.code }}" cx="{{ d.x }}" cy="{{ d.y }}" r="4.5"></circle>{% endfor %}
      </g>
    </svg>
    <div class="mapctl">
      <button id="zin" title="Zoom in">+</button>
      <button id="zout" title="Zoom out">−</button>
      <button id="zres" title="Reset view" style="font-size:12px">⤢</button>
    </div>
    <div class="maptip" id="tip"></div>
  </div>

  <div class="gf-grid">
    <div class="ctable" id="ctable">
      <div class="thead">
        <span class="c-name" data-sort="name">Market</span>
        <span class="c-val" data-sort="valuation">Priced</span>
        <span class="c-cape sorted" data-sort="cape">CAPE</span>
        <span class="c-er" data-sort="er">Est. ₹ ret.</span>
      </div>
      <div id="crows"></div>
    </div>
    <div class="gf-panelwrap">
      <div class="panel" id="panel">
        <p class="hint">Pick a country on the map or in the table to see what you would be
        paying, what you might get back in rupees, and what could go wrong.</p>
      </div>
    </div>
  </div>
</section>

<!-- ==================== VIEW 2: MARKET MOVERS ==================== -->
<section id="view-mov" class="gf-view" hidden>
  <div class="rot-now">
    <span class="mood">Right now · mood: {{ g.current.mood_today or g.current.mood }}</span>
    <p>{{ g.current.summary }}</p>
  </div>

  <div class="gf-note">
    <b>How to read the grid.</b> Each column is a period, each row an asset. Green = money
    flowing in (that asset was winning); red = money leaving. Watch the <b>Gold</b> row — it
    turns green almost every time the world gets scared. Hover any square for the story.
  </div>

  <div class="heatwrap">
    <table class="heat">
      <thead><tr><th></th>{% for p in g.rotation %}<th class="per">{{ p.period }}</th>{% endfor %}</tr></thead>
      <tbody>
        {% for b in g.buckets %}
        <tr>
          <th class="rowlbl {{ 'gold' if b.key=='GOLD' }}">{{ b.label }}</th>
          {% for p in g.rotation %}
          <td class="{{ p.cls[b.key] }}" data-p="{{ loop.index0 }}" data-b="{{ b.label }}"></td>
          {% endfor %}
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <div class="heatlegend">
      <span class="sc"><i class="box s2"></i>Money piling in</span>
      <span class="sc"><i class="box s1"></i>Favoured</span>
      <span class="sc"><i class="box s0"></i>Neutral</span>
      <span class="sc"><i class="box sm1"></i>Out of favour</span>
      <span class="sc"><i class="box sm2"></i>Heavily sold</span>
    </div>
    <div class="maptip" id="htip"></div>
  </div>

  <div class="section">The story behind each shift</div>
  <ul class="rot">
    {% for p in g.rotation %}
    <li class="{{ 'hl' if p.gold_spike }}">
      <span class="per">{{ p.period }}</span>
      <span class="mood-tag {{ 'mood-on' if p.mood=='risk-on' else 'mood-off' if p.mood=='risk-off' else 'mood-mixed' }}">{{ p.mood }}</span>
      <div class="flows">
        {% for x in p.into %}<span class="into {{ 'gold' if 'Gold' in x }}">▲ {{ x }}</span>{% endfor %}
        {% for x in p.out_of %}<span class="outof">▼ {{ x }}</span>{% endfor %}
      </div>
      <div class="rwhy">{{ p.why }}</div>
    </li>
    {% endfor %}
  </ul>
  <div class="gf-note">{{ g.note }}</div>
</section>

<div class="disclaimer">
  <b>Learning tool, not advice.</b> Valuations are curated, indicative estimates (refreshed
  periodically) and the money-movement view is an educational reading of market history, not
  precise fund-flow data. Nothing here is a recommendation to buy or sell anything.
</div>

<footer class="pagefoot">
  <div class="archive"><a href="index.html">← Back to today's brief</a></div>
  <p>News Finance Hub · Global Finance</p>
</footer>

<script>
var GF = {{ g_json }};
var ROT = {{ rot_json }};
(function(){
  var $=function(id){return document.getElementById(id);};
  function esc(s){var d=document.createElement('div');d.textContent=(s==null?'':String(s));return d.innerHTML;}
  var VC={cheap:'v-cheap',fair:'v-fair',expensive:'v-exp'};
  var order=Object.keys(GF), sortKey='cape', sortAsc=true, cur=null;

  /* ---------- view switch ---------- */
  function view(v){
    $('view-val').hidden=!v; $('view-mov').hidden=v;
    $('sw-val').classList.toggle('on',v); $('sw-mov').classList.toggle('on',!v);
  }
  $('sw-val').onclick=function(){view(true);};
  $('sw-mov').onclick=function(){view(false);};

  /* ---------- helpers ---------- */
  function erRow(label,val,total){
    var MAX=12,w=Math.min(Math.abs(val)/MAX,1)*50,cls=val>=0?'pos':'neg';
    var style=val>=0?('left:50%;width:'+w+'%'):('right:50%;width:'+w+'%');
    return '<div class="erow'+(total?' total':'')+'"><span class="lbl">'+esc(label)+'</span>'
      +'<span class="track"><span class="fill '+cls+'" style="'+style+'"></span></span>'
      +'<span class="num">'+(val>0?'+':'')+val.toFixed(1)+'%</span></div>';
  }
  function block(title,inner){return inner?'<div class="pblock"><h4>'+title+'</h4>'+inner+'</div>':'';}
  function list(arr,cls){if(!arr||!arr.length)return '';
    return '<ul class="plist '+(cls||'')+'">'+arr.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';}
  function erTotal(c){return (c.er_growth||0)+(c.er_dividend||0)+(c.er_valuation||0)+(c.er_currency||0);}

  /* ---------- detail panel ---------- */
  function show(code,scroll){
    var c=GF[code]; if(!c)return; cur=code;
    var vc=VC[c.valuation]||'v-fair';
    var gr=c.er_growth||0,dv=c.er_dividend||0,vl=c.er_valuation||0,fx=c.er_currency||0;
    var inr=gr+dv+vl+fx;
    var er=block('What you might earn — and where it comes from',
      '<div class="erbar">'+erRow('Earnings growth',gr)+erRow('Dividends',dv)
      +erRow('Valuation drift',vl)+erRow('Currency vs rupee',fx)
      +erRow('Est. return in rupees',inr,true)+'</div>'
      +'<p class="pnote" style="margin-top:9px"><em>'+esc(c.currency_note||'')+'</em></p>');
    var pay=block('What you are paying',
      '<div class="kv"><span class="k">CAPE now<b>'+esc(c.cape_now)+'</b></span>'
      +'<span class="k">Its own average<b>'+esc(c.cape_avg)+'</b></span>'
      +'<span class="k">Dearer than<b>'+esc(c.cape_pct)+'% of its past</b></span>'
      +'<span class="k">Price / book<b>'+esc(c.pb)+'</b></span>'
      +'<span class="k">Dividend<b>'+esc(c.div_yield)+'%</b></span>'
      +'<span class="k">Return on equity<b>'+esc(c.roe)+'%</b></span></div>');
    var qual=block('Quality &amp; safety checks',
      '<div class="kv"><span class="k">Top-10 weight<b>'+esc(c.top10_weight)+'%</b></span>'
      +'<span class="k">Govt debt / GDP<b>'+esc(c.govt_debt_gdp)+'%</b></span>'
      +'<span class="k wide">Worst fall on record<b>'+esc(c.worst_drawdown)+'</b></span>'
      +'<span class="k wide">Rule of law &amp; shareholder protection<b class="sm">'+esc(c.rule_of_law)+'</b></span>'
      +'<span class="k wide">Demographics<b class="sm">'+esc(c.demographics)+'</b></span></div>');
    var news='';
    if(c.news&&c.news.length){news=block('Today in the news','<div class="gf-news">'
      +c.news.map(function(n){return '<a href="'+esc(n.url)+'" target="_blank" rel="noopener">'+esc(n.title)+'</a>';}).join('')+'</div>');}
    $('panel').innerHTML='<h3>'+esc(c.name)+'<span class="gf-vpill '+vc+'">'+esc(c.valuation)+'</span></h3>'
      +'<div class="sub">'+esc(c.index)+' · '+esc(c.region)+'</div>'
      +'<div class="verdict '+vc+'"><b>The verdict</b>'+esc(c.verdict)+'</div>'
      +block('Outlook','<p class="pnote">'+esc(c.outlook)+'</p>')
      +pay+er+qual
      +block('What could go wrong',list(c.risks,'bad'))
      +block('Tailwinds',list(c.tailwinds,'good'))
      +block('Headwinds',list(c.headwinds,'bad'))
      +block('Can you actually buy it?','<p class="pnote">'+esc(c.access)+'</p>')
      +'<div class="gf-india"><b>Why it matters for India:</b> '+esc(c.india_angle)+'</div>'
      +news;
    var shapes=document.querySelectorAll('.cty');
    for(var i=0;i<shapes.length;i++){shapes[i].classList.toggle('sel',shapes[i].getAttribute('data-code')===code);}
    var rows=document.querySelectorAll('#crows .row');
    for(var j=0;j<rows.length;j++){rows[j].classList.toggle('sel',rows[j].getAttribute('data-code')===code);}
    if(scroll&&window.innerWidth<=900){$('panel').scrollIntoView({behavior:'smooth',block:'start'});}
  }

  /* ---------- sortable country table ---------- */
  var VORD={cheap:0,fair:1,expensive:2};
  function renderRows(){
    var arr=order.slice();
    arr.sort(function(a,b){
      var A=GF[a],B=GF[b],x,y;
      if(sortKey==='name'){return sortAsc?A.name.localeCompare(B.name):B.name.localeCompare(A.name);}
      if(sortKey==='valuation'){x=VORD[A.valuation];y=VORD[B.valuation];}
      else if(sortKey==='er'){x=erTotal(A);y=erTotal(B);}
      else{x=A.cape_now;y=B.cape_now;}
      return sortAsc?x-y:y-x;
    });
    $('crows').innerHTML=arr.map(function(code){
      var c=GF[code],t=erTotal(c),vc=VC[c.valuation];
      var col=t>=4?'var(--c-cheap)':(t<=1?'var(--c-exp)':'var(--ink2)');
      return '<div class="row '+vc+'" data-code="'+code+'"><span class="c-name"><i class="sw"></i>'
        +'<i>'+esc(c.name)+'</i></span><span class="c-val">'+esc(c.valuation)+'</span>'
        +'<span class="c-cape">'+esc(c.cape_now)+'</span>'
        +'<span class="c-er" style="color:'+col+'">'+(t>0?'+':'')+t.toFixed(1)+'%</span></div>';
    }).join('');
    if(cur){var r=document.querySelector('#crows .row[data-code="'+cur+'"]');if(r)r.classList.add('sel');}
  }
  var heads=document.querySelectorAll('#ctable .thead span');
  for(var h=0;h<heads.length;h++){
    heads[h].onclick=function(){
      var k=this.getAttribute('data-sort');
      if(k===sortKey){sortAsc=!sortAsc;}else{sortKey=k;sortAsc=(k!=='er');}
      for(var i=0;i<heads.length;i++){heads[i].classList.remove('sorted');}
      this.classList.add('sorted');
      renderRows();
    };
  }
  renderRows();

  /* ---------- map: hover, click, zoom, pan ---------- */
  var svg=$('map'),tip=$('tip'),VB={x:0,y:0,w:1000,h:500};
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
  }
  function svgPt(e){
    var r=svg.getBoundingClientRect();
    return {x:VB.x+(e.clientX-r.left)/r.width*VB.w, y:VB.y+(e.clientY-r.top)/r.height*VB.h};
  }
  $('zin').onclick=function(){zoom(0.7);};
  $('zout').onclick=function(){zoom(1.4);};
  $('zres').onclick=function(){VB={x:0,y:0,w:1000,h:500};applyVB();};
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
    var t=e.target,code=t.getAttribute&&t.getAttribute('data-code');
    if(code&&GF[code]){
      var c=GF[code],r=svg.parentNode.getBoundingClientRect();
      tip.innerHTML='<b>'+esc(c.name)+'</b>'+esc(c.valuation)+' · CAPE '+esc(c.cape_now)+' (avg '+esc(c.cape_avg)+')';
      tip.style.left=Math.min(e.clientX-r.left+14,r.width-215)+'px';
      tip.style.top=(e.clientY-r.top+14)+'px';
      tip.classList.add('on');
    }else{tip.classList.remove('on');}
  });

  document.addEventListener('click',function(e){
    if(moved){moved=false;return;}
    var t=e.target.closest('[data-code]');
    if(t&&GF[t.getAttribute('data-code')]){show(t.getAttribute('data-code'),true);}
  });

  /* ---------- heat-map tooltip ---------- */
  var htip=$('htip'),cells=document.querySelectorAll('.heat td');
  for(var k=0;k<cells.length;k++){
    (function(cell){
      cell.addEventListener('mouseenter',function(){
        var p=ROT[+cell.getAttribute('data-p')];if(!p)return;
        var wrap=cell.closest('.heatwrap'),r=wrap.getBoundingClientRect(),cr=cell.getBoundingClientRect();
        htip.innerHTML='<b>'+esc(p.period)+' · '+esc(cell.getAttribute('data-b'))+'</b>'
          +'<span class="wrapline">'+esc(p.why)+'</span>';
        htip.style.left=Math.max(6,Math.min(cr.left-r.left,r.width-300))+'px';
        htip.style.top=(cr.bottom-r.top+8)+'px';
        htip.classList.add('on');
      });
      cell.addEventListener('mouseleave',function(){htip.classList.remove('on');});
    })(cells[k]);
  }

  if(GF['IN']){show('IN',false);}
})();
</script>
</div></body></html>
"""

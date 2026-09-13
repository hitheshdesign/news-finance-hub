"""
render/assets_page.py — the Asset Classes page template.

Everything an Indian investor can actually buy, priced against its OWN history,
behind one switch:
  * Priced today — a valuation board of tiles grouped by family, a sortable
    table, and a rich detail panel per asset that ends with the real routes to
    buy it (fund, ETF, direct, cost, entry ticket, tax).
  * History & what wins when — the long-run record, the cross-asset
    relative-value gauges, and the five market-weather regimes with what has
    historically won and lost in each.

Kept in its own module, like global_page.py, because of the inline JS.
"""

ASSETS_PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asset Classes — India Impact Brief</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{{ fonts }}" rel="stylesheet">
{{ icon }}{{ themeboot }}
<style>{{ css }}</style>
</head><body><div class="wrap wide">

<header class="mast">
  <div class="kicker">World news, decoded for Indian markets</div>
  <div class="brandrow">{{ logo }}<h1>Asset Classes</h1></div>
  {{ themebtn }}
  <div class="date">Everything you can actually invest in from India — what each one
    costs against its own history, where the return would come from, and how you
    would buy it · <span class="engine">updated {{ a.updated_human }}</span></div>
</header>

{{ nav }}

<div class="gf-switch" role="tablist">
  <button id="sw-now" class="on" role="tab">Priced today</button>
  <button id="sw-hist" role="tab">History &amp; what wins when</button>
</div>

<!-- ==================== VIEW 1: PRICED TODAY ==================== -->
<section id="view-now" class="gf-view">
  <details class="gf-note gf-acc">
    <summary>Indicative &amp; educational — not advice
      <span class="more">· how this page works, and what updates when</span></summary>
    <div class="acc-body">
      Every asset is coloured by how it is priced against
      <span class="term" tabindex="0" role="button" data-def="Comparing an asset with its own past, not with other assets. A PE of 22 means nothing on its own — it means something once you know this market normally trades nearer 23.5. Each asset is judged on its own yardstick: shares on profits, bonds on real yield after inflation, property on rent, silver on its ratio to gold.">its own history</span>,
      never against a target. Cheap or dear is worked out, not hand-set: inside 8% of its
      own normal counts as fair, further than that is cheap or dear. Any
      <span class="term" tabindex="0" role="button" data-def="Wherever a label is underlined like this, tap or hover it for a plain-English explanation.">underlined label</span>
      has a plain-English explanation.
      <span class="freshness"><b>Updated every morning:</b>
      {% if a.live_ok %}today's <b>P/E, price-to-book and dividend yield</b> for all
      {{ a.live_count }} live assets, straight from the NSE's own published index file
      ({{ a.live_as_of }}), plus gold, silver and the rupee. The cheap/fair/dear colour,
      the position of every marker and the valuation part of each return estimate are all
      recomputed from those numbers.{% else %}the news in each panel, the market mood and
      the highlighted weather pattern. <b>Live market data could not be reached on this
      run</b>, so the numbers below are the curated fallback.{% endif %}
      <b>Hand-curated and slower-moving:</b> each asset's long-run average, its history,
      the routes to buy it and every word of explanation — last reviewed
      <b>{{ a.as_of }}</b>. Ratios move daily; the lesson inside each panel does not.</span>
    </div>
  </details>

  <div class="gf-legend">
    <span class="lg v-cheap"><span class="sw"></span>Cheap vs its past · {{ a.stats.cheap }}</span>
    <span class="lg v-fair"><span class="sw"></span>Fair · {{ a.stats.fair }}</span>
    <span class="lg v-exp"><span class="sw"></span>Dear vs its past · {{ a.stats.expensive }}</span>
    <span class="lg v-none"><span class="sw"></span>No way to value it · {{ a.stats.no_anchor }}</span>
    <span class="hintx">The dot on each bar shows where today sits in that asset's own
      history — left of the tick is cheaper than usual, right is dearer.</span>
  </div>

  <div class="board">
    {% for f in a.families %}
    <section class="fam">
      <div class="famhead">
        <h3>{{ f.label }}</h3><span class="count">{{ f.assets|length }} options</span>
      </div>
      <p class="famnote">{{ f.note }}</p>
      <div class="tiles">
        {% for x in f.assets %}
        <button class="tile {{ x.vc }}" data-code="{{ x.code }}" type="button">
          <span class="tname">{{ x.short or x.name }}</span>
          <span class="tnum"><b>{{ x.metric_show }}</b><em>{{ x.metric_short }}</em></span>
          <span class="tavg">{% if x.metric_avg is not none %}normally {{ x.metric_avg_show }} <em>({{ x.metric_avg_short }})</em>{% else %}nothing to compare it with{% endif %}</span>
          {% if x.metric_pct is not none %}
          <span class="hist"><i class="tick"></i><i class="pin" style="left:{{ x.pin }}%"></i></span>
          {% else %}
          <span class="hist none"></span>
          {% endif %}
        </button>
        {% endfor %}
      </div>
    </section>
    {% endfor %}
  </div>

  <div class="gf-grid">
    <div class="ctable acols" id="atable">
      <div class="thead">
        <span class="c-name" data-sort="name">Asset</span>
        <span class="c-val" data-sort="valuation">Priced</span>
        <span class="c-met sorted" data-sort="pct">Vs its past</span>
        <span class="c-er" data-sort="er">Est. return</span>
      </div>
      <div id="arows"></div>
    </div>
    <div class="gf-panelwrap">
      <div class="panel" id="apanel">
        <p class="hint">Pick anything above to see what you would actually own, what it costs
        against its own history, where the return would come from — and every route you have
        to buy it in India, with the cost and the tax.</p>
      </div>
    </div>
  </div>
</section>

<!-- ============== VIEW 2: HISTORY & WHAT WINS WHEN ============== -->
<section id="view-hist" class="gf-view" hidden>
  <details class="gf-note gf-acc">
    <summary>Why this page has a second half{% if a.mood_today %}
      <span class="more">· today's news reads as {{ a.mood_today }}</span>{% endif %}</summary>
    <div class="acc-body">
      Knowing what each asset costs is only half the job. The other half is knowing
      <b>which asset wins in which weather</b> — because no single asset wins in all of it,
      and the ones that feel safest are often the ones being quietly destroyed. Below: how
      the same assets compare against each other right now, then the five weather patterns
      worth memorising.
      {% if a.mood_today %}<span class="freshness"><b>Today's news reads as
      {{ a.mood_today }}.</b>{% if a.leading_regime %} The pattern it points at most is
      <b>{{ a.leading_regime }}</b> — highlighted below.{% endif %}</span>{% endif %}
    </div>
  </details>

  <div class="section">How they compare with each other right now</div>
  <div class="gauges">
    {% for g in a.gauges %}
    <div class="gauge {{ g.vc }}">
      <h4>{{ g.name }}</h4>
      <span class="gmet">{{ g.metric }}</span>
      <div class="gnums">
        <span class="gn now">Today<span>{{ g.now }}</span></span>
        <span class="gn">Its normal level<span>{{ g.avg }}</span></span>
      </div>
      <p>{{ g.plain|gloss }}</p>
      <p class="gmean">{{ g.meaning|gloss }}</p>
    </div>
    {% endfor %}
  </div>

  <div class="section">The five weather patterns, and what wins in each</div>
  <div class="regimes">
    {% for r in a.regimes %}
    <div class="regime{{ ' on' if r.name == a.leading_regime }}">
      <div class="rgtop">
        <h4>{{ r.name }}</h4>
        {% if r.name == a.leading_regime %}<span class="now">Today's news points here</span>{% endif %}
      </div>
      <span class="tell"><b>How you would know:</b> {{ r.tell }}</span>
      <div class="wl">
        <div class="w"><h5>Tends to win</h5>
          <ul class="plist good">{% for x in r.winners %}<li>{{ x|gloss }}</li>{% endfor %}</ul>
        </div>
        <div class="l"><h5>Tends to lose</h5>
          <ul class="plist bad">{% for x in r.losers %}<li>{{ x|gloss }}</li>{% endfor %}</ul>
        </div>
      </div>
      <div class="rgblk"><h5>Why it works that way</h5><p>{{ r.why|gloss }}</p></div>
      <div class="rgindia"><b>The India twist</b>{{ r.india|gloss }}</div>
    </div>
    {% endfor %}
  </div>

  <div class="section">Every asset side by side</div>
  <div class="gf-note">
    What each asset has actually returned, worst fall included — because the fall is what
    decides whether you were still holding when the return arrived. Ordered by the indicative
    estimate looking forward, which is the sum of that asset's own return breakdown, so the
    boring assets at the top are boring on purpose. Past returns describe history; the
    estimate is arithmetic — nominal, before tax — not a forecast.
  </div>
  <div class="records">
    {% for x in a.by_return %}
    <div class="rec {{ x.vc }}">
      <div class="rtop">
        <span class="rname">{{ x.name }}</span>
        <span class="rband">{{ x.band_short }}</span>
        <span class="rer">{% if x.total_return is none %}No honest estimate possible{% else %}Estimate ahead <b>{{ x.total_show }} a year</b>{% endif %}</span>
      </div>
      <div class="rhist">
        {% for h in x.history %}<span class="rh"><b>{{ h.label }}</b>{{ h.value }}</span>{% endfor %}
      </div>
      <p class="rfall"><b>Worst fall:</b> {{ x.worst_fall }}</p>
    </div>
    {% endfor %}
  </div>

  <div class="gf-note">{{ a.note }}</div>
</section>

<div class="disclaimer">
  <b>Learning tool, not advice.</b> Valuations, long-run returns, costs and tax notes are
  curated indicative estimates refreshed periodically, not live data, and tax rules change.
  Nothing here is a recommendation to buy or sell anything, and none of it accounts for your
  own situation.
</div>

<footer class="pagefoot">
  <div class="archive"><a href="index.html">← Back to today's brief</a>
    <a href="global.html">World valuations →</a></div>
  <p>News Finance Hub · Asset Classes</p>
</footer>

<script>{{ tipjs }}{{ themejs }}
var AC = {{ a_json }};
(function(){
  var $=function(id){return document.getElementById(id);};
  function esc(s){var d=document.createElement('div');d.textContent=(s==null?'':String(s));return d.innerHTML;}
  var order=Object.keys(AC), sortKey='pct', sortAsc=true, cur=null;

  /* ---------- view switch ---------- */
  function view(v){
    $('view-now').hidden=!v; $('view-hist').hidden=v;
    $('sw-now').classList.toggle('on',v); $('sw-hist').classList.toggle('on',!v);
  }
  $('sw-now').onclick=function(){view(true);};
  $('sw-hist').onclick=function(){view(false);};

  /* ---------- helpers ---------- */
  function tdef(label,def){
    if(!def)return esc(label);
    return '<span class="term" tabindex="0" role="button" aria-label="'+esc(def)+'" '
      +'data-def="'+esc(def)+'">'+esc(label)+'</span>';
  }
  function block(title,inner){return inner?'<div class="pblock"><h4>'+title+'</h4>'+inner+'</div>':'';}
  function list(arr,cls){if(!arr||!arr.length)return '';
    return '<ul class="plist '+(cls||'')+'">'+arr.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';}
  function clamp(p){return Math.max(3,Math.min(97,p));}
  var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function shortDate(iso){
    if(!iso||iso.length<10)return '';
    var mo=parseInt(iso.slice(5,7),10);
    return parseInt(iso.slice(8,10),10)+' '+(MON[mo-1]||'');
  }
  /* Says plainly whether a number came from today's market or from the
     curated notes — the reader should never have to guess which. */
  function livePill(c){
    if(!c.live_ok)return '<span class="livepill off">Curated</span>';
    var d=shortDate(c.live_as_of);
    return '<span class="livepill on">Live · '+esc(c.live_source||'')
      +(d?' '+esc(d):'')+'</span>';
  }
  function histBar(c,extra){
    if(c.metric_pct==null)return '<div class="hist none'+(extra||'')+'"></div>';
    return '<div class="hist'+(extra||'')+'"><i class="tick"></i>'
      +'<i class="pin" style="left:'+clamp(c.metric_pct)+'%"></i></div>';
  }
  /* One row of the "where would the return come from" bar. */
  function erRow(label,val,total,hint){
    var MAX=12,w=Math.min(Math.abs(val)/MAX,1)*50,cls=val>=0?'pos':'neg';
    var style=val>=0?('left:50%;width:'+w+'%'):('right:50%;width:'+w+'%');
    return '<div class="erow'+(total?' total':'')+'"><span class="lbl">'+tdef(label,hint)+'</span>'
      +'<span class="track"><span class="fill '+cls+'" style="'+style+'"></span></span>'
      +'<span class="num">'+(val>0?'+':'')+val.toFixed(1)+'%</span></div>';
  }

  /* ---------- detail panel ---------- */
  function show(code,scroll){
    var c=AC[code]; if(!c)return; cur=code;

    /* 1. what it actually is */
    var comp='';
    if(c.composition&&c.composition.length){
      comp=c.composition.map(function(x){
        return '<div class="sec"><div class="secbar"><span style="width:'+Math.min(x.weight*2,100)+'%"></span></div>'
          +'<div class="sectxt"><b>'+esc(x.name)+'</b><span class="pct">'+esc(x.weight)+'%</span>'
          +'<p>'+esc(x.note)+'</p></div></div>';
      }).join('');
    }
    var what=block('What this actually is',
      '<p class="pnote">'+esc(c.what_it_is)+'</p>'
      +'<p class="explain"><b>What you would really own.</b> '+esc(c.own)+'</p>'
      +(comp?'<div class="secs"><div class="secshead">What is inside it</div>'+comp+'</div>':''));

    /* 2. priced against its own history */
    var pay;
    if(c.metric_now==null){
      pay=block('What it costs',
        '<div class="vsnow"><span class="vbig">—</span><div class="vmid">'
        +'<div class="vhead"><span class="vlbl">'+tdef(c.metric_label,c.metric_def)+'</span></div>'
        +'<div class="vavg">'+esc(c.metric_avg_label)+'</div></div></div>');
    }else{
      var cmp=c.dear?'dearer':'cheaper';
      pay=block('What it costs, against its own history',
        '<div class="vsnow"><span class="vbig">'+esc(c.metric_show)+'</span><div class="vmid">'
        +'<div class="vhead"><span class="vlbl">'+tdef(c.metric_label,c.metric_def)+'</span>'
        +livePill(c)+'</div>'
        +'<div class="vavg">Normally <b>'+esc(c.metric_avg_show)+'</b> ('+esc(c.metric_avg_label)
        +') — so today is <b>'+cmp+' than usual</b></div></div></div>'
        +histBar(c)
        +'<div class="histscale"><span>Cheaper than its past</span>'
        +'<span>Its normal level</span><span>Dearer</span></div>'
        +(c.extras&&c.extras.length?'<div class="kv" style="margin-top:12px">'
          +c.extras.map(function(x){
              return '<span class="k">'+tdef(x.label,x['def'])+'<b>'+esc(x.value)+'</b></span>';
            }).join('')+'</div>':''));
    }

    /* 3. where the return would come from */
    var er='';
    if(c.returns&&c.returns.length){
      er=block('Where your return would come from',
        '<p class="explain">Add these up and you have the honest long-run expectation. Rough '
        +'yearly averages, <b>in rupees and before tax</b>, so every asset on this page is '
        +'measured the same way — tap any label to see what it means.</p>'
        +'<div class="erbar">'
        +c.returns.map(function(r){return erRow(r.label,r.value,0,r['def']);}).join('')
        +erRow('Rough yearly total',c.total_return,1,'The rows above added together. Indicative only, before tax — a way to see WHY a return might be good or poor, not a forecast.')
        +'</div>'
        +(c.return_note?'<p class="explain">'+esc(c.return_note)+'</p>':''));
    }

    /* 4. what it has actually done */
    var hrows=(c.history||[]).map(function(h){
      return '<div class="qrow"><span class="qk">'+esc(h.label)+'</span>'
        +'<span class="qv">'+esc(h.value)+'</span></div>';
    }).join('');
    var past=block('What it has actually done',
      '<div class="qrows">'+hrows
      +'<div class="qrow"><span class="qk">'+tdef('Worst fall','The deepest drop it has ever put its owners through, and how long recovery took. This — not the average return — is what decides whether you are still holding when the return arrives.')+'</span>'
      +'<span class="qv">'+esc(c.worst_fall)+'</span></div></div>');

    /* 5. when it wins, and its job */
    var role=block('When it wins, and its job in a portfolio',
      '<div class="qrows"><div class="qrow"><span class="qk">Wins when</span>'
      +'<span class="qv">'+esc(c.wins_when)+'</span></div>'
      +'<div class="qrow"><span class="qk">Its job</span>'
      +'<span class="qv">'+esc(c.role)+'</span></div></div>');

    /* 6. how you can actually buy it — the point of the page */
    var routes='';
    if(c.how_to_invest&&c.how_to_invest.length){
      routes=c.how_to_invest.map(function(r){
        var chips='';
        if(r.cost&&r.cost!=='—')  chips+='<span class="chip"><b>Cost</b>'+esc(r.cost)+'</span>';
        if(r.entry&&r.entry!=='—') chips+='<span class="chip"><b>Start with</b>'+esc(r.entry)+'</span>';
        if(r.tax&&r.tax!=='—')    chips+='<span class="chip"><b>Tax</b>'+esc(r.tax)+'</span>';
        return '<div class="route"><span class="rname">'+esc(r.route)+'</span>'
          +(r.examples&&r.examples!=='—'?'<span class="rex">'+esc(r.examples)+'</span>':'')
          +(chips?'<div class="rchips">'+chips+'</div>':'')
          +'<p>'+esc(r.note)+'</p></div>';
      }).join('');
      routes=block('How you can actually buy it','<div class="howto">'+routes+'</div>');
    }

    var news='';
    if(c.news&&c.news.length){news=block('Today in the news','<div class="gf-news">'
      +c.news.map(function(n){return '<a href="'+esc(n.url)+'" target="_blank" rel="noopener">'+esc(n.title)+'</a>';}).join('')+'</div>');}

    $('apanel').className='panel '+c.vc;
    $('apanel').innerHTML='<h3>'+esc(c.name)+'<span class="gf-vpill '+c.vc+'">'+esc(c.band_label)+'</span></h3>'
      +'<div class="sub">'+esc(c.proxy)+' · '+esc(c.family_label)+'</div>'
      +(c.reading?'<p class="reading">'+esc(c.reading)+'</p>':'')
      +'<div class="verdict '+c.vc+'"><b>The bottom line</b>'+esc(c.verdict)+'</div>'
      +what+pay+er+past
      +block('What could lift it',list(c.drivers_up,'good'))
      +block('What could hurt it',list(c.drivers_down,'bad'))
      +role+routes
      +block('What is taken in tax','<p class="pnote">'+esc(c.tax)+'</p>')
      +block('What to watch',list(c.watch))
      +news;

    var tiles=document.querySelectorAll('.tile');
    for(var i=0;i<tiles.length;i++){tiles[i].classList.toggle('sel',tiles[i].getAttribute('data-code')===code);}
    var rows=document.querySelectorAll('#arows .row');
    for(var j=0;j<rows.length;j++){rows[j].classList.toggle('sel',rows[j].getAttribute('data-code')===code);}
    if(scroll&&window.innerWidth<=900){$('apanel').scrollIntoView({behavior:'smooth',block:'start'});}
  }

  /* ---------- sortable table ---------- */
  var VORD={cheap:0,fair:1,expensive:2,no_anchor:3};
  function renderRows(){
    var arr=order.slice();
    arr.sort(function(a,b){
      var A=AC[a],B=AC[b],x,y;
      if(sortKey==='name'){return sortAsc?A.name.localeCompare(B.name):B.name.localeCompare(A.name);}
      if(sortKey==='valuation'){x=VORD[A.valuation];y=VORD[B.valuation];}
      else if(sortKey==='er'){
        if(A.total_return==null||B.total_return==null){
          return (A.total_return==null?1:0)-(B.total_return==null?1:0);
        }
        x=A.total_return;y=B.total_return;
      }
      else{  /* percentile: nulls always last, whichever way we sort */
        if(A.metric_pct==null||B.metric_pct==null){
          return (A.metric_pct==null?1:0)-(B.metric_pct==null?1:0);
        }
        x=A.metric_pct;y=B.metric_pct;
      }
      return sortAsc?x-y:y-x;
    });
    $('arows').innerHTML=arr.map(function(code){
      var c=AC[code],t=c.total_return;
      var col=t==null?'var(--faint)':(t>=8?'var(--c-cheap)':(t<=4?'var(--c-exp)':'var(--ink2)'));
      return '<div class="row '+c.vc+'" data-code="'+code+'" '
        +'title="'+esc(c.name+' — '+c.proxy)+'">'
        +'<span class="c-name"><i class="sw"></i><i>'+esc(c.short||c.name)+'</i></span>'
        +'<span class="c-val">'+esc(c.band_short)+'</span>'
        +'<span class="c-met">'+histBar(c,' mini')+'</span>'
        +'<span class="c-er" style="color:'+col+'">'+esc(c.total_show)+'</span></div>';
    }).join('');
    if(cur){var r=document.querySelector('#arows .row[data-code="'+cur+'"]');if(r)r.classList.add('sel');}
  }
  var heads=document.querySelectorAll('#atable .thead span');
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

  /* ---------- clicks ---------- */
  document.addEventListener('click',function(e){
    var t=e.target.closest('[data-code]');
    if(t&&AC[t.getAttribute('data-code')]){show(t.getAttribute('data-code'),true);}
  });

  if(AC['LARGECAP']){show('LARGECAP',false);}
})();
</script>
</div></body></html>
"""

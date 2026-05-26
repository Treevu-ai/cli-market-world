"""Dashboard HTML — embedded single-page app for /dashboard.

Terminal / OS-style BI dashboard for the CLI Market data moat.
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CLI Market // Data Moat</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #0a0a0a;
    --panel: #0f0f0f;
    --border: #1a1a1a;
    --text: #b0b0b0;
    --dim: #444;
    --green: #3cffd0;
    --red: #ff4444;
    --yellow: #ffbd2e;
    --blue: #60a5fa;
    --pink: #f472b6;
    --purple: #a78bfa;
    --font: 'JetBrains Mono','IBM Plex Mono','Courier New',monospace;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:12px;line-height:1.5;padding:12px 16px;min-height:100vh}
  .status-bar{display:flex;justify-content:space-between;align-items:center;background:var(--panel);border:1px solid var(--border);padding:8px 14px;margin-bottom:10px;font-size:11px}
  .status-bar .host{color:var(--green)}
  .status-bar .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px}
  .status-bar .dot.ok{background:var(--green);box-shadow:0 0 6px var(--green)}
  .status-bar .dot.warn{background:var(--yellow)}
  .status-bar .dot.dead{background:var(--red)}
  .kpi-row{display:flex;gap:10px;margin-bottom:10px;flex-wrap:wrap}
  .kpi{background:var(--panel);border:1px solid var(--border);padding:10px 18px;min-width:110px}
  .kpi .val{font-size:1.6rem;font-weight:700;color:var(--green);line-height:1.1}
  .kpi .lbl{font-size:0.6rem;color:var(--dim);text-transform:uppercase;letter-spacing:1.5px;margin-top:2px}
  .kpi .sub{font-size:0.55rem;color:#333}
  .alerts{margin-bottom:10px}
  .alert{background:#1a0f0f;border:1px solid #3a1a1a;color:var(--red);padding:6px 12px;font-size:0.65rem;margin-bottom:4px;display:flex;align-items:center;gap:6px}
  .alert::before{content:'!';font-weight:700;font-size:0.8rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:10px}
  .panel{background:var(--panel);border:1px solid var(--border)}
  .panel-title{color:var(--dim);font-size:0.6rem;text-transform:uppercase;letter-spacing:2px;padding:8px 14px;border-bottom:1px solid var(--border)}
  .panel-title::before{content:'[ '}
  .panel-title::after{content:' ]'}
  .panel-body{padding:10px 14px}
  canvas{max-height:200px}
  table{width:100%;font-size:0.62rem;border-collapse:collapse}
  th{text-align:left;color:var(--dim);font-weight:400;padding:4px 8px;border-bottom:1px solid var(--border);font-size:0.55rem;text-transform:uppercase;letter-spacing:1px}
  td{padding:3px 8px;border-bottom:1px solid #111;white-space:nowrap}
  td.num{text-align:right;font-variant-numeric:tabular-nums}
  td.up{color:var(--red)}
  td.down{color:var(--green)}
  tr:hover{background:#111}
  .footer{color:var(--dim);font-size:0.55rem;text-align:right;margin-top:10px;padding:6px 0;border-top:1px solid var(--border)}
  .wide{grid-column:span 2}
  @media(max-width:820px){.wide{grid-column:span 1}}
  .badge{font-size:0.5rem;padding:1px 5px;border-radius:2px;margin-left:4px}
  .badge-ok{background:#0a2a1a;color:var(--green)}
  .badge-warn{background:#2a1a0a;color:var(--yellow)}
</style>
</head>
<body>
<div class="status-bar">
  <div><span class="dot ok"></span><span class="host">CLI Market</span> // Data Moat <span style="color:var(--dim)">v1.4.0</span></div>
  <div id="statusRight" style="color:var(--dim)">loading...</div>
</div>

<div class="kpi-row" id="kpis"></div>
<div class="alerts" id="alerts"></div>

<div class="grid">
  <div class="panel"><div class="panel-title">Precios por línea</div><div class="panel-body"><canvas id="chartLines"></canvas></div></div>
  <div class="panel"><div class="panel-title">Precios por país</div><div class="panel-body"><canvas id="chartCountries"></canvas></div></div>
  <div class="panel"><div class="panel-title">Dispersión de precios</div><div class="panel-body"><table><thead><tr><th>Línea</th><th class="num">Precio prom.</th><th class="num">Spread</th></tr></thead><tbody id="dispersionTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Tienda más barata por línea</div><div class="panel-body"><table><thead><tr><th>Línea</th><th>Tienda</th><th class="num">Precio prom.</th></tr></thead><tbody id="cheapestTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Top descuentos</div><div class="panel-body"><table><thead><tr><th>Producto</th><th>Tienda</th><th class="num">Precio</th><th class="num">Desc.</th></tr></thead><tbody id="discountsTable"></tbody></table></div></div>
  <div class="panel wide"><div class="panel-title">Price movers 7d</div><div class="panel-body" style="display:flex;gap:20px;flex-wrap:wrap">
    <div style="flex:1;min-width:200px"><h3 style="font-size:0.6rem;color:var(--red);text-transform:uppercase;margin-bottom:6px">&#9650; Subieron</h3><table><thead><tr><th>Producto</th><th class="num">Antes</th><th class="num">Ahora</th><th class="num">Δ</th></tr></thead><tbody id="risersTable"></tbody></table></div>
    <div style="flex:1;min-width:200px"><h3 style="font-size:0.6rem;color:var(--green);text-transform:uppercase;margin-bottom:6px">&#9660; Bajaron</h3><table><thead><tr><th>Producto</th><th class="num">Antes</th><th class="num">Ahora</th><th class="num">Δ</th></tr></thead><tbody id="fallersTable"></tbody></table></div>
  </div></div>
  <div class="panel"><div class="panel-title">Frescura de datos</div><div class="panel-body"><table><thead><tr><th>Tienda</th><th>Último snapshot</th></tr></thead><tbody id="freshnessTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Store health</div><div class="panel-body"><table><thead><tr><th>Tienda</th><th class="num">Éxito</th><th class="num">Fallos</th><th>Último</th></tr></thead><tbody id="healthTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Collector history</div><div class="panel-body"><table><thead><tr><th>Inicio</th><th class="num">Tiendas</th><th class="num">Precios</th><th class="num">Errs</th></tr></thead><tbody id="historyTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Distribución de precios</div><div class="panel-body"><canvas id="chartPriceDist"></canvas></div></div>
  <div class="panel"><div class="panel-title">Line × Country</div><div class="panel-body" id="matrixTable" style="overflow-x:auto"></div></div>
  <div class="panel"><div class="panel-title">Productos por tienda</div><div class="panel-body"><table><thead><tr><th>Tienda</th><th class="num">Productos</th><th class="num">Snapshots</th></tr></thead><tbody id="productsPerStoreTable"></tbody></table></div></div>
  <div class="panel"><div class="panel-title">Outliers de precio</div><div class="panel-body"><table><thead><tr><th>Producto</th><th>Tienda</th><th class="num">Precio</th></tr></thead><tbody id="outliersTable"></tbody></table></div></div>
</div>

<p class="footer" id="footer"></p>

<script>
let charts = [];
function destroyCharts(){charts.forEach(c=>c.destroy());charts=[]}

async function load(){
  try{
  const r=await fetch('/dashboard/data');
  if(!r.ok) throw new Error('HTTP '+r.status);
  const d=await r.json();

  // ── Status bar ──────────────────────────────────────────────────
  const coll = d.collector || {};
  const dotCls = coll.status==='healthy'?'ok':coll.status==='stale'?'warn':'dead';
  const ts = d.generated_at ? new Date(d.generated_at).toLocaleTimeString('es-PE') : '--:--';
  document.getElementById('statusRight').innerHTML =
    `<span class="dot ${dotCls}"></span>collector: ${coll.status} | stores: ${coll.stores_succeeded||0}/${d.kpis.total_stores} | ${ts}`;

  // ── Alerts ──────────────────────────────────────────────────────
  const alerts=[];
  if(coll.status&&coll.status!=='healthy'){
    alerts.push(`Collector ${coll.status} — última ejecución: ${coll.last_finished||'nunca'} (${coll.age_hours!=null?coll.age_hours+'h':'?'})`);
  }
  if(d.failing_stores&&d.failing_stores.length){
    alerts.push(d.failing_stores.map(s=>`${s.store} (×${s.consecutive_failures})`).join(', ') + ' — tiendas caídas');
  }
  if(d.kpis.stores_24h===0 && d.kpis.active_stores>0){
    alerts.push('0 tiendas actualizadas en 24h — ¿collector detenido?');
  }
  document.getElementById('alerts').innerHTML=alerts.map(a=>`<div class="alert">${a}</div>`).join('');

  // ── KPIs ────────────────────────────────────────────────────────
  document.getElementById('kpis').innerHTML = `
    <div class="kpi"><div class="val">${(d.kpis.total_snapshots||0).toLocaleString()}</div><div class="lbl">Precios</div></div>
    <div class="kpi"><div class="val">${d.kpis.active_stores||0}<span class="sub">/${d.kpis.total_stores}</span></div><div class="lbl">Tiendas</div></div>
    <div class="kpi"><div class="val">${d.by_country.length}</div><div class="lbl">Países</div></div>
    <div class="kpi"><div class="val">${d.kpis.total_runs||0}</div><div class="lbl">Ciclos</div></div>
    <div class="kpi"><div class="val">${d.kpis.stores_24h||0}</div><div class="lbl">24h activas</div></div>
    <div class="kpi"><div class="val">${(d.top_discounts||[]).length}</div><div class="lbl">Descuentos</div></div>
  `;

  // ── Charts ──────────────────────────────────────────────────────
  destroyCharts();
  const colors=['#3cffd0','#60a5fa','#f472b6','#a78bfa','#ffbd2e','#ff6b6b','#4ade80','#fb923c'];

  if(d.by_line&&d.by_line.length){
    charts.push(new Chart(document.getElementById('chartLines'),{type:'bar',data:{
      labels:d.by_line.map(x=>x.line_name||x.line||'?'),
      datasets:[{label:'Precios',data:d.by_line.map(x=>x.count),backgroundColor:colors,borderRadius:2}]
    },options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false}},scales:{y:{grid:{color:'#1a1a1a'},ticks:{color:'#444',font:{size:9}}},x:{ticks:{color:'#444',font:{size:9}}}}}}));
  }

  if(d.by_country&&d.by_country.length){
    charts.push(new Chart(document.getElementById('chartCountries'),{type:'doughnut',data:{
      labels:d.by_country.map(x=>x.country),
      datasets:[{data:d.by_country.map(x=>x.count),backgroundColor:colors, borderColor:'#0a0a0a',borderWidth:2}]
    },options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{color:'#555',font:{size:9},padding:12}}}}}}));
  }

  // ── Dispersion ──────────────────────────────────────────────────
  const dispRows=(d.dispersion||[]).map(x=>`<tr><td>${x.line}</td><td class="num">${(x.avg_price||0).toFixed(2)}</td><td class="num">${x.spread_ratio>2?'<span style="color:#ffbd2e">':''}${x.spread_ratio.toFixed(2)}×${x.spread_ratio>2?'</span>':''}</td></tr>`).join('');
  document.getElementById('dispersionTable').innerHTML=dispRows||'<tr><td colspan="3" style="color:var(--dim)">sin datos</td></tr>';

  // ── Cheapest by line ────────────────────────────────────────────
  const cheapRows=(d.cheapest_by_line||[]).map(x=>`<tr><td>${x.line_name}</td><td>${x.store_name}</td><td class="num" style="color:var(--green)">${x.currency||''} ${(x.avg_price||0).toFixed(2)}</td></tr>`).join('');
  document.getElementById('cheapestTable').innerHTML=cheapRows||'<tr><td colspan="3" style="color:var(--dim)">sin datos</td></tr>';

  // ── Top discounts ───────────────────────────────────────────────
  const discRows=(d.top_discounts||[]).map(x=>`<tr><td>${(x.name||'?').slice(0,40)}</td><td>${x.store_name||'?'}</td><td class="num">${x.currency||''} ${(x.price||0).toFixed(2)}</td><td class="num" style="color:var(--green)">−${x.discount_pct}%</td></tr>`).join('');
  document.getElementById('discountsTable').innerHTML=discRows||'<tr><td colspan="4" style="color:var(--dim)">sin descuentos detectados</td></tr>';

  // ── Risers / Fallers ────────────────────────────────────────────
  const riserRows=(d.top_risers||[]).map(x=>{
    const pid=x.product_id||'?';
    return `<tr><td>${pid.slice(0,25)}</td><td class="num">${(x.price_before||0).toFixed(2)}</td><td class="num">${(x.price_now||0).toFixed(2)}</td><td class="num up">+${x.delta_pct}%</td></tr>`;
  }).join('')||'<tr><td colspan="4" style="color:var(--dim)">sin datos</td></tr>';
  document.getElementById('risersTable').innerHTML=riserRows;

  const fallerRows=(d.top_fallers||[]).map(x=>
    `<tr><td>${(x.product_id||'?').slice(0,25)}</td><td class="num">${(x.price_before||0).toFixed(2)}</td><td class="num">${(x.price_now||0).toFixed(2)}</td><td class="num down">${x.delta_pct}%</td></tr>`
  ).join('')||'<tr><td colspan="4" style="color:var(--dim)">sin datos</td></tr>';
  document.getElementById('fallersTable').innerHTML=fallerRows;

  // ── Store health ────────────────────────────────────────────────
  const healthRows=(d.store_health||[]).slice(0,15).map(x=>{
    const pct=x.success_pct||0;
    const cls=pct>=90?'color:var(--green)':pct>=50?'color:var(--yellow)':'color:var(--red)';
    return `<tr><td>${x.store}</td><td class="num" style="${cls}">${pct}%</td><td class="num">${x.consecutive_failures||0}</td><td style="font-size:0.5rem">${(x.last_success||'—').slice(0,16)}</td></tr>`;
  }).join('');
  document.getElementById('healthTable').innerHTML=healthRows||'<tr><td colspan="4" style="color:var(--dim)">sin datos</td></tr>';

  // ── Collector history ────────────────────────────────────────────
  const histRows=(d.collector_history||[]).map(x=>{
    const start=((x.started_at||'')+'').slice(0,16);
    return `<tr><td>${start}</td><td class="num">${x.stores_succeeded||0}/${x.stores_attempted||0}</td><td class="num">${(x.prices_collected||0).toLocaleString()}</td><td class="num">${x.errors||0}</td></tr>`;
  }).join('');
  document.getElementById('historyTable').innerHTML=histRows||'<tr><td colspan="4" style="color:var(--dim)">sin historial</td></tr>';

  // ── Price distribution chart ─────────────────────────────────────
  if(d.price_distribution&&d.price_distribution.length){
    charts.push(new Chart(document.getElementById('chartPriceDist'),{type:'bar',data:{
      labels:d.price_distribution.map(x=>x.bucket),
      datasets:[{label:'Productos',data:d.price_distribution.map(x=>x.count),backgroundColor:colors,borderRadius:2}]
    },options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false}},scales:{y:{grid:{color:'#1a1a1a'},ticks:{color:'#444',font:{size:9}}},x:{ticks:{color:'#444',font:{size:9}}}}}}));
  }

  // ── Line × Country matrix ────────────────────────────────────────
  if(d.line_country_matrix&&d.line_country_matrix.length){
    const lines=[...new Set(d.line_country_matrix.map(x=>x.line))];
    const countries=[...new Set(d.line_country_matrix.map(x=>x.country))].sort();
    const map={};
    d.line_country_matrix.forEach(x=>{map[x.line+'|'+x.country]=x.stores;});
    let mhtml='<table><thead><tr><th></th>'+countries.map(c=>`<th class="num">${c}</th>`).join('')+'</tr></thead><tbody>';
    lines.forEach(l=>{
      mhtml+=`<tr><td>${l}</td>`+countries.map(c=>{
        const v=map[l+'|'+c]||0;
        const bg=v>0?'background:#0a2a1a;color:var(--green)':'';
        return `<td class="num" style="${bg}">${v||'·'}</td>`;
      }).join('')+'</tr>';
    });
    mhtml+='</tbody></table>';
    document.getElementById('matrixTable').innerHTML=mhtml;
  }

  // ── Products per store ───────────────────────────────────────────
  const ppsRows=(d.products_per_store||[]).map(x=>`<tr><td>${x.store_name||x.store}</td><td class="num">${(x.unique_products||0).toLocaleString()}</td><td class="num">${(x.total_snapshots||0).toLocaleString()}</td></tr>`).join('');
  document.getElementById('productsPerStoreTable').innerHTML=ppsRows||'<tr><td colspan="3" style="color:var(--dim)">sin datos</td></tr>';

  // ── Outliers ─────────────────────────────────────────────────────
  const outRows=(d.outliers||[]).map(x=>`<tr><td>${(x.name||'?').slice(0,35)}</td><td>${x.store_name}</td><td class="num" style="color:var(--red)">${x.currency||''} ${(x.price||0).toFixed(2)}</td></tr>`).join('');
  document.getElementById('outliersTable').innerHTML=outRows||'<tr><td colspan="3" style="color:var(--dim)">sin outliers detectados</td></tr>';

  // ── Freshness ───────────────────────────────────────────────────
  const freshRows=(d.freshness||[]).slice(0,15).map(x=>{
    const seen=new Date(x.last_seen+'Z');
    const ago=Math.round((Date.now()-seen.getTime())/3600000);
    const cls=ago<12?'badge-ok':ago<24?'badge-warn':'';
    return `<tr><td>${x.store_name||x.store}</td><td>${seen.toLocaleString('es-PE')} <span class="badge ${cls}">${ago}h</span></td></tr>`;
  }).join('');
  document.getElementById('freshnessTable').innerHTML=freshRows||'<tr><td colspan="2" style="color:var(--dim)">sin datos</td></tr>';

  // ── Footer ──────────────────────────────────────────────────────
  document.getElementById('footer').textContent =
    `actualizado ${new Date().toLocaleString('es-PE')} · CLI Market Data Moat · PostgreSQL · auto-refresh 5min`;
  }catch(err){
    document.getElementById('statusRight').textContent='ERROR: '+err.message;
    document.getElementById('kpis').innerHTML='<div class="alert">JS Error: '+err.message+'</div>';
    console.error(err);
  }
}

load();
setInterval(load, 300000);
</script>
</body>
</html>"""

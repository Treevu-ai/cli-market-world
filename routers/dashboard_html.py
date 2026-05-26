"""Dashboard HTML — embedded single-page app for /dashboard.

Isolated from market_server.py and routers/dashboard.py so that:
  1. The HTML/CSS/JS lives in one file and grep'ing for selectors is sane.
  2. Future migration to a real frontend (the Next.js landing in /landing)
     means deleting THIS file and pointing /dashboard to a static asset.

If you're hand-editing this for more than 30 minutes, that migration is
overdue.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CLI Market — Data Moat</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#131313;color:#fff;font-family:'IBM Plex Mono',monospace;padding:20px}
h1{font-size:1.5rem;margin-bottom:4px}
h1 span{color:#3cffd0}
.subtitle{color:#949494;font-size:0.75rem;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.card{background:#1a1a1a;border:1px solid #2d2d2d;border-radius:8px;padding:16px}
.card h2{font-size:0.7rem;color:#3cffd0;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px}
canvas{max-height:260px}
.kpi-row{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap}
.kpi{background:#1a1a1a;border:1px solid #2d2d2d;border-radius:8px;padding:12px 20px;text-align:center;min-width:100px}
.kpi .val{font-size:1.8rem;font-weight:700;color:#3cffd0}
.kpi .lbl{font-size:0.6rem;color:#555;text-transform:uppercase;letter-spacing:1px}
table{width:100%;font-size:0.65rem;border-collapse:collapse}
th{text-align:left;color:#555;text-transform:uppercase;font-weight:400;padding:6px 8px;border-bottom:1px solid #2d2d2d}
td{padding:5px 8px;border-bottom:1px solid #1a1a1a}
td.price{color:#3cffd0;text-align:right}
.mono{font-size:0.55rem;color:#444}
#updated{color:#444;font-size:0.6rem;text-align:right;margin-top:8px}
.alert{background:#2d1a1a;border:1px solid #ff4444;color:#ff6b6b;border-radius:6px;padding:8px 14px;font-size:0.65rem;margin-bottom:6px}
.alert b{color:#ff8888}
</style>
</head>
<body>
<h1>CLI Market <span>Data Moat</span></h1>
<p class="subtitle">Precios recolectados de 60 retailers VTEX en 11 países · 6 líneas</p>
<div class="kpi-row" id="kpis"></div>
<div id="alerts"></div>
<div class="grid">
  <div class="card"><h2>Precios por línea</h2><canvas id="chartLines"></canvas></div>
  <div class="card"><h2>Precios por país</h2><canvas id="chartCountries"></canvas></div>
  <div class="card" style="grid-column:span 2"><h2>Últimos productos indexados</h2><table><thead><tr><th>Producto</th><th>Tienda</th><th class="price">Precio</th><th>Línea</th></tr></thead><tbody id="topProducts"></tbody></table></div>
</div>
<p id="updated"></p>
<script>
async function load(){
  const r=await fetch('/dashboard/data');
  const d=await r.json();

  // Alerts
  const alerts=[];
  if(d.collector&&d.collector.status&&d.collector.status!=='healthy'){
    alerts.push(`⚠️ Collector: <b>${d.collector.status}</b> — última vez: ${d.collector.last_finished||'nunca'}`);
  }
  if(d.failing_stores&&d.failing_stores.length>0){
    const names=d.failing_stores.map(s=>`${s.store} (×${s.consecutive_failures})`).join(', ');
    alerts.push(`🔴 Tiendas caídas: ${names}`);
  }
  if(d.price_trend&&d.price_trend.recent_7d===0&&d.price_trend.previous_7d>0){
    alerts.push('📉 0 precios nuevos en 7 días — ¿collector detenido?');
  }
  document.getElementById('alerts').innerHTML=alerts.map(a=>`<div class="alert">${a}</div>`).join('');

  // KPIs
  const total=d.by_line.reduce((s,x)=>s+x.count,0);
  const lines=d.by_line.length;
  const countries=d.by_country.length;
  document.getElementById('kpis').innerHTML=`
    <div class="kpi"><div class="val">${total.toLocaleString()}</div><div class="lbl">Precios</div></div>
    <div class="kpi"><div class="val">${lines}</div><div class="lbl">Líneas</div></div>
    <div class="kpi"><div class="val">${countries}</div><div class="lbl">Países</div></div>
    <div class="kpi"><div class="val">${d.total_runs}</div><div class="lbl">Ciclos</div></div>
    <div class="kpi"><div class="val">${d.collector?d.collector.stores_succeeded||'?':'?'}</div><div class="lbl">Tiendas ok</div></div>
  `;

  // Lines chart
  new Chart(document.getElementById('chartLines'),{type:'bar',data:{labels:d.by_line.map(x=>x.line_name||x.line||'?'),datasets:[{label:'Precios',data:d.by_line.map(x=>x.count),backgroundColor:'#3cffd0',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{grid:{color:'#2d2d2d'},ticks:{color:'#555'}},x:{ticks:{color:'#555'}}}}});

  // Countries chart
  new Chart(document.getElementById('chartCountries'),{type:'doughnut',data:{labels:d.by_country.map(x=>x.country),datasets:[{data:d.by_country.map(x=>x.count),backgroundColor:['#3cffd0','#5200ff','#FFD600','#FF6B35','#60A5FA','#F472B6','#A78BFA','#FB923C']}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{color:'#949494',font:{size:10}}}}}});

  // Top products table
  document.getElementById('topProducts').innerHTML=d.top_products.map(p=>`<tr><td>${p.name||'?'}</td><td>${p.store_name||'?'}</td><td class="price">${p.currency||''} ${(p.price||0).toFixed(2)}</td><td class="mono">${p.line_name||'?'}</td></tr>`).join('');

  document.getElementById('updated').textContent='Actualizado: '+new Date().toLocaleString();
}
load();
setInterval(load,300000);
</script>
</body>
</html>"""

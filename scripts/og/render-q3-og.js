// Renders the Q3 Open Graph image: node scripts/og/render-q3-og.js, then downscale og@2x.png to 1200x630 as 2026/q3/og.png.
const fs=require('fs'),path=require('path');const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const S=path.dirname(__filename);const D=require(path.join(S,'../../2026/q3/q3data.json'));
const TIMEsvg=fs.readFileSync(path.join(S,'time.svg'),'utf8').trim(),STsvg=fs.readFileSync(path.join(S,'statista.svg'),'utf8').trim();
const logo='data:image/png;base64,'+fs.readFileSync(path.join(S,'logo.png')).toString('base64');
// sparkline of rolling 30-day active students
const m=D.ga.mau,W=470,H=170,mn=Math.min(...m),mx=Math.max(...m);
const pts=m.map((v,i)=>[(i/(m.length-1))*W,H-((v-mn)/(mx-mn))*(H-24)-4]);
const line=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join('');
const area=line+`L${W},${H}L0,${H}Z`;const pk=pts[m.indexOf(mx)];
const html=`<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{background:#07090b;color:#eef3f1;font-family:'Manrope',system-ui,sans-serif;-webkit-font-smoothing:antialiased;position:relative;
 background-image:radial-gradient(900px 520px at 88% -12%,rgba(61,220,151,.16),transparent 62%),radial-gradient(700px 420px at -8% 110%,rgba(90,169,255,.09),transparent 60%)}
.wrap{position:absolute;inset:0;padding:52px 60px 48px}
.brand{display:flex;align-items:center;gap:14px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:24px;letter-spacing:-.01em}
.brand img{width:40px;height:40px;object-fit:contain}
.brand span{color:#8b9a95;font-weight:500;font-family:'JetBrains Mono',monospace;font-size:14px;letter-spacing:.12em;text-transform:uppercase;margin-left:10px}
h1{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:70px;line-height:1.02;letter-spacing:-.035em;margin:38px 0 14px}
h1 em{font-style:normal;color:#3ddc97}
.sub{color:#8b9a95;font-size:23px;font-weight:500;margin:0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:40px}
.kpi{background:rgba(14,18,21,.9);border:1px solid #26323a;border-radius:20px;padding:20px 22px 18px;box-shadow:0 1px 0 rgba(255,255,255,.035) inset}
.kpi .v{font-family:'JetBrains Mono',monospace;font-size:40px;font-weight:600;letter-spacing:-.03em;line-height:1}
.kpi .l{font-size:15px;font-weight:700;margin-top:10px}
.kpi .d{font-family:'JetBrains Mono',monospace;font-size:13px;margin-top:8px;color:#3ddc97;font-weight:500}
.kpi .d.flat{color:#8b9a95}
.chart{position:absolute;right:60px;top:138px;width:${W}px}
.chart .cap{font-family:'JetBrains Mono',monospace;font-size:13px;color:#8b9a95;letter-spacing:.04em;margin-bottom:26px;text-align:right}
.chart .pk{position:absolute;font-family:'JetBrains Mono',monospace;font-size:13px;color:#eef3f1;font-weight:600}
.foot{position:absolute;left:60px;right:60px;bottom:44px;display:flex;justify-content:space-between;align-items:center;font-family:'JetBrains Mono',monospace;font-size:14px;color:#8b9a95}
.pill{display:inline-flex;align-items:center;gap:10px;border:1px solid rgba(61,220,151,.35);background:rgba(61,220,151,.1);color:#9af2cc;border-radius:999px;padding:8px 16px;font-weight:500;letter-spacing:.02em}
.pill svg{height:18px;width:auto;display:block;color:#eef3f1}.pill em{font-style:normal;color:#8b9a95;margin:0 2px}
</style></head><body><div class="wrap">
<div class="brand"><img src="${logo}" alt=""> ASG SHOP <span>Q3 · 2026 · Performance Report</span></div>
<h1>Q3 2026 <em>Performance</em><br>Report</h1>
<p class="sub">Apars Classroom · Jul 1 – Sep 30, 2026</p>
<div class="chart"><div class="cap">ROLLING 30-DAY ACTIVE STUDENTS</div>
<div style="position:relative"><svg style="display:block" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3ddc97" stop-opacity=".45"/><stop offset="1" stop-color="#3ddc97" stop-opacity="0"/></linearGradient></defs>
<path d="${area}" fill="url(#g)"/><path d="${line}" fill="none" stroke="#3ddc97" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="${pk[0].toFixed(1)}" cy="${pk[1].toFixed(1)}" r="5" fill="#3ddc97" stroke="#07090b" stroke-width="2"/></svg>
<div class="pk" style="right:${(W-pk[0]+20).toFixed(0)}px;top:${(pk[1]-9).toFixed(0)}px">609K · Sep 9</div></div></div>
<div class="kpis">
<div class="kpi"><div class="v">1.19M</div><div class="l">Active students</div><div class="d">▲ 86.5% vs Q2</div></div>
<div class="kpi"><div class="v">1.72 PB</div><div class="l">Delivered at the edge</div><div class="d">▲ 62.7% vs Q2</div></div>
<div class="kpi"><div class="v">311K</div><div class="l">Live class participants</div><div class="d flat">917 sessions · new</div></div>
<div class="kpi"><div class="v">57m 05s</div><div class="l">Avg engagement</div><div class="d">▲ 3.0× vs Q2</div></div>
</div>
<div class="foot"><span class="pill">${TIMEsvg}<em>×</em>${STsvg}<em>·</em>World's Top EdTech Companies 2026</span><span>stats.asgshop.ai/2026/q3</span></div>
</div></body></html>`;
fs.writeFileSync(path.join(S,'og.html'),html);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:2});
  await p.goto('file://'+path.join(S,'og.html'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
  const fonts=await p.evaluate(()=>[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)===i));console.log('fonts loaded:',fonts);
  await p.screenshot({path:path.join(S,'og@2x.png'),type:'png'});await b.close();})().catch(e=>{console.error(e);process.exit(1)});

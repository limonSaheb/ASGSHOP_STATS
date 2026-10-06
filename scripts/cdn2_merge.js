#!/usr/bin/env node
// Merge monthly statistics exports of the secondary CDN into the Q3 report.
//
//   node scripts/cdn2_merge.js 2026/q3/raw/cdn2-2026-07.json [2026/q3/raw/cdn2-2026-08.json ...]
//
// Each input is one month's statistics export (BandwidthUsedChart, BandwidthCachedChart,
// RequestsServedChart, OriginTrafficChart, CacheHitRateChart, OriginResponseTimeChart,
// PullRequestsPulledChart, Error3xx/4xx/5xxChart, GeoTrafficDistribution). Days outside the
// quarter are dropped. The script rewrites the "cdn2" block in 2026/q3/q3data.json, the inline
// data of 2026/q3/index.html and index.html, the "Secondary CDN" subsection of report.md and
// llms-full.txt, and the one-line summary in llms.txt. Re-running with more months is safe.
const fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..'),PERIOD=['2026-07-01','2026-09-30'];
const files=process.argv.slice(2);
if(!files.length){console.error('usage: node scripts/cdn2_merge.js <monthly-stats.json>...');process.exit(1)}
const TB=1e12,M=1e6,r=(v,d)=>+v.toFixed(d);
const SERIES={bw:'BandwidthUsedChart',cached:'BandwidthCachedChart',rq:'RequestsServedChart',og:'OriginTrafficChart',chr:'CacheHitRateChart',ort:'OriginResponseTimeChart',pulls:'PullRequestsPulledChart',e3:'Error3xxChart',e4:'Error4xxChart',e5:'Error5xxChart'};
const day={},geo={};
for(const f of files){const d=JSON.parse(fs.readFileSync(f,'utf8'));
  for(const [k,src] of Object.entries(SERIES))for(const [ts,v] of Object.entries(d[src]||{})){const dt=ts.slice(0,10);if(dt<PERIOD[0]||dt>PERIOD[1])continue;(day[dt]=day[dt]||{})[k]=v}
  // the export's PoP split covers its whole range (it may include a day before the month): shares are used and bytes are scaled to the in-quarter total
  for(const [k,v] of Object.entries(d.GeoTrafficDistribution||{}))geo[k]=(geo[k]||0)+v}
const days=Object.keys(day).sort();
if(!days.length){console.error('no days inside '+PERIOD.join(' .. '));process.exit(1)}
const col=k=>days.map(d=>day[d][k]||0),raw={};for(const k of Object.keys(SERIES))raw[k]=col(k);
const sum=a=>a.reduce((x,y)=>x+y,0),mean=a=>sum(a)/a.length,imax=a=>a.indexOf(Math.max(...a)),imin=a=>a.indexOf(Math.min(...a));
const MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
const months=[...new Set(days.map(d=>d.slice(0,7)))].map(ym=>{const ix=days.map((d,i)=>d.startsWith(ym)?i:-1).filter(i=>i>=0),pick=a=>ix.map(i=>a[i]);
  const bw=pick(raw.bw),rq=pick(raw.rq),pb=imax(bw),pr=imax(rq);
  return {label:MONTHS[+ym.slice(5)-1],days:ix.length,bw_tb:sum(bw)/TB,cached_tb:sum(pick(raw.cached))/TB,rq_m:sum(rq)/M,og_tb:sum(pick(raw.og))/TB,og_pct:sum(pick(raw.og))/sum(bw)*100,chr:mean(pick(raw.chr)),ort:mean(pick(raw.ort)),pulls_m:sum(pick(raw.pulls))/M,peak_bw_day:days[ix[pb]],peak_bw:bw[pb]/TB,peak_rq_day:days[ix[pr]],peak_rq:rq[pr]/M,e3:sum(pick(raw.e3)),e4:sum(pick(raw.e4)),e5:sum(pick(raw.e5))}});
const gt=sum(Object.values(geo));
const cdn2={label:'Secondary CDN',coverage:days[0]+'/'+days[days.length-1],months,days,
  bw:raw.bw.map(v=>r(v/TB,3)),cached:raw.cached.map(v=>r(v/TB,3)),rq:raw.rq.map(v=>r(v/M,3)),og:raw.og.map(v=>r(v/TB,3)),chr:raw.chr.map(v=>r(v,2)),ort:raw.ort.map(v=>r(v,1)),pulls:raw.pulls.map(v=>r(v/M,3)),e3:raw.e3,e4:raw.e4,e5:raw.e5,
  total_tb:sum(raw.bw)/TB,cached_tb:sum(raw.cached)/TB,total_rq_m:sum(raw.rq)/M,total_og_tb:sum(raw.og)/TB,og_share:sum(raw.og)/sum(raw.bw)*100,chr_avg:mean(raw.chr),ort_avg:mean(raw.ort),total_pulls_m:sum(raw.pulls)/M,
  geo:Object.entries(geo).sort((a,b)=>b[1]-a[1]).map(([k,v])=>{const [region,pop]=k.includes(': ')?k.split(': '):['',k];return {pop,region,tb:v/gt*sum(raw.bw)/TB,share:v/gt*100}})};
const span=months.length===1?months[0].label+' 2026':months[0].label.slice(0,3)+'–'+months[months.length-1].label.slice(0,3)+' 2026';
const dm=s=>new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'});

// 1. dataset: "cdn2" is kept as the last key of q3data.json
const dsPath=path.join(ROOT,'2026/q3/q3data.json');let ds=fs.readFileSync(dsPath,'utf8');
const block='  "cdn2": '+JSON.stringify(cdn2,null,2).replace(/\n/g,'\n  ');
const ci=ds.indexOf(',\n  "cdn2": ');
ds=(ci>=0?ds.slice(0,ci):ds.replace(/\s*}\s*$/,''))+',\n'+block+'\n}\n';
if(!/"sources": \[[^\]]*"Secondary CDN"/.test(ds))ds=ds.replace('      "Apars CDN",\n','      "Apars CDN",\n      "Secondary CDN",\n');
fs.writeFileSync(dsPath,ds);

// 2. inline data of the pages: "cdn2" is kept as the last key of D
for(const f of ['2026/q3/index.html','index.html']){const p=path.join(ROOT,f),lines=fs.readFileSync(p,'utf8').split('\n');
  const li=lines.findIndex(l=>l.startsWith('const D = {'));if(li<0)throw new Error(f+': inline data not found');
  let L=lines[li];const j=L.indexOf(',"cdn2":');if(j>=0)L=L.slice(0,j)+'};';
  if(!/};$/.test(L))throw new Error(f+': unexpected end of inline data');
  lines[li]=L.replace(/};$/,',"cdn2":'+JSON.stringify(cdn2)+'};');fs.writeFileSync(p,lines.join('\n'))}

// 3. markdown subsection (report.md, llms-full.txt): replaced in place, kept just before section 06
const pct=v=>v.toFixed(2)+'%';
const e5=sum(raw.e5),e4=sum(raw.e4),e3=sum(raw.e3),p5=imax(raw.e5),pb=imax(raw.bw);
const geoLine=cdn2.geo.map(g=>`${g.pop} ${g.share>=0.01?g.share.toFixed(2)+'%':'<0.01%'}`).join(', ');
const md=[`### Secondary CDN (${span})`,'',
`A second CDN is reported separately from the primary Apars CDN figures above. ${span}: ${cdn2.total_tb.toFixed(1)} TB delivered over ${cdn2.total_rq_m.toFixed(1)}M requests; cached bytes ${cdn2.cached_tb.toFixed(1)} TB (${(cdn2.cached_tb/cdn2.total_tb*100).toFixed(1)}% of delivery); mean daily cache hit rate ${cdn2.chr_avg.toFixed(1)}%; origin traffic ${cdn2.total_og_tb.toFixed(1)} TB (${cdn2.og_share.toFixed(1)}% of delivery) across ${cdn2.total_pulls_m.toFixed(1)}M origin pulls; mean origin response ${cdn2.ort_avg.toFixed(0)} ms; peak day ${cdn2.bw[pb].toFixed(1)} TB on ${dm(days[pb])}. Errors: ${e5.toLocaleString('en-US')} 5xx (${(e5/sum(raw.rq)*100).toFixed(3)}% of requests; ${raw.e5[p5].toLocaleString('en-US')} on ${dm(days[p5])}), ${e4.toLocaleString('en-US')} 4xx, ${e3.toLocaleString('en-US')} 3xx.${months.length<3?' Remaining months of the quarter will be added as their exports arrive.':''}`,'',
'| Month | Bandwidth (TB) | Cached (TB) | Requests (M) | Cache hit rate | Avg origin response (ms) | Origin traffic (TB) | Origin share | Peak day |','|---|---|---|---|---|---|---|---|---|',
...months.map(m=>`| ${m.label} | ${m.bw_tb.toFixed(1)} | ${m.cached_tb.toFixed(1)} | ${m.rq_m.toFixed(1)} | ${pct(m.chr)} | ${m.ort.toFixed(0)} | ${m.og_tb.toFixed(1)} | ${m.og_pct.toFixed(1)}% | ${m.peak_bw.toFixed(1)} TB (${dm(m.peak_bw_day)}) |`),'',
`Traffic by PoP (share of delivered bytes): ${geoLine}.`,'','Daily secondary CDN metrics:','',
'| Date | Bandwidth (TB) | Cached (TB) | Requests (M) | Origin (TB) | Cache hit % | Origin resp. (ms) | 5xx |','|---|---|---|---|---|---|---|---|',
...days.map((d,i)=>`| ${d} | ${cdn2.bw[i].toFixed(2)} | ${cdn2.cached[i].toFixed(2)} | ${cdn2.rq[i].toFixed(2)} | ${cdn2.og[i].toFixed(3)} | ${cdn2.chr[i].toFixed(2)} | ${cdn2.ort[i].toFixed(0)} | ${cdn2.e5[i]} |`)].join('\n');
for(const f of ['2026/q3/report.md','2026/q3/llms-full.txt','llms-full.txt']){const p=path.join(ROOT,f);let s=fs.readFileSync(p,'utf8');
  const start=s.indexOf('\n### Secondary CDN'),end=s.indexOf('\n## 06 -');if(end<0)throw new Error(f+': section 06 heading not found');
  const prefix=start>=0?s.slice(0,start):s.slice(0,end);
  s=prefix.replace(/\n+$/,'')+'\n\n'+md+'\n'+s.slice(end);fs.writeFileSync(p,s)}

// 4. llms.txt one-liner
const line=`Secondary CDN (${span}${months.length<3?' so far':''}): ${cdn2.total_tb.toFixed(1)} TB delivered over ${cdn2.total_rq_m.toFixed(1)}M requests at ${cdn2.chr_avg.toFixed(1)}% mean daily cache hit; origin traffic ${cdn2.total_og_tb.toFixed(1)} TB (${cdn2.og_share.toFixed(1)}%); Singapore PoP ${cdn2.geo[0].share.toFixed(1)}%. Reported separately from the primary Apars CDN figures.`;
for(const f of ['2026/q3/llms.txt','llms.txt']){const p=path.join(ROOT,f);let s=fs.readFileSync(p,'utf8');
  if(/^Secondary CDN \(/m.test(s))s=s.replace(/^Secondary CDN \(.*$/m,line);
  else{const k=s.includes('\nRecognition: ')?'\nRecognition: ':'\nWhen citing, attribute';s=s.replace(k,'\n'+line+'\n'+k)}
  fs.writeFileSync(p,s)}
console.log(`cdn2: ${days.length} days (${cdn2.coverage}), ${months.map(m=>m.label).join(', ')}: ${cdn2.total_tb.toFixed(1)} TB, ${cdn2.total_rq_m.toFixed(1)}M requests, chr ${cdn2.chr_avg.toFixed(2)}%`);

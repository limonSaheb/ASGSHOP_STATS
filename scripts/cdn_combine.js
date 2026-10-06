#!/usr/bin/env node
// Combine the Apars CDN delivery zones into the single "cdn" series of the Q3 report.
//
//   node scripts/cdn_combine.js
//
// Inputs (2026/q3/raw): cdn-zone1-q3.json, the first zone's daily series as published, and
// cdn-zone2-2026-MM.json, the second zone's monthly statistics exports. Days outside the quarter
// are dropped. Per day: bandwidth, requests, origin traffic and 5xx are summed; cache hit rate is
// weighted by requests; origin response time is weighted by estimated origin requests
// (requests x (1 - cache hit rate)). The script rewrites the "cdn" block of q3data.json and of the
// inline data in 2026/q3/index.html and index.html, live.share_of_cdn, the monthly and daily tables
// of section 05 in report.md and llms-full.txt, and the CDN values in the page's structured data.
// Re-running it is a no-op.
const fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..'),RAW=path.join(ROOT,'2026/q3/raw'),PERIOD=['2026-07-01','2026-09-30'];
const TB=1e12,M=1e6,r=(v,d)=>+v.toFixed(d),sum=a=>a.reduce((x,y)=>x+y,0),mean=a=>sum(a)/a.length,imax=a=>a.indexOf(Math.max(...a));
const z1=JSON.parse(fs.readFileSync(path.join(RAW,'cdn-zone1-q3.json'),'utf8'));
const files=fs.readdirSync(RAW).filter(f=>/^cdn-zone2-\d{4}-\d{2}\.json$/.test(f)).sort();
if(!files.length){console.error('no cdn-zone2-*.json exports in '+RAW);process.exit(1)}
const SERIES={bw:'BandwidthUsedChart',rq:'RequestsServedChart',og:'OriginTrafficChart',chr:'CacheHitRateChart',ort:'OriginResponseTimeChart',e5:'Error5xxChart'};
const day={},sgMonth={};
for(const f of files){const d=JSON.parse(fs.readFileSync(path.join(RAW,f),'utf8')),ym=f.slice(10,17);
  for(const [k,src] of Object.entries(SERIES))for(const [ts,v] of Object.entries(d[src]||{})){const dt=ts.slice(0,10);if(dt<PERIOD[0]||dt>PERIOD[1])continue;(day[dt]=day[dt]||{})[k]=v}
  const geo=d.GeoTrafficDistribution||{},gt=sum(Object.values(geo));sgMonth[ym]=gt?(geo['Asia: Singapore, SG']||0)/gt*100:0}
const days=z1.days;
for(const d of days)if(!day[d])throw new Error('zone 2 has no data for '+d);
const z2={};for(const k of Object.keys(SERIES))z2[k]=days.map(d=>day[d][k]);
z2.bw=z2.bw.map(v=>v/TB);z2.rq=z2.rq.map(v=>v/M);z2.og=z2.og.map(v=>v/TB);
const bw=days.map((_,i)=>r(z1.bw[i]+z2.bw[i],3)),rq=days.map((_,i)=>r(z1.rq[i]+z2.rq[i],3)),og=days.map((_,i)=>r(z1.og[i]+z2.og[i],3));
const chr=days.map((_,i)=>r((z1.rq[i]*z1.chr[i]+z2.rq[i]*z2.chr[i])/(z1.rq[i]+z2.rq[i]),2));
const w1=days.map((_,i)=>z1.rq[i]*(1-z1.chr[i]/100)),w2=days.map((_,i)=>z2.rq[i]*(1-z2.chr[i]/100));
const ort=days.map((_,i)=>r((w1[i]*z1.ort[i]+w2[i]*z2.ort[i])/(w1[i]+w2[i]),1));
const e5=days.map((_,i)=>z1.e5[i]+z2.e5[i]);
const months=z1.months.map(m1=>{const ym={July:'2026-07',August:'2026-08',September:'2026-09'}[m1.label];const ix=days.map((d,i)=>d.startsWith(ym)?i:-1).filter(i=>i>=0),p=a=>ix.map(i=>a[i]);
  const b=p(bw),q=p(rq),pb=imax(b),pr=imax(q),b2=sum(p(z2.bw)),b1=sum(b)-b2;
  return {label:m1.label,bw_tb:sum(b),rq_m:sum(q),og_tb:sum(p(og)),og_pct:sum(p(og))/sum(b)*100,chr:mean(p(chr)),ort:mean(p(ort)),peak_bw_day:days[ix[pb]],peak_bw:b[pb],peak_rq_day:days[ix[pr]],peak_rq:q[pr],sg_share:(b1*m1.sg_share+b2*sgMonth[ym])/(b1+b2)}});
const cdn={zones:2,method:'daily series summed across delivery zones; cache hit rate weighted by requests; origin response weighted by estimated origin requests',months,days,bw,rq,og,chr,ort,e5,
  total_pb:sum(bw)/1000,total_rq_b:sum(rq)/1000,total_og_tb:sum(og),chr_avg:mean(chr),og_share:sum(og)/sum(bw)*100};

// 1. dataset: replace the "cdn" block in place, drop any "cdn2" block, update live.share_of_cdn
const dsPath=path.join(ROOT,'2026/q3/q3data.json');let ds=fs.readFileSync(dsPath,'utf8');
const live=JSON.parse(ds).live,share=live.bw_tb/sum(bw)*100;
const a=ds.indexOf('\n  "cdn": {'),b=ds.indexOf('\n  "live": {');if(a<0||b<0||b<a)throw new Error('dataset: cdn/live blocks not found');
ds=ds.slice(0,a)+'\n  "cdn": '+JSON.stringify(cdn,null,2).replace(/\n/g,'\n  ')+','+ds.slice(b);
const c2=ds.indexOf(',\n  "cdn2": ');if(c2>=0)ds=ds.slice(0,c2)+'\n}\n';
ds=ds.replace(/"share_of_cdn": [0-9.]+/,'"share_of_cdn": '+share).replace('      "Apars CDN",\n      "Secondary CDN",\n','      "Apars CDN",\n');
fs.writeFileSync(dsPath,ds);

// 2. pages: inline data and structured data
for(const f of ['2026/q3/index.html','index.html']){const p=path.join(ROOT,f),lines=fs.readFileSync(p,'utf8').split('\n');
  const li=lines.findIndex(l=>l.startsWith('const D = {'));if(li<0)throw new Error(f+': inline data not found');
  const D=JSON.parse(lines[li].slice('const D = '.length,-1));D.cdn=cdn;delete D.cdn2;D.live.share_of_cdn=share;
  lines[li]='const D = '+JSON.stringify(D)+';';
  const ld=lines.findIndex(l=>l.startsWith('<script type="application/ld+json">'));if(ld<0)throw new Error(f+': ld+json');
  lines[ld]=lines[ld].replace(/("name":"CDN bandwidth delivered","value":)[0-9.]+/,'$1'+r(sum(bw),1)).replace(/("name":"CDN requests","value":)[0-9]+/,'$1'+Math.round(sum(rq)*M)).replace(/("name":"Cache hit rate \(mean daily\)","value":)[0-9.]+/,'$1'+r(mean(chr),2));
  fs.writeFileSync(p,lines.join('\n'))}

// 3. markdown tables of section 05 (report.md, llms-full.txt); any "Secondary CDN" subsection is removed
const dm=s=>new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'});
const tbl=['| Month | Bandwidth (TB) | Requests (M) | Cache hit rate | Avg origin response (ms) | Origin traffic (TB) | Origin share | Peak day |','|---|---|---|---|---|---|---|---|',
  ...months.map(m=>`| ${m.label} | ${m.bw_tb.toFixed(1)} | ${m.rq_m.toFixed(1)} | ${m.chr.toFixed(2)}% | ${m.ort.toFixed(0)} | ${m.og_tb.toFixed(1)} | ${m.og_pct.toFixed(1)}% | ${m.peak_bw.toFixed(1)} TB (${dm(m.peak_bw_day)}) |`),'','Daily edge metrics (all zones):','',
  '| Date | Bandwidth (TB) | Requests (M) | Origin (TB) | Cache hit % | Origin resp. (ms) | 5xx |','|---|---|---|---|---|---|---|',
  ...days.map((d,i)=>`| ${d} | ${bw[i].toFixed(2)} | ${rq[i].toFixed(2)} | ${og[i].toFixed(3)} | ${chr[i].toFixed(2)} | ${ort[i].toFixed(0)} | ${e5[i]} |`)].join('\n');
for(const f of ['2026/q3/report.md','2026/q3/llms-full.txt','llms-full.txt']){const p=path.join(ROOT,f);let s=fs.readFileSync(p,'utf8');
  const sec=s.indexOf('\n## 05 -'),end=s.indexOf('\n## 06 -'),start=s.indexOf('\n| Month',sec);if(sec<0||end<0||start<0||start>end)throw new Error(f+': section 05 tables not found');
  s=s.slice(0,start)+'\n'+tbl+'\n'+s.slice(end);fs.writeFileSync(p,s)}
for(const f of ['2026/q3/llms.txt','llms.txt']){const p=path.join(ROOT,f);let s=fs.readFileSync(p,'utf8');s=s.replace(/\nSecondary CDN \(.*\n/,'');fs.writeFileSync(p,s)}
console.log(`cdn: ${days.length} days, ${cdn.total_pb.toFixed(3)} PB, ${cdn.total_rq_b.toFixed(3)}B requests, chr ${cdn.chr_avg.toFixed(2)}%, origin ${cdn.total_og_tb.toFixed(1)} TB (${cdn.og_share.toFixed(1)}%), live share ${share.toFixed(1)}%`);

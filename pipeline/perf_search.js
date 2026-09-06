// PERFORMANCE GATE for search and the dictionary panel — the number that can
// regress.  Written 2026-09-05, because until then there was none
// (claude/search_and_dictionary_speed_brief.md §7).
//
// WHAT IS MEASURED, per query, through the pages' OWN code paths (jsdom boots
// search.html, reader2.html and panel.js exactly as check_search.js and
// check_lookup_reach.js do):
//
//   req    requests made
//   raw    bytes the browser would have to PARSE (file size on disk)
//   gz     bytes that would cross the wire — gzip -6 of each file, which is
//          what GitHub Pages and Cloudflare send (measured live 2026-09-05:
//          encodedBodySize/decodedBodySize = 0.19–0.25 on every /index/ file;
//          R2 answers with zstd at about the same ratio).  So `gz` IS the
//          transfer cost and `raw` is the parse cost; both matter, on a phone
//          the second more.
//   waves  the DEPENDENT ROUND TRIPS: every fetch here takes LAT ms to
//          resolve, so a query that must wait for A before asking for B costs
//          two waves.  wall/LAT, rounded.  This is the dictionary's whole
//          cost — its files are small and its chain was six deep.
//   ms     wall time in jsdom (parse + compute + LAT×waves).  Reported, not
//          gated: it is a laptop number, not the phone's.
//   max    the LARGEST SINGLE FILE the query fetched, raw bytes.  Gated at an
//          absolute MAXFILE, not against the baseline: a phone must hold and
//          scan each file whole.  The postings shards are ≤ 515 KB, the text
//          chunks ≤ 301 KB, and `index/names.json` — the section names,
//          scanned on every search, fetched once per page — WAS 1.09 MB, the
//          largest file a search read, and the ceiling sat just above it at
//          1.25 MB.  `k.txt`, the substring / `*`-suffix sweep surface, was
//          12.5 MB — lever 3 of the brief.  Added 2026-09-05 (later session);
//          red on the two sweep queries before `tg/` existed.  (A first cut
//          at 1 MB went red on EVERY cold query, which is how names.json's
//          size was noticed.)  2026-09-05, fourth session: the names are
//          read as ONE `tn/` shard (≤ 200 KB) and the ceiling is 520 KB —
//          just above the largest postings shard; red on every cold query
//          before `tn/` existed.
//
// THE QUERY SET is the one §7 of the brief asks for: cold first search and
// warm; a median word; a `pa`/`sa` word; the common word that pulls every
// volume; both wildcard shapes; a substring sweep; a phrase; and a word typed
// without diacritics.  Each is measured on a FRESH page (cold) except the one
// marked warm, which repeats the previous query on the same page.
//
//   node pipeline/perf_search.js            compare against perf_baseline.json;
//                                           FAIL on any query whose gz bytes or
//                                           request count grew past the slack
//   node pipeline/perf_search.js --record   rewrite the baseline (do this ONLY
//                                           together with a change that is
//                                           meant to move the numbers, and say
//                                           so in the commit)
//   node pipeline/perf_search.js --lat 0    no simulated latency (faster run;
//                                           waves then read 0)
//
// A perf change that ALTERS RESULTS is a correctness regression, not a perf
// win: check_search.js is the gate for that, and it must be run alongside.
const fs=require('fs'),path=require('path'),zlib=require('zlib');const {JSDOM}=require('jsdom');
const ROOT=path.dirname(__dirname);
const SITE=path.join(ROOT,'site');
const BASE=path.join(__dirname,'perf_baseline.json');
const RECORD=process.argv.includes('--record');
const li=process.argv.indexOf('--lat'); const LAT=li>=0?+process.argv[li+1]:40;
const STORE=fs.existsSync(path.join(ROOT,'stores/lookup/index.json'))?'stores':'site';
const isStore=p=>/^lookup(_eval)?\//.test(p);
const MAXFILE=520_000;     // raw bytes: no single fetch by a SEARCH may exceed this (largest postings shard 514 KB; names.json, 1.09 MB, was the ceiling until tn/)
// the dictionary's largest file is `lookup_eval/index.json`, 653 KB, on R2 —
// a store change (r2_upload.sh + WLV) that this gate records as an open item
// rather than hides: the lookup rows get their own ceiling, just above it
const MAXSTORE=700_000;
const wait=ms=>new Promise(r=>setTimeout(r,ms));

// gzip -6 size of a file, cached by path+size+mtime
const GZC={};
function gzSize(f,buf){ const st=fs.statSync(f); const k=f+':'+st.size+':'+st.mtimeMs;
  if(GZC[k]==null) GZC[k]=zlib.gzipSync(buf,{level:6}).length; return GZC[k]; }

function mkResolve(base){ return u=>{ u=String(u).split('?')[0];
  if(u.startsWith('../')){ const p=u.slice(3); return path.join(isStore(p)?path.join(ROOT,STORE):SITE,p); }
  if(u.startsWith('http')){ let p=u; try{p=new URL(u).pathname.replace(/^\//,'');}catch(e){}
    return isStore(p)?path.join(ROOT,STORE,p):path.join(base,p); }
  return path.join(base,u); }; }
function inlineScripts(html,resolve){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    return t==null?m:'<script>'+t+'</script>'; });
}
// the instrumented window: every fetch is counted, sized, and delayed LAT ms
function boot(file,base,url){
  const resolve=mkResolve(base);
  const log={req:0,raw:0,gz:0,paths:[],sizes:[]};
  const dom=new JSDOM(inlineScripts(fs.readFileSync(file,'utf8'),resolve),{runScripts:'dangerously',pretendToBeVisual:true,url:url||'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
    w.__log=log;
    w.fetch=async u=>{ const f=resolve(u); let b=null; try{b=fs.readFileSync(f);}catch(e){}
      log.req++; log.paths.push(String(u).split('?')[0]); log.sizes.push(b?b.length:0);
      if(b){ log.raw+=b.length; log.gz+=gzSize(f,b); }
      if(LAT) await wait(LAT);
      return {ok:b!=null,status:b!=null?200:404,
        json:()=>Promise.resolve(b?JSON.parse(b.toString('utf8')):{}),
        text:()=>Promise.resolve(b?b.toString('utf8'):''),
        arrayBuffer:()=>Promise.resolve(b?b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength):new ArrayBuffer(0))}; };
  }});
  return dom.window;
}
const snap=l=>({req:l.req,raw:l.raw,gz:l.gz});
// the largest single file among the fetches made since snapshot `a`
const diff=(a,b,l)=>({req:b.req-a.req,raw:b.raw-a.raw,gz:b.gz-a.gz,max:Math.max(0,...l.sizes.slice(a.req))});
const mb=n=>(n/1e6).toFixed(2);

async function readyReader(w){ for(let k=0;k<100;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

// ------------------------------------------------------------ the query set
const QUERIES=[
  ['cold median word',     'yamakasālānaṁ',      {cold:true}],
  ['warm, same word',      'yamakasālānaṁ',      {warmAfter:'yamakasālānaṁ'}],
  ['pa- word',             'paṭisambhidā',       {cold:true}],
  ['common word (117 vols)','tassā',             {cold:true}],
  ['prefix wildcard',      'dhamm*',             {cold:true}],
  ['suffix wildcard',      '*vaggo',             {cold:true}],
  ['substring sweep',      'amakasālāna',        {cold:true}],
  ['phrase',               'evaṁ me sutaṁ',      {cold:true}],
  ['no diacritics typed',  'nibbana',            {cold:true}],
];

async function measureSearch(){
  const out={};
  for(const [label,q,o] of QUERIES){
    const s=boot(path.join(SITE,'search.html'),SITE);
    await wait(200);
    const run=async v=>{ s.document.getElementById('q').value=v; const t0=Date.now(); await s.run(); return Date.now()-t0; };
    if(o.warmAfter) await run(o.warmAfter);
    const a=snap(s.__log); const ms=await run(q); const d=diff(a,snap(s.__log),s.__log);
    const st=s.document.getElementById('status').textContent;
    const ktxt=s.__log.paths.slice(-d.req).some(p=>/tp\/k\.txt$/.test(p));
    out['search: '+label]={q,req:d.req,raw:d.raw,gz:d.gz,max:d.max,ms,waves:LAT?Math.round(ms/LAT):0,ktxt,status:st.slice(0,90)};
    s.close();
  }
  // reader2's box: the cold and the common word, so drift between the two
  // implementations shows up here as well as in check_search.js
  for(const [label,q] of [['cold median word','yamakasālānaṁ'],['common word (117 vols)','tassā']]){
    const w=boot(path.join(SITE,'reader/reader2.html'),path.join(SITE,'reader'));
    if(!await readyReader(w)){ out['reader: '+label]={error:'reader did not boot'}; continue; }
    const a=snap(w.__log); const t0=Date.now(); await w.doSearch(q); const ms=Date.now()-t0; const d=diff(a,snap(w.__log),w.__log);
    const head=[...w.document.querySelectorAll('.sr-head')].map(h=>h.textContent)[0]||'';
    out['reader: '+label]={q,req:d.req,raw:d.raw,gz:d.gz,max:d.max,ms,waves:LAT?Math.round(ms/LAT):0,status:head.slice(0,90)};
    w.close();
  }
  return out;
}

async function measureLookup(){
  const out={};
  // a common word and a lemma-only word (the class check_lookup_reach.js guards)
  for(const [label,word] of [['cold common word','tathāgato'],['warm, second word','bhagavā'],['lemma-only word','atappaka']]){
    const w=boot(path.join(SITE,'reader/reader2.html'),path.join(SITE,'reader'),'http://x/?wl=1');
    if(!await readyReader(w)){ out['lookup: '+label]={error:'reader did not boot'}; continue; }
    const para=w.document.querySelector('.para')||w.document.body;
    const done=()=>new Promise(res=>{ const el=w.document.getElementById('wl'); let n=0;
      const t=setInterval(()=>{ n++; if((el&&el.dataset.state&&el.dataset.state!=='loading')||n>400){ clearInterval(t); res(); } },10); });
    if(label.startsWith('warm')){ await w.WL.lookup('tathāgato',para); await done(); }
    const a=snap(w.__log); const t0=Date.now(); await w.WL.lookup(word,para); await done(); const ms=Date.now()-t0;
    const d=diff(a,snap(w.__log),w.__log);
    const hdr=(w.document.getElementById('wlc')||{}).textContent||'';
    out['lookup: '+label]={q:word,req:d.req,raw:d.raw,gz:d.gz,max:d.max,ms,waves:LAT?Math.round(ms/LAT):0,status:hdr.slice(0,90)};
    w.close();
  }
  return out;
}

(async()=>{
  console.log('perf: LAT='+LAT+'ms per fetch; store='+STORE);
  const res=Object.assign({},await measureSearch(),await measureLookup());
  const base=(!RECORD&&fs.existsSync(BASE))?JSON.parse(fs.readFileSync(BASE,'utf8')).results:null;
  console.log('\n  '+'query'.padEnd(34)+'req'.padStart(5)+'raw MB'.padStart(9)+'gz MB'.padStart(8)+'max MB'.padStart(8)+'waves'.padStart(7)+'ms'.padStart(7)+(base?'   vs baseline':'')+'  status');
  let fails=0;
  for(const k in res){ const r=res[k];
    if(r.error){ console.log('  '+k.padEnd(34)+'  ERROR '+r.error); fails++; continue; }
    let cmp='';
    if(base&&base[k]&&!base[k].error){ const b=base[k];
      // bytes may not grow past 10 % (+50 KB slack); requests not past 25 %
      // (+10).  The 2026-09-05 redesign traded 40 MB of volume shards for a
      // few hundred small chunk fetches on purpose, so the two are gated
      // separately rather than as one score.
      const gzOk=r.gz<=b.gz*1.10+50000, reqOk=r.req<=b.req*1.25+10;
      cmp=('  gz '+(r.gz>=b.gz?'+':'')+mb(r.gz-b.gz)+' req '+(r.req>=b.req?'+':'')+(r.req-b.req)).padEnd(24);
      if(!(gzOk&&reqOk)){ cmp+=' FAIL'; fails++; }
    }
    // absolute, baseline or not: no single file over MAXFILE
    const cap=k.startsWith('lookup')?MAXSTORE:MAXFILE;
    if(r.max>cap){ cmp+=' FAIL max>'+mb(cap)+'MB'; fails++; }
    console.log('  '+k.padEnd(34)+String(r.req).padStart(5)+mb(r.raw).padStart(9)+mb(r.gz).padStart(8)+mb(r.max||0).padStart(8)+String(r.waves).padStart(7)+String(r.ms).padStart(7)+cmp+'  '+(r.ktxt?'[k.txt] ':'')+r.status);
  }
  if(RECORD){ fs.writeFileSync(BASE,JSON.stringify({recorded:new Date().toISOString().slice(0,10),lat:LAT,results:res},null,1)); console.log('\nbaseline written: '+path.relative(ROOT,BASE)); }
  else if(!base) console.log('\nno baseline yet — run with --record');
  console.log(fails?('\nFAILED: '+fails):'\nall within baseline');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('threw: '+(e&&e.stack||e)); process.exit(1); });

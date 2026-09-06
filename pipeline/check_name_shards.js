// GATE: the section-name shards (index/tn/) answer exactly what names.json
// answers — same labels, same rows, same order — for every query shape the
// two search UIs can pose.
//
// 2026-09-05 (fourth session).  `searchcore.js names(fq)` reads one n-gram
// shard instead of the 1.09 MB file and hands the page an object of the
// file's shape holding only the candidates.  The page's substring test then
// decides every hit, so the result can differ from the whole-file path only
// if the gram narrowed too far — which is exactly what this checks: random
// substrings of real labels (with and without diacritics, in both modes),
// whole labels, multi-word fragments, digits-only and one-letter queries
// (the fallback), and strings no label contains.
//
// Usage:  node pipeline/check_name_shards.js [--n 500]
const fs=require('fs'),path=require('path'),vm=require('vm');
const ROOT=path.dirname(__dirname), SITE=path.join(ROOT,'site');
const ni=process.argv.indexOf('--n'); const NQ=ni>=0?+process.argv[ni+1]:500;

// searchcore.js in a bare context with a file-backed fetch
const ctx={window:{}, console};
ctx.fetch=async u=>{ const f=path.join(SITE,String(u).split('?')[0]); let b=null; try{b=fs.readFileSync(f,'utf8');}catch(e){}
  ctx.__fetched.push(String(u).split('?')[0]);
  return {ok:b!=null,status:b!=null?200:404,json:async()=>JSON.parse(b),text:async()=>b}; };
ctx.__fetched=[];
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(SITE,'searchcore.js'),'utf8'),ctx);
const SC=ctx.window.SearchCore;
const S=SC.create({base:'index/'});
const D=JSON.parse(fs.readFileSync(path.join(SITE,'index','names.json'),'utf8'));

// the page's rule, over any names-shaped object: matching rows, in the
// object's own order (the pages sort with a stable comparator afterwards, so
// equal candidate order means equal painted order)
function hits(N,fq,fold){
  const NN=N.labels.map(fold?SC.foldS:SC.canonS);
  const keep=new Set(); for(let i=0;i<NN.length;i++) if(NN[i].indexOf(fq)>=0) keep.add(i);
  return N.rows.filter(r=>keep.has(r[0])).map(r=>N.labels[r[0]]+'|'+N.vols[r[1]]+'|'+r[2]+'|'+N.layers[r[3]]);
}
// deterministic pseudo-random, so a failure is reproducible
let seed=20260905; const rnd=n=>{ seed=(seed*1103515245+12345)&0x7fffffff; return seed%n; };
const L=D.labels;
const queries=[];
for(let k=0;k<NQ;k++){
  const lab=L[rnd(L.length)]; const c=SC.canonS(lab);
  const shape=k%8;
  if(shape===0) queries.push(c);                                   // the whole label
  else if(shape===1){ const a=rnd(Math.max(1,c.length-3)); queries.push(c.slice(a,a+2+rnd(6))); }   // a short substring
  else if(shape===2){ const a=rnd(Math.max(1,c.length-8)); queries.push(c.slice(a,a+6+rnd(10))); }  // a longer one
  else if(shape===3){ const a=rnd(Math.max(1,c.length-3)); queries.push(SC.foldS(c.slice(a,a+3+rnd(6)))); } // typed without diacritics
  else if(shape===4) queries.push(c.replace(/^\d+(-\d+)?\.\s*/,''));  // the label without its number
  else if(shape===5){ const w=c.split(/\s+/); queries.push(w.slice(Math.max(0,w.length-2)).join(' ')); } // its last words
  else if(shape===6) queries.push(c.slice(-4));                     // its tail
  else queries.push(c.slice(0,1+rnd(2)));                            // one or two letters
}
queries.push('1.','12','', 'zzzq','xkcd','sutta','vagga','vaṇṇanā','a b','ṭ','(dutiyo)','mahā-','–');
(async()=>{
  let n=0, diffs=0, fallback=0, empty=0, shards=new Set();
  for(const q of queries) for(const fold of [false,true]){
    const fq=(fold?SC.foldS:SC.canonS)(q).trim();
    const before=ctx.__fetched.length;
    const N=await S.names(fq);
    const used=ctx.__fetched.slice(before);
    if(N===undefined){ fallback++; if(!used.length&&/[a-z]{2}/.test(SC.foldS(fq))) { console.log('  FAIL  fallback on a query with a gram: '+JSON.stringify(q)); diffs++; } continue; }
    if(N===null){ console.log('  FAIL  names() failed for '+JSON.stringify(q)); diffs++; continue; }
    used.forEach(u=>{ const m=u.match(/tn\/([a-z_]+)\.json/); if(m) shards.add(m[1]); });
    if(!N.labels.length) empty++;
    const got=hits(N,fq,fold), want=hits(D,fq,fold);
    n++;
    if(got.length!==want.length||got.some((x,i)=>x!==want[i])){
      diffs++; console.log('  FAIL  '+JSON.stringify(q)+(fold?' (folded)':'')+': '+got.length+' rows vs '+want.length);
    }
  }
  console.log(`${n} query × mode combinations against names.json: ${diffs} difference(s); ${fallback} fell back to names.json (no gram); ${empty} proved empty by the manifest; ${shards.size} distinct shards read`);
  if(!ctx.__fetched.some(u=>/tn\/index\.json/.test(u))){ console.log('  FAIL  the tn/ manifest was never fetched'); diffs++; }
  console.log(diffs?'FAILED: '+diffs:'all green');
  process.exit(diffs?1:0);
})();

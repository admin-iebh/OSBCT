// OSBCT search core — ONE implementation for search.html and reader2.html.
// ---------------------------------------------------------------------------
// WRITTEN 2026-09-05.  The two pages carried two copies of the same search
// and the gate exists because they drifted (check_search.js, 2026-08-08).
// This file is the copy; the pages keep only their UI.
//
// WHAT CHANGED THAT DAY, AND WHY IT IS ONE CHANGE, NOT TWO
//
// 1. DIACRITICS ARE MATCHED EXACTLY BY DEFAULT.  Reader: "in Pāḷi `tassa` and
//    `tassā` are different words".  Every index key used to be folded
//    (`tassā` -> `tassa`), so either query reported both — 36,644 where
//    `tassā` alone is 4,322.  The keys are now the printed tokens (NFC, lower
//    case, ṃ written as the edition's ṁ), a query is canonicalised the same
//    way and matched by identity.  Folding — `nibbana` finds `nibbāna` — is a
//    SWITCH (`fold:true`), resolved here from the exact keys, and the result
//    always says which mode produced it: a count is meaningless if you cannot
//    tell which question produced it.
//
// 2. A SEARCH NO LONGER DOWNLOADS THE VOLUMES IT HITS.  Measured live before
//    this change: `tassā` fetched 117 `<VOL>.idx.json`, 43 MB gzipped and
//    194 MB parsed, because postings and paragraph text shared a file.  Now:
//      index/tp/index.json    the manifest — volumes, layers, shard names,
//                             and each volume's text-chunk starts
//      index/tp/<name>.json   {terms:{key:{volIdx:[[paraIdx,count],…]}}} —
//                             every key whose FOLDED form starts with <name>;
//                             one fetch counts a word across the whole canon
//      index/tp/k.txt         every key, sorted, one per line — the sweep
//                             surface for substrings and *-suffixes UNTIL
//                             later the same day; now the fallback only
//      index/tg/<gram>.txt    (later 2026-09-05) the keys containing one
//                             folded n-gram — a substring or `*vaggo` sweep
//                             fetches the query's cheapest gram (≤ 500 KB,
//                             was 12.5 MB) and verifies each key itself
//      index/tn/<gram>.json   (fourth session) the section names containing
//                             one folded n-gram, with their rows — a search
//                             reads its cheapest gram (≤ 200 KB) instead of
//                             the whole 1.09 MB names.json, now the fallback
//      index/tx/<VOL>/<i>.json the paragraphs of one volume, chunked — fetched
//                             only for the rows that are DRAWN, or for the
//                             candidates of a phrase that must be verified
//    The per-volume shards and `terms.compact.json` remain as the LEGACY path
//    (manifest 404 = an unpacked deposit from before this date) and as the
//    gates' ground truth; `legacy` below is that whole older algorithm.
//
// The two changes are one because folding widened every lookup — an unaccented
// query had to reach every accented key — and the store had to be rebuilt for
// the exact keys anyway.  pipeline/perf_search.js holds the before and after.
//
// USED BY:  const S=SearchCore.create({base:'index/', bust:u=>u+'?v='+BUILD});
//           const r=await S.search('tassā', {fold:false, layer:'', capP:70, capA:35});
// Returns null when the index could not be loaded (never cached — the next
// call retries), else {words, mode, vis, total, phrParas, phrVols, andTotal,
// phrOut:[{vi,vol,lay,p}], andOut:[…], capped:[{word,matched,used}], legacy}.
// `capped` names any word whose match list was cut at 500 forms, so the page
// can say so instead of presenting a truncated count as a total.  `norm(s)` is the text
// normaliser for the mode, for snippets and section names.
window.SearchCore=(function(){
'use strict';
const FOLDM={'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'};
const foldS=s=>(s||'').normalize('NFC').toLowerCase().replace(/[āīūṁṃṅñṭḍṇḷ]/g,c=>FOLDM[c]||c);
// the edition prints ṁ; the modern ṃ is the reader's display convention only
const canonS=s=>(s||'').normalize('NFC').toLowerCase().replace(/ṃ/g,'ṁ');
const rxEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
// `*` against a KEY is `.*` (a key is one word); against RUNNING TEXT it is
// `\S*`, or `dhamm* ti` would let the star cross a word boundary
const wpat=w=>w.indexOf('*')>=0?w.split('*').map(rxEsc).join('\\S*'):rxEsc(w);
const kpat=w=>'^'+w.split('*').map(rxEsc).join('.*')+'$';
const LRANK={'pali-unicode':0,'atthakatha-unicode':1,'tika-unicode':2};
const CAPKEYS=500;   // a sweep stops at this many keys, as it always has
// A PHRASE IS CONSECUTIVE TOKENS (2026-09-06).  Until then a phrase was a
// substring of the normalised text — `indexOf('tassa bhagavato')` — which
// counted *etassa bhagavato* (63 paragraphs) and refused *dhammā”ti* for
// `dhammā ti`, because the edition closes the quotative up against its word
// and the substring wanted a space.  Now the paragraph is tokenised exactly
// as the index builder tokenises it (`_TOK` in build_search_index.py), each
// word matches a token the way the single-word search does — the keys it
// resolved to — and the words must follow each other, whatever the edition
// prints between them.  Measured for both rules by
// pipeline/measure_phrase_semantics.py; the result line names the rule.
const TOKRX=/[^a-zāīūṁṃṅñṇṭḍḷ]+/;
const phraseCount=(text,sets)=>{ const toks=canonS(text).split(TOKRX); let n=0;
  for(let j=0;j+sets.length<=toks.length;j++){ let all=true;
    for(let i=0;i<sets.length;i++) if(!sets[i].has(toks[j+i])){ all=false; break; }
    if(all) n++; } return n; };

function create(opts){
  const base=opts.base, bust=opts.bust||(u=>u);
  let MAN=null, MANERR=null;           // the tp/ manifest
  let TERMS=null, TERMSERR=null;       // legacy: terms.compact.json
  const SH={}, FM={}, CH={}, IDX={};   // shard, fold-map, chunk and legacy-shard caches
  let KTXT=null, KFOLD=null;

  // ---- loading: failures are never cached as answers ---------------------
  async function ensure(){
    if(MAN||TERMS) return;
    try{
      const r=await fetch(bust(base+'tp/index.json'));
      if(r.ok){ const j=await r.json();
        if(j&&j.vols&&j.layers&&j.shards&&j.tx){ MAN=j; MANERR=null; return; }
        throw new Error('malformed manifest'); }
      if(r.status===404){ await ensureLegacy(); return; }
      throw new Error('HTTP '+r.status);
    }catch(e){ MANERR=(e&&e.message)||String(e); if(!TERMS) await ensureLegacy(); }
  }
  async function ensureLegacy(){
    if(TERMS) return;
    try{ const r=await fetch(bust(base+'terms.compact.json'));
      if(!r.ok) throw new Error('HTTP '+r.status);
      const j=await r.json(); if(!j||!j.terms||!j.vols) throw new Error('malformed index');
      TERMS=j; TERMSERR=null;
    }catch(e){ TERMS=null; TERMSERR=(e&&e.message)||String(e); }
  }
  const ready=()=>!!(MAN||TERMS);
  const error=()=>MANERR||TERMSERR||null;
  const vols=()=>MAN?MAN.vols:(TERMS?TERMS.vols:null);
  const layers=()=>MAN?MAN.layers:(TERMS?TERMS.layers:null);

  function shardName(f){ const m=MAN.shards;
    for(let d=2;d<=40;d++){ const n=(f.slice(0,d)+'_'.repeat(d)).slice(0,d); if(m[n]) return n; }
    return null; }
  function shard(name){ if(SH[name]) return SH[name];
    return SH[name]=(async()=>{ try{
        const r=await fetch(bust(base+'tp/'+name+'.json'));
        if(r.status===404) return {};
        if(!r.ok) throw new Error('HTTP '+r.status);
        return (await r.json()).terms||{};
      }catch(e){ delete SH[name]; return null; } })(); }
  // fold -> [exact keys] for one shard, built once
  function foldMap(name,terms){ if(FM[name]) return FM[name];
    const m={}; for(const k in terms){ const f=foldS(k); (m[f]=m[f]||[]).push(k); }
    return FM[name]=m; }
  function keys(){ if(KTXT) return KTXT;
    return KTXT=(async()=>{ try{
        const r=await fetch(bust(base+'tp/k.txt'));
        if(!r.ok) throw new Error('HTTP '+r.status);
        return await r.text();
      }catch(e){ KTXT=null; return null; } })(); }
  // the folded key string, same length and offsets as the exact one
  async function keysFolded(){ const t=await keys(); if(t==null) return null;
    if(KFOLD==null) KFOLD=foldS(t); return KFOLD; }
  // ---- the n-gram sweep (2026-09-05, later session; lever 3 of the brief) --
  // Substrings and non-terminal wildcards used to be answered by scanning
  // k.txt whole — 12.5 MB for `amakasālāna` or `*vaggo`.  Now `tg/<gram>.txt`
  // holds the keys whose folded form CONTAINS <gram>, deepened by the next
  // character until it fits (`vag` may be `vaga`…`vagg`…`vag_`, `_` = the
  // key ends there), and a sweep fetches the CHEAPEST gram of the query's
  // literal fragments and verifies every key it holds by substring or
  // pattern in the mode's view.  The gram narrows; the verification decides;
  // the result is sorted — so keys, order, the 500-cap and `matched` are
  // what the k.txt scan gave.  Fragments with no gram at all fall back to it.
  let GM=null; const GS={};
  function grams(){ if(GM) return GM;
    return GM=(async()=>{ try{
        const r=await fetch(bust(base+'tg/index.json'));
        if(r.status===404) return {};
        if(!r.ok) throw new Error('HTTP '+r.status);
        const j=await r.json(); return (j&&j.grams)?j:{};
      }catch(e){ GM=null; return null; } })(); }
  function gramShard(name){ if(GS[name]) return GS[name];
    return GS[name]=(async()=>{ try{
        const r=await fetch(bust(base+'tg/'+name+'.txt'));
        if(!r.ok) throw new Error('HTTP '+r.status);
        return (await r.text()).split('\n').filter(Boolean);
      }catch(e){ delete GS[name]; return null; } })(); }
  // {names, bytes} for a folded gram: the shard itself, else its children,
  // else the shallowest shard that prefixes it
  function resolveGram(M,g){ const G=M.grams;
    if(G[g]!=null) return {names:[g],bytes:G[g]};
    const kids=[]; let b=0; for(const n in G){ if(n.startsWith(g)){ kids.push(n); b+=G[n]; } }
    if(kids.length) return {names:kids,bytes:b};
    for(let d=M.mind||2;d<g.length;d++){ const p=g.slice(0,d); if(G[p]!=null) return {names:[p],bytes:G[p]}; }
    return null; }
  // `frags`: the literal fragments of the query in the mode's view;
  // `terminal`: the last fragment ends the key (no trailing `*`).
  // Returns the sorted matching keys and the total, or null on failure, or
  // undefined when no gram applies (the caller then sweeps k.txt).
  async function sweep(frags,terminal,test){
    const M=await grams(); if(M===null) return null;
    if(!M.grams) return undefined;
    const mind=M.mind||2, maxd=M.maxd||8; let best=null;
    frags.forEach((fr,fi)=>{ const f=foldS(fr);
      for(let L=mind;L<=Math.min(maxd,f.length);L++) for(let j=0;j+L<=f.length;j++){
        const g=f.slice(j,j+L); const cands=[g];
        if(terminal&&fi===frags.length-1&&j+L===f.length&&L<maxd) cands.push(g+'_');
        for(const c of cands){ const r=resolveGram(M,c); if(r&&(!best||r.bytes<best.bytes)) best=r; } } });
    if(!best) return undefined;
    const ns=best.names; let i=0; const pool=[]; const seen=new Set(); let failed=false;
    for(let w=0;w<Math.min(6,ns.length);w++)
      pool.push((async()=>{ while(i<ns.length){ const t=await gramShard(ns[i++]);
        if(t===null){ failed=true; continue; } for(const k of t) if(test(k)) seen.add(k); } })());
    await Promise.all(pool);
    if(failed) return null;
    const ks=[...seen].sort();
    return {keys:ks.slice(0,CAPKEYS),matched:ks.length};
  }
  // ---- SECTION NAMES (2026-09-05, fourth session) -----------------------
  // `index/names.json` — every printed heading, 1.09 MB — used to be read
  // whole by both pages before their first query and scanned by substring
  // on every search: after tg/ it was the largest file a search fetched.
  // Now `index/tn/<gram>.json` holds the labels (with their rows) whose
  // folded form contains one n-gram inside a run of letters — the tg/ idiom
  // applied to labels — and a query reads its cheapest gram.  `names(fq)`
  // returns an object of names.json's SHAPE ({vols, layers, labels, rows})
  // holding only the candidates, rows in the file's own order, so the
  // page's matching, ranking and drawing run unchanged over it: the gram
  // narrows, the page's substring test decides.  Returns undefined when no
  // gram applies (no run of `mind` letters) or the store is absent — the
  // page then reads names.json as before — and null when a shard failed.
  let NM=null; const NS={};
  function nmanifest(){ if(NM) return NM;
    return NM=(async()=>{ try{
        const r=await fetch(bust(base+'tn/index.json'));
        if(r.status===404) return {};
        if(!r.ok) throw new Error('HTTP '+r.status);
        const j=await r.json(); return (j&&j.grams&&j.vols&&j.layers)?j:{};
      }catch(e){ NM=null; return null; } })(); }
  function nshard(name){ if(NS[name]) return NS[name];
    return NS[name]=(async()=>{ try{
        const r=await fetch(bust(base+'tn/'+name+'.json'));
        if(!r.ok) throw new Error('HTTP '+r.status);
        return await r.json();
      }catch(e){ delete NS[name]; return null; } })(); }
  async function names(fq){
    const M=await nmanifest(); if(M===null) return null;
    if(!M.grams) return undefined;
    const mind=M.mind||2, maxd=M.maxd||8; let best=null, any=false;
    for(const run of (foldS(fq).match(/[a-z]+/g)||[])){
      for(let L=mind;L<=Math.min(maxd,run.length);L++) for(let j=0;j+L<=run.length;j++){
        any=true; const r=resolveGram(M,run.slice(j,j+L));
        if(r&&(!best||r.bytes<best.bytes)) best=r; } }
    if(!any) return undefined;
    // a gram no label contains proves the query matches no label
    if(!best) return {vols:M.vols,layers:M.layers,labels:[],rows:[]};
    const shards=await Promise.all(best.names.map(nshard));
    if(shards.some(s=>s===null)) return null;
    const lidx={}, labels=[], rows={};
    for(const s of shards){
      const loc=s.labels.map(l=>{ if(lidx[l]==null){ lidx[l]=labels.length; labels.push(l); } return lidx[l]; });
      for(const r of s.rows) rows[r[4]]=[loc[r[0]],r[1],r[2],r[3]]; }
    const order=Object.keys(rows).map(Number).sort((a,b)=>a-b);
    return {vols:M.vols,layers:M.layers,labels,rows:order.map(g=>rows[g])};
  }
  function chunk(vol,ci){ const k=vol+'/'+ci; if(CH[k]) return CH[k];
    return CH[k]=(async()=>{ try{
        const r=await fetch(bust(base+'tx/'+vol+'/'+ci+'.json'));
        if(!r.ok) throw new Error('HTTP '+r.status);
        return (await r.json()).paras||[];
      }catch(e){ delete CH[k]; return null; } })(); }
  function chunkOf(vol,pi){ const s=MAN.tx[vol]; let lo=0,hi=s.length-1;
    while(lo<hi){ const mid=(lo+hi+1)>>1; if(s[mid]<=pi) lo=mid; else hi=mid-1; }
    return lo; }
  // the paragraph objects for a list of [vi,pi].  Chunks are small (about
  // 24 KB on the wire) and many, so the pool is 16 wide: over HTTP/2 that is
  // one connection, and the cost of a chunk is its round trip, not its bytes
  async function paras(list){
    const need={}; list.forEach(([vi,pi])=>{ const v=MAN.vols[vi]; need[v+'/'+chunkOf(v,pi)]=1; });
    const ks=Object.keys(need); let i=0; const pool=[]; let failed=false;
    for(let w=0;w<Math.min(16,ks.length);w++)
      pool.push((async()=>{ while(i<ks.length){ const k=ks[i++]; const s=k.indexOf('/');
        if(await chunk(k.slice(0,s),+k.slice(s+1))===null) failed=true; } })());
    await Promise.all(pool);
    if(failed) return null;
    const out=[];
    for(const [vi,pi] of list){ const v=MAN.vols[vi]; const ci=chunkOf(v,pi);
      const c=await chunk(v,ci); out.push(c?c[pi-MAN.tx[v][ci]]:null); }
    return out;
  }

  // ---- resolving one query word to {keys, post:{key:{vi:[[pi,c]]}}} -------
  // `w` is already normalised for the mode.  null = a fetch failed.
  async function postingsFor(ks){
    const byn={}; ks.forEach(k=>{ const n=shardName(foldS(k)); if(n)(byn[n]=byn[n]||[]).push(k); });
    const ns=Object.keys(byn); const post={}; let i=0; const pool=[]; let failed=false;
    for(let w=0;w<Math.min(6,ns.length);w++)
      pool.push((async()=>{ while(i<ns.length){ const n=ns[i++]; const t=await shard(n);
        if(t===null){ failed=true; continue; } byn[n].forEach(k=>{ if(t[k]) post[k]=t[k]; }); } })());
    await Promise.all(pool);
    if(failed) return null;
    return {keys:ks.filter(k=>post[k]),post};
  }
  async function resolveWord(w,fold){
    if(TERMS) return legacyResolve(w,fold);
    const view=fold?foldS:(k=>k);
    if(w.indexOf('*')>=0){
      if(w.replace(/\*/g,'').length<3) return {keys:[],post:{}};
      const rx=new RegExp(kpat(w)); const star=w.indexOf('*');
      if(star>=2){
        // dhamm*: every key lives in a shard whose name is a prefix of, or
        // extends, the folded literal prefix
        const fp=foldS(w.slice(0,star)); const names=[];
        for(const n in MAN.shards){ const bare=n.replace(/_+$/,'');
          if(fp.startsWith(bare)||bare.startsWith(fp)) names.push(n); }
        const found={}; let i=0; const pool=[]; let failed=false;
        for(let x=0;x<Math.min(6,names.length);x++)
          pool.push((async()=>{ while(i<names.length){ const t=await shard(names[i++]);
            if(t===null){ failed=true; continue; }
            for(const k in t){ if(rx.test(view(k))) found[k]=t[k]; } } })());
        await Promise.all(pool);
        if(failed) return null;
        // the cap keeps the COMMONEST forms, not an arbitrary 500: ranked by
        // paragraphs carrying them.  (Until 2026-09-05 it kept the first 500
        // in bucket order, which was volume order — `dhamm*` answered 88,895
        // or 4,822 depending on which forms happened to come first.)
        const size=k=>{ let n=0; for(const vi in found[k]) n+=found[k][vi].length; return n; };
        const ks=Object.keys(found).sort((a,b)=>size(b)-size(a)||(a<b?-1:1));
        const kk=ks.slice(0,CAPKEYS); const post={}; kk.forEach(k=>{post[k]=found[k];});
        return {keys:kk,post,matched:ks.length};
      }
      // *vaggo, a*vaggo: the gram sweep, verified by the pattern
      { const sw=await sweep(w.split('*').filter(Boolean),!w.endsWith('*'),k=>rx.test(view(k)));
        if(sw===null) return null;
        if(sw){ const r=await postingsFor(sw.keys); if(r) r.matched=sw.matched; return r; } }
      const txt=fold?await keysFolded():await keys(); if(txt==null) return null;
      const exact=await keys();
      const rxg=new RegExp(kpat(w),'gm'); const ks=[]; let m, matched=0;
      while((m=rxg.exec(txt))){ if(!m[0]){ rxg.lastIndex++; continue; } matched++;
        if(ks.length<CAPKEYS) ks.push(exact.slice(m.index,m.index+m[0].length)); }
      const r=await postingsFor(ks); if(r) r.matched=matched; return r;
    }
    const n=shardName(foldS(w)); const t=n?await shard(n):{};
    if(t===null) return null;
    let ks;
    if(fold){ ks=(foldMap(n,t)[w]||[]).slice(); }
    else ks=t[w]?[w]:[];
    if(ks.length){ const post={}; ks.forEach(k=>{post[k]=t[k];}); return {keys:ks,post}; }
    if(w.length<3) return {keys:[],post:{}};
    // the substring sweep: a bare word also matches inside longer words
    { const sw=await sweep([w],false,k=>view(k).indexOf(w)>=0);
      if(sw===null) return null;
      if(sw){ const r=await postingsFor(sw.keys); if(r) r.matched=sw.matched; return r; } }
    const txt=fold?await keysFolded():await keys(); if(txt==null) return null;
    const exact=await keys();
    const out=[]; let i=txt.indexOf(w), matched=0;
    while(i>=0){
      const a=txt.lastIndexOf('\n',i)+1; let z=txt.indexOf('\n',i); if(z<0) z=txt.length;
      matched++; if(out.length<CAPKEYS) out.push(exact.slice(a,z)); i=txt.indexOf(w,z);
    }
    const r=await postingsFor(out); if(r) r.matched=matched; return r;
  }

  // ---- the search -----------------------------------------------------------
  async function search(q,o){
    o=o||{}; const fold=!!o.fold, lf=o.layer||'', CAPP=o.capP||70, CAPA=o.capA||35;
    const say=o.onProgress||(()=>{});
    await ensure();
    if(!ready()) return null;
    const norm=fold?foldS:canonS;
    const words=norm(q).trim().split(/\s+/).filter(Boolean);
    const res={words,mode:fold?'fold':'exact',legacy:!!TERMS,vis:null,total:0,phrParas:0,phrVols:new Set(),andTotal:0,phrOut:[],andOut:[],capped:[]};
    if(!words.length) return res;
    const resolved=[];
    for(const wd of words){ const r=await resolveWord(wd,fold); if(r===null) return null; resolved.push(r);
      if(r.matched&&r.matched>r.keys.length) res.capped.push({word:wd,matched:r.matched,used:r.keys.length}); }
    if(!resolved.every(r=>r.keys.length)) return res;
    if(TERMS) return legacySearch(res,resolved,lf,CAPP,CAPA,norm);
    const LAY=layers();
    // per word: vi -> Map(pi -> count), summed over its keys
    const per=resolved.map(r=>{ const m={};
      for(const k of r.keys){ const pv=r.post[k]; for(const vi in pv){ const mm=m[vi]||(m[vi]=new Map());
        for(const [pi,c] of pv[vi]) mm.set(pi,(mm.get(pi)||0)+c); } }
      return m; });
    let vis=Object.keys(per[0]).map(Number).filter(vi=>per.every(m=>m[vi]));
    if(lf) vis=vis.filter(vi=>LAY[vi]===lf);
    // canon first, then aṭṭhakathā, then ṭīkā — the caps spend themselves in
    // this order, so it is `vis` that is sorted, not the drawn rows
    vis.sort((a,b)=>((LRANK[LAY[a]]??3)-(LRANK[LAY[b]]??3))||a-b);
    if(!vis.length) return res;
    res.vis=vis;
    const V=vols(); const nPhr={}, nAnd={};
    if(words.length===1){
      const draw=[];
      for(const vi of vis){ const mm=per[0][vi]; const lay=LAY[vi];
        const pis=[...mm.keys()].sort((a,b)=>a-b);
        for(const pi of pis){ res.total+=mm.get(pi); res.phrParas++; res.phrVols.add(vi);
          if((nPhr[lay]=(nPhr[lay]||0)+1)<=CAPP) draw.push([vi,pi]); } }
      say(res.phrParas);
      const ps=await paras(draw); if(ps===null) return null;
      draw.forEach(([vi,pi],i)=>{ if(ps[i]) res.phrOut.push({vi,vol:V[vi],lay:LAY[vi],p:ps[i]}); });
      return res;
    }
    // a phrase: every candidate paragraph carrying all the words is read, and
    // adjacency is decided on its TOKENS — never on the postings alone, which
    // carry counts, not positions (a position store was measured and not
    // built: claude/phrase_positions_are_a_different_semantic.md)
    const cand=[];
    for(const vi of vis){ const pis=[...per[0][vi].keys()].filter(pi=>per.every(m=>m[vi].has(pi))).sort((a,b)=>a-b);
      for(const pi of pis) cand.push([vi,pi]); }
    say(cand.length);
    const ps=await paras(cand); if(ps===null) return null;
    const sets=resolved.map(r=>new Set(r.keys));
    cand.forEach(([vi,pi],i)=>{ const p=ps[i]; if(!p) return; const lay=LAY[vi];
      const c=phraseCount(p.text,sets);
      if(c>0){ res.total+=c; res.phrParas++; res.phrVols.add(vi); if((nPhr[lay]=(nPhr[lay]||0)+1)<=CAPP) res.phrOut.push({vi,vol:V[vi],lay,p}); }
      else { res.andTotal++; if((nAnd[lay]=(nAnd[lay]||0)+1)<=CAPA) res.andOut.push({vi,vol:V[vi],lay,p}); } });
    return res;
  }

  // ---- legacy: terms.compact.json + <VOL>.idx.json, the pre-09-05 algorithm
  // with the mode added.  Kept so an unpacked older deposit still answers.
  let TK=null, TKF=null;
  function legacyResolve(w,fold){
    const T=TERMS.terms; if(!TK){ TK=Object.keys(T); TKF=TK.map(foldS); }
    const view=i=>fold?TKF[i]:TK[i];
    let ks=[];
    if(w.indexOf('*')>=0){ if(w.replace(/\*/g,'').length<3) return {keys:[],post:{}};
      const rx=new RegExp(kpat(w)); for(let i=0;i<TK.length&&ks.length<CAPKEYS;i++) if(rx.test(view(i))) ks.push(TK[i]); }
    else if(!fold&&T[w]) ks=[w];
    else { if(fold) for(let i=0;i<TK.length;i++) if(TKF[i]===w) ks.push(TK[i]);
      if(!ks.length&&w.length>=3) for(let i=0;i<TK.length&&ks.length<CAPKEYS;i++) if(view(i).indexOf(w)>=0) ks.push(TK[i]); }
    const post={}; ks.forEach(k=>{ post[k]=T[k]||[]; });   // here post[key] = [volIdx…]
    return {keys:ks,post};
  }
  function idx(vi){ if(IDX[vi]) return IDX[vi];
    return IDX[vi]=(async()=>{ try{ const r=await fetch(bust(base+TERMS.vols[vi]+'.idx.json'));
        if(!r.ok) throw new Error('HTTP '+r.status); return await r.json();
      }catch(e){ delete IDX[vi]; return {paras:[],inv:{}}; } })(); }
  async function legacySearch(res,resolved,lf,CAPP,CAPA,norm){
    const LAY=TERMS.layers, V=TERMS.vols, words=res.words;
    const vsets=resolved.map(r=>new Set(r.keys.flatMap(k=>r.post[k]||[])));
    let vis=[...vsets[0]].filter(v=>vsets.every(s=>s.has(v)));
    if(lf) vis=vis.filter(v=>LAY[v]===lf);
    vis.sort((a,b)=>((LRANK[LAY[a]]??3)-(LRANK[LAY[b]]??3))||a-b);
    if(!vis.length) return res;
    res.vis=vis;
    { const need=[...vis]; let ni=0; const pool=[];
      for(let w=0;w<Math.min(8,need.length);w++) pool.push((async()=>{ while(ni<need.length) await idx(need[ni++]); })());
      await Promise.all(pool); }
    const sets=resolved.map(r=>new Set(r.keys));
    const nPhr={}, nAnd={};
    for(const vi of vis){ const sh=await idx(vi); const lay=LAY[vi];
      const maps=resolved.map(r=>{ const mm=new Map();
        for(const k of r.keys) for(const [pi,c] of (sh.inv[k]||[])) mm.set(pi,(mm.get(pi)||0)+c); return mm; });
      const pis=[...maps[0].keys()].filter(pi=>maps.every(mm=>mm.has(pi))).sort((a,b)=>a-b);
      for(const pi of pis){ const p=sh.paras[pi];
        if(words.length>1){ const c=phraseCount(p.text,sets);
          if(c>0){ res.total+=c; res.phrParas++; res.phrVols.add(vi); if((nPhr[lay]=(nPhr[lay]||0)+1)<=CAPP) res.phrOut.push({vi,vol:V[vi],lay,p}); }
          else { res.andTotal++; if((nAnd[lay]=(nAnd[lay]||0)+1)<=CAPA) res.andOut.push({vi,vol:V[vi],lay,p}); } }
        else { res.total+=maps[0].get(pi); res.phrParas++; res.phrVols.add(vi);
          if((nPhr[lay]=(nPhr[lay]||0)+1)<=CAPP) res.phrOut.push({vi,vol:V[vi],lay,p}); } } }
    return res;
  }

  return {ensure,ready,error,vols,layers,search,resolveWord,names,
          norm:fold=>fold?foldS:canonS, isLegacy:()=>!!TERMS};
}
return {create,foldS,canonS,rxEsc,wpat};
})();

// GATE: both search implementations answer multi-word and wildcard queries,
// name the book on a row, and never count a non-adjacent hit as the phrase.
//
// WHY.  Reader, 2026-08-08, with screenshots: a result row said only
// `Pāḷi ¶52`; a query of more than one word was wanted; "if I type a word
// after searching one it does not search anymore"; and the same `sabbe
// saṅkhārā` failure again on search.html — THE TWO IMPLEMENTATIONS HAD
// DRIFTED, which is why this gate boots BOTH pages.  The multi-word failures
// were one bug: single-word term keys, so a spaced query matched no key and
// painted "No matches".
//
// WHAT IS ASSERTED, each against ground truth computed HERE from the shards
// with the reference algorithm, never against a page's own output:
//   reader2.html — phrase count and rows; non-adjacent listed separately;
//     book from `booktitle/` (07Di02 = `Mahāvaggapāḷi`, NEVER the corpus
//     `book` field's kathā); single-word count unchanged; `*` wildcard alone
//     and inside a phrase (`\S*` in text, so it cannot cross a word); the
//     layer chips actually filter; the "?" help box opens; the head counts
//     paragraphs and volumes, not drawn rows; both `markInEl` paths.
//   search.html — the same phrase, book, wildcard and layer assertions
//     against its own DOM (`#status`, `.hit`, `.loc`).
//
// SELFTEST: `node pipeline/check_search.js --selftest OLD_READER OLD_SEARCH`
// runs the same assertions against older builds (e.g. `git show
// f82db5ab:site/reader/reader2.html` and `git show HEAD:site/search.html`
// from before the port) and must FAIL — a gate that has never failed has
// never been shown to guard anything.
//
// Usage:  node pipeline/check_search.js
//         node pipeline/check_search.js --selftest /tmp/r2_old.html /tmp/se_old.html

const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const ROOT=path.dirname(__dirname);
const SELF=process.argv.includes('--selftest');
const ai=process.argv.indexOf('--selftest');
const READER=SELF?process.argv[ai+1]:path.join(ROOT,'site','reader','reader2.html');
const SEARCH=SELF?process.argv[ai+2]:path.join(ROOT,'site','search.html');

const wait=ms=>new Promise(r=>setTimeout(r,ms));
// two pages, two fetch bases: reader2 fetches '../index/…' and 'booktitle/…'
// relative to site/reader/; search.html fetches 'index/…' and
// 'reader/booktitle/…' relative to site/.
function mkResolve(base){ return u=>{ u=String(u).split('?')[0];
  if(u.startsWith('../')) return path.join(ROOT,'site',u.slice(3));
  if(u.startsWith('http')){ try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){} }
  return path.join(base,u); }; }
// the shared core is a <script src> (2026-09-05: searchcore.js, one
// implementation for both pages); jsdom does not fetch scripts, so it is
// inlined the way check_lookup_reach.js inlines panel.js
function inlineScripts(html,resolve){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    return t==null?m:'<script>'+t+'</script>'; });
}
function boot(file,base,opts){
  const resolve=mkResolve(base);
  const hideTb=opts&&opts.hideTb;   // simulate an unpacked deposit from before tp/
  const dom=new JSDOM(inlineScripts(fs.readFileSync(file,'utf8'),resolve),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
    w.__fetched=[];
    w.fetch=u=>{w.__fetched.push(String(u).split('?')[0]);
      const f=resolve(u);let t=null;
      if(!(hideTb&&/\/tp\//.test(String(u)))){ try{t=fs.readFileSync(f,'utf8');}catch(e){} }
      return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};
  }});
  return dom.window;
}
async function readyReader(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

// ---- ground truth, straight from the shards --------------------------------
const FOLDM={'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'};
const foldS=s=>(s||'').toLowerCase().replace(/[āīūṁṃṅñṭḍṇḷ]/g,c=>FOLDM[c]||c);
const rxEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
// EXACT is the default since 2026-09-05 (reader: `tassa` and `tassā` are
// different words).  The query is canonicalised — NFC, lower case, the
// modern ṃ written as the edition's ṁ — and matched against the keys AS
// STORED; folding is a switch.  `truth()` therefore takes the mode: in exact
// mode a key matches by identity/substring/wildcard on itself, in fold mode
// on its folded form, and the phrase check runs over the canonical text
// rather than the folded one.  Against the pre-09-05 index (folded keys) the
// two modes coincide, which is why the old assertions still pass on it and
// the new ones below do not.
const canonS=s=>(s||'').normalize('NFC').toLowerCase().replace(/ṃ/g,'ṁ');
let _T=null;
const T=()=>_T||(_T=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index','terms.compact.json'),'utf8')));
const keysFor=(w,fold)=>{
  const norm=fold?foldS:canonS; w=norm(w);
  const view=k=>fold?foldS(k):k;
  if(w.indexOf('*')>=0){ const rx=new RegExp('^'+w.split('*').map(rxEsc).join('.*')+'$');
    const out=[]; for(const k in T().terms){ if(rx.test(view(k))){ out.push(k); if(out.length>=500) break; } } return out; }
  if(!fold && T().terms[w]) return [w];
  if(fold){ const ex=[]; for(const k in T().terms) if(foldS(k)===w) ex.push(k); if(ex.length) return ex; }
  if(w.length<3) return [];
  const out=[]; for(const k in T().terms){ if(view(k).indexOf(w)>=0){ out.push(k); if(out.length>=500) break; } } return out;
};
// {phrTot, phrParas, andParas, vols} for a query, optionally within one layer
function truth(words,layer,fold){
  const norm=fold?foldS:canonS;
  const per=words.map(w=>keysFor(w,fold));
  if(per.some(m=>!m.length)) return {phrTot:0,phrParas:0,andParas:0,vols:0};
  const vsets=per.map(m=>new Set(m.flatMap(k=>T().terms[k]||[])));
  let vis=[...vsets[0]].filter(v=>vsets.every(s=>s.has(v)));
  if(layer) vis=vis.filter(v=>T().layers[v]===layer);
  const phRx=new RegExp(words.map(norm).map(w=>w.indexOf('*')>=0?w.split('*').map(rxEsc).join('\\S*'):rxEsc(w)).join(' '),'g');
  let phrTot=0,phrParas=0,andParas=0; const volsWith=new Set();
  for(const vi of vis){
    const sh=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index',T().vols[vi]+'.idx.json'),'utf8'));
    const maps=per.map(m=>{const mm=new Map(); for(const k of m) for(const [pi,c] of (sh.inv[k]||[])) mm.set(pi,(mm.get(pi)||0)+c); return mm;});
    for(const pi of maps[0].keys()){ if(!maps.every(mm=>mm.has(pi))) continue;
      if(words.length===1){ phrTot+=maps[0].get(pi); phrParas++; volsWith.add(vi); continue; }
      const f=norm(sh.paras[pi].text);
      phRx.lastIndex=0; let n=0,m; while((m=phRx.exec(f))){ if(!m[0]){phRx.lastIndex++;continue;} n++; }
      if(n>0){phrTot+=n;phrParas++;volsWith.add(vi);} else {andParas++;}
    }
  }
  return {phrTot,phrParas,andParas,vols:volsWith.size};
}
// ---- exact-diacritics truth FROM THE CORPUS TEXT, not from any index ------
// The assertions built on this are the ones that had to go red on the folded
// index of 2026-09-05 before it was rebuilt: the map above cannot know what it
// merged, so the count comes straight from `site/<VOL>.json`, tokenised the
// way the builder tokenises.
function corpusCounts(words){
  const TOKRX=/[^a-zāīūṁṃṅñṇṭḍḷ]+/i;
  const want=new Set(words); const out={}; words.forEach(w=>out[w]={occ:0,paras:0,vols:new Set()});
  const man=JSON.parse(fs.readFileSync(path.join(ROOT,'site/reader/manifest.json'),'utf8')).volumes;
  for(const vol of Object.keys(man).sort()){
    const P=JSON.parse(fs.readFileSync(path.join(ROOT,'site',vol+'.json'),'utf8')).paragraphs;
    for(const p of P){ const seen=new Set();
      for(const w of canonS(p.text).split(TOKRX)){ if(want.has(w)){ out[w].occ++; seen.add(w); } }
      for(const w of seen){ out[w].paras++; out[w].vols.add(vol); } } }
  for(const w in out) out[w].vols=out[w].vols.size; return out;
}

let fails=0;
const ok=(cond,label,detail)=>{ console.log((cond?'  ok    ':'  FAIL  ')+label+(detail?'  ['+detail+']':'')); if(!cond)fails++; };

(async()=>{
  console.log((SELF?'SELFTEST — expected to FAIL — against ':'checking ')+READER+' and '+SEARCH);

  // ================= reader2.html =================
  const w=boot(READER,path.join(ROOT,'site','reader'));
  if(!await readyReader(w)){ console.log('  FAIL  reader did not boot'); process.exit(1); }
  const heads=dd=>[...dd.querySelectorAll('.sr-head')].map(h=>h.textContent);

  // 1. two-word phrase, rare on purpose (7 volumes) so the run stays light.
  const t1=truth(['yamakasālānaṁ','antare']);
  await w.doSearch('yamakasālānaṁ antare');
  let dd=w.document.getElementById('sdrop');
  ok(heads(dd).some(h=>h.startsWith(t1.phrTot.toLocaleString()+' occurrence')),
     'reader: phrase count painted', 'want '+t1.phrTot+' | '+heads(dd).join(' / '));
  ok(t1.andParas===0 || heads(dd).some(h=>h.includes(t1.andParas.toLocaleString()+' paragraph')&&h.includes('not adjacent')),
     'reader: non-adjacent listed separately', 'want '+t1.andParas);
  ok(!dd.textContent.includes('No matches'),'reader: a spaced query is not "No matches"');
  ok(dd.querySelectorAll('.sresult').length===t1.phrParas+t1.andParas,
     'reader: row count = phrase + AND paras', dd.querySelectorAll('.sresult').length+' vs '+(t1.phrParas+t1.andParas));
  ok([...dd.querySelectorAll('.sresult mark')].length>0,'reader: match marked in snippet');
  ok(heads(dd).some(h=>h.includes(' in '+t1.phrParas.toLocaleString()+' paragraph(s), '+t1.vols.toLocaleString()+' volume(s)')),
     'reader: head counts PHRASE paragraphs and volumes, not AND ones',
     'want '+t1.phrParas+'p/'+t1.vols+'v | '+heads(dd)[0]);

  // 2. the book on a row: 07Di02, whose corpus `book` field is the kathā.
  await w.doSearch('piṇḍapātapaṭikkantānaṁ karerimaṇḍalamāḷe');
  dd=w.document.getElementById('sdrop');
  const wheres=[...dd.querySelectorAll('.sr-where')].map(e=>e.textContent);
  ok(wheres.some(t=>t.includes('Mahāvaggapāḷi')&&t.includes('07Di02')),
     'reader: book from booktitle/', wheres.slice(0,3).join(' | ')||'no .sr-where at all');
  ok(!wheres.some(t=>t.includes('Pubbenivāsa')),'reader: corpus book field not printed');

  // 3. single word, exact term — its 8 volumes span all three layers, so it
  // also carries the ORDER assertion: canon rows first, then aṭṭhakathā, then
  // ṭīkā (2026-08-08, user request; volume order alone leads with 01ViT01, a
  // ṭīkā).  Sections stay above, untouched.
  const t3=truth(['yamakasālānaṁ']);
  const t3c=truth(['yamakasālānaṁ'],'pali-unicode');
  await w.doSearch('yamakasālānaṁ');
  dd=w.document.getElementById('sdrop');
  ok(heads(dd).some(h=>h.startsWith(t3.phrTot.toLocaleString()+' occurrence')),
     'reader: single-word count unchanged', 'want '+t3.phrTot+' | '+heads(dd).join(' / '));
  const seq=[...dd.querySelectorAll('.sresult .sr-lay')].map(e=>e.textContent.split(/[\s¶]/)[0]);
  const LR={'Pāḷi':0,'Aṭṭhakathā':1,'Ṭīkā':2};
  ok(t3c.phrParas>0 && seq.length>0 && seq[0]==='Pāḷi'
     && seq.every((x,i)=>i===0||LR[seq[i-1]]<=LR[x]),
     'reader: rows ordered Pāḷi → Aṭṭhakathā → Ṭīkā', seq.join(','));

  // 4. `*` wildcard, alone and in a phrase.  `\S*` in text: the star must not
  // cross a word boundary.
  const t4=truth(['yamakasāl*']);
  await w.doSearch('yamakasāl*');
  dd=w.document.getElementById('sdrop');
  ok(t4.phrTot>0 && heads(dd).some(h=>h.startsWith(t4.phrTot.toLocaleString()+' occurrence')),
     'reader: wildcard word', 'want '+t4.phrTot+' | '+heads(dd).join(' / '));
  const t5=truth(['yamakasāl*','antare']);
  await w.doSearch('yamakasāl* antare');
  dd=w.document.getElementById('sdrop');
  ok(t5.phrTot>0 && heads(dd).some(h=>h.startsWith(t5.phrTot.toLocaleString()+' occurrence')),
     'reader: wildcard inside a phrase', 'want '+t5.phrTot+' | '+heads(dd).join(' / '));

  // 5. the layer chips filter, and the way out is on screen.  Ṭīkā, not the
  // canon: the canon volumes that carry both WORDS carry them in no single
  // PARAGRAPH, so a canon expectation is 0 rows and the assertion would pass
  // vacuously on a build with no filter at all.
  const t6=truth(['yamakasālānaṁ','antare'],'tika-unicode');
  w.document.getElementById('sq').value='yamakasālānaṁ antare';
  if(typeof w.setSLayer==='function'){ w.setSLayer('tika-unicode'); await wait(600); }
  dd=w.document.getElementById('sdrop');
  const lays=[...dd.querySelectorAll('.sresult .sr-lay')].map(e=>e.textContent);
  ok(typeof w.setSLayer==='function'
     && (t6.phrParas+t6.andParas)>0
     && dd.querySelectorAll('.sresult').length===t6.phrParas+t6.andParas
     && lays.every(t=>t.startsWith('Ṭīkā')),
     'reader: layer chip filters to the ṭīkā', (typeof w.setSLayer)+' rows='+dd.querySelectorAll('.sresult').length+' want '+(t6.phrParas+t6.andParas));
  ok(!!dd.querySelector('.sr-chip.on'),'reader: active chip shown');
  if(typeof w.setSLayer==='function'){ w.setSLayer(''); await wait(600); }

  // 6. the "?" help.
  if(typeof w.setSHelp==='function'){ w.setSHelp(); await wait(600); }
  dd=w.document.getElementById('sdrop');
  ok(!!dd.querySelector('.sr-helpbox'),'reader: help box opens');
  if(typeof w.setSHelp==='function'){ w.setSHelp(); await wait(600); }

  // 6b. per-layer caps: `arati` = 80 canon paragraphs, EXACTLY the old global
  // cap, so the reader saw only Pāḷi rows however far he scrolled
  // (2026-08-08, user-reported with a screenshot).  Reader caps 30/layer.
  const rP=truth(['arati'],'pali-unicode').phrParas,
        rA=truth(['arati'],'atthakatha-unicode').phrParas,
        rT=truth(['arati'],'tika-unicode').phrParas;
  await w.doSearch('arati');
  dd=w.document.getElementById('sdrop');
  const rcnt={};
  for(const e of dd.querySelectorAll('.sresult .sr-lay')) { const k=e.textContent.split(/[\s¶]/)[0]; rcnt[k]=(rcnt[k]||0)+1; }
  ok(rcnt['Pāḷi']===Math.min(30,rP)&&rcnt['Aṭṭhakathā']===Math.min(30,rA)&&rcnt['Ṭīkā']===Math.min(30,rT),
     'reader: every layer draws up to its own cap',
     JSON.stringify(rcnt)+' want '+[Math.min(30,rP),Math.min(30,rA),Math.min(30,rT)].join('/'));

  // 6c. a chip click must not close the dropdown.  In the browser the chip's
  // onclick REPAINTS the dropdown before the document-level outside-click
  // listener runs (microtasks run between listeners of one event), so that
  // listener saw a DETACHED target, `contains()` said "outside", and the box
  // hid mid-use (2026-08-08, user-reported).  jsdom dispatches listeners
  // without the microtask gap, so the race is SIMULATED: an event whose
  // target is detached but whose composedPath — captured at dispatch — still
  // holds the search div.
  dd.hidden=false;
  { const sdiv=w.document.querySelector('.search');
    const ghost=w.document.createElement('span');
    const ev=new w.Event('click',{bubbles:true});
    ev.composedPath=()=>[ghost,dd,sdiv,w.document.body,w.document];
    Object.defineProperty(ev,'target',{value:ghost});
    w.document.dispatchEvent(ev); }
  ok(dd.hidden===false,'reader: chip click cannot close the dropdown','hidden='+dd.hidden);

  // 6d. THE WIRING FACTS (2026-08-09, the bucketed index).  An exact-word
  //     search must have fetched tb/ buckets and NEVER terms.compact.json —
  //     the 22 MB map and its 643,965-entry parse are the cost the buckets
  //     exist to remove.  The searches above covered exact, substring-sweep
  //     (none needed yet — added below), both wildcard shapes and phrases.
  const fetched=w.__fetched.join(' ');
  ok(/\/tp\/index\.json/.test(fetched)&&/\/tp\/[a-z_]+\.json/.test(fetched),
     'wiring: postings shards are fetched');
  ok(!/terms\.compact\.json/.test(fetched),
     'wiring: the 22 MB map is never fetched');
  // 2026-09-05: nor is any per-volume shard — counting `tassā` used to pull
  // 117 of them (194 MB); rows now come from text chunks
  ok(!/\.idx\.json/.test(fetched)&&/\/tx\/[^/]+\/\d+\.json/.test(fetched),
     'wiring: no per-volume idx.json; rows come from tx/ chunks');
  // a SUBSTRING sweep (not exact, no wildcard) must still count exactly —
  // truth comes from the source map, so this is the first time the
  // assertion is not circular.  2026-09-05 (later): the sweep surface is no
  // longer `k.txt` (12.5 MB, scanned whole for every substring and
  // `*`-suffix query) but ONE n-gram shard under `tg/` — the keys containing
  // the query's rarest gram, verified by substring on the client.  The
  // assertion that used to say "the sweep fetched k.txt" now says the
  // opposite; it went red on `20a4d997e795` before the shards existed.
  const tS=truth(['amakasālāna']);
  const nBefore=w.__fetched.length;
  await w.doSearch('amakasālāna');
  dd=w.document.getElementById('sdrop');
  ok(tS.phrTot>0 && heads(dd).some(h=>h.startsWith(tS.phrTot.toLocaleString()+' occurrence')),
     'wiring: substring sweep counts exactly', 'want '+tS.phrTot+' | '+heads(dd).join(' / '));
  { const sw=w.__fetched.slice(nBefore).join(' ');
    ok(!/tp\/k\.txt/.test(sw),'wiring: the substring sweep does not fetch k.txt', sw.match(/tp\/k\.txt/)?'fetched k.txt':'');
    ok(/\/tg\/[a-z_]+\.txt/.test(sw),'wiring: the substring sweep fetched an n-gram shard (tg/)'); }
  // and the `*`-suffix shape, which took the same 12.5 MB path
  const tV=truth(['*vaggo']);
  const nB2=w.__fetched.length;
  await w.doSearch('*vaggo');
  dd=w.document.getElementById('sdrop');
  ok(tV.phrTot>0 && heads(dd).some(h=>h.startsWith(tV.phrTot.toLocaleString()+' occurrence')),
     'wiring: *-suffix sweep counts exactly', 'want '+tV.phrTot+' | '+heads(dd).join(' / '));
  { const sw=w.__fetched.slice(nB2).join(' ');
    ok(!/tp\/k\.txt/.test(sw),'wiring: the *-suffix sweep does not fetch k.txt');
    ok(/\/tg\/[a-z_]+\.txt/.test(sw),'wiring: the *-suffix sweep fetched an n-gram shard (tg/)'); }

  // 6e. the FALLBACK: with tb/ absent (an unpacked deposit from before the
  //     buckets) the box must still answer, from terms.compact.json
  {
    const w2=boot(READER,path.join(ROOT,'site','reader'),{hideTb:true});
    if(await readyReader(w2)){
      await w2.doSearch('yamakasālānaṁ');
      const dd2=w2.document.getElementById('sdrop');
      const h2=[...dd2.querySelectorAll('.sr-head')].map(h=>h.textContent);
      ok(h2.some(h=>h.startsWith(t3.phrTot.toLocaleString()+' occurrence')),
         'wiring: legacy fallback answers when tp/ is absent', h2.join(' / '));
      ok(/terms\.compact\.json/.test(w2.__fetched.join(' ')),
         'wiring: the fallback used the legacy map');
    } else { ok(false,'wiring: fallback window did not boot'); }
  }

  // 6f. EXACT DIACRITICS BY DEFAULT (2026-09-05, reader: "tassa and tassā are
  //     different words").  Truth from the corpus text.  `anīkaratto` (6
  //     occurrences, 2 volumes) and `anikaratto` (3) fold to one key; each
  //     must count only itself, the head must SAY which mode produced the
  //     count, and the switch must merge them again — and say so.
  const X=corpusCounts(['anīkaratto','anikaratto','tassā']);
  const XA=X['anīkaratto'], XB=X['anikaratto'];
  ok(XA.occ>0&&XB.occ>0&&XA.occ!==XB.occ,'exact: the test pair is real', JSON.stringify([XA,XB]));
  if(typeof w.setSFold==='function') w.setSFold(false);
  await w.doSearch('anīkaratto');
  dd=w.document.getElementById('sdrop');
  ok(heads(dd).some(h=>h.startsWith(XA.occ.toLocaleString()+' occurrence')&&h.includes(' in '+XA.paras+' paragraph')),
     'reader exact: anīkaratto counts only anīkaratto', 'want '+XA.occ+'/'+XA.paras+' | '+heads(dd).join(' / '));
  ok(heads(dd).some(h=>/exact/i.test(h)),'reader exact: the head names the mode', heads(dd).join(' / '));
  await w.doSearch('anikaratto');
  dd=w.document.getElementById('sdrop');
  ok(heads(dd).some(h=>h.startsWith(XB.occ.toLocaleString()+' occurrence')),
     'reader exact: anikaratto counts only anikaratto', 'want '+XB.occ+' | '+heads(dd).join(' / '));
  ok(typeof w.setSFold==='function','reader: the fold switch exists');
  if(typeof w.setSFold==='function'){
    w.document.getElementById('sq').value='anikaratto';
    w.setSFold(true); await wait(800);
    dd=w.document.getElementById('sdrop');
    ok(heads(dd).some(h=>h.startsWith((XA.occ+XB.occ).toLocaleString()+' occurrence')&&/ignored|fold/i.test(h)),
       'reader fold: the switch merges the pair and the head says so', heads(dd).join(' / '));
    ok(!!dd.querySelector('.sr-chip.sr-fold.on'),'reader fold: the switch state is visible');
    w.setSFold(false); await wait(300);
  }

  // 7. markInEl: phrase as one run; words apart each marked; wildcard extent.
  const doc=w.document;
  const el1=doc.createElement('div'); el1.textContent='idha yamakasālānaṁ antare pupphitā';
  w.markInEl(el1,'yamakasālānaṁ antare');
  ok(el1.querySelectorAll('mark.shl').length===1,'reader: phrase marked as one run',
     el1.querySelectorAll('mark.shl').length+' marks');
  const el2=doc.createElement('div'); el2.textContent='antare pana kiñci, yamakasālānaṁ pucchā';
  w.markInEl(el2,'yamakasālānaṁ antare');
  ok(el2.querySelectorAll('mark.shl').length===2,'reader: words apart each marked',
     el2.querySelectorAll('mark.shl').length+' marks');
  const el3=doc.createElement('div'); el3.textContent='tattha dhammacakkhuṁ udapādi';
  w.markInEl(el3,'dhamm*');
  const m3=el3.querySelector('mark.shl');
  ok(!!m3&&m3.textContent==='dhammacakkhuṁ','reader: wildcard marks the whole word',
     m3?m3.textContent:'no mark');

  // ================= search.html =================
  const s=boot(SEARCH,path.join(ROOT,'site'));
  await wait(300);
  const sq=v=>{ s.document.getElementById('q').value=v; return s.run(); };
  const st=()=>s.document.getElementById('status').textContent;

  await sq('yamakasālānaṁ antare');
  ok(st().startsWith(t1.phrTot.toLocaleString()+' occurrence')&&st().includes('paragraph(s)'),
     'search: phrase count in status', st());
  ok(t1.andParas===0||st().includes(t1.andParas.toLocaleString()+' paragraph'),
     'search: non-adjacent counted in status', st());
  ok(s.document.querySelectorAll('.hit').length===t1.phrParas+t1.andParas,
     'search: row count = phrase + AND paras', s.document.querySelectorAll('.hit').length+' vs '+(t1.phrParas+t1.andParas));
  ok([...s.document.querySelectorAll('.hit mark')].length>0,'search: match marked in snippet');

  await sq('piṇḍapātapaṭikkantānaṁ karerimaṇḍalamāḷe');
  const locs=[...s.document.querySelectorAll('.hit .loc')].map(e=>e.textContent);
  ok(locs.some(t=>t.includes('Mahāvaggapāḷi')&&t.includes('07Di02')),
     'search: book from booktitle/', locs.slice(0,2).join(' | ')||'no rows');
  ok(!locs.some(t=>t.includes('Pubbenivāsa')),'search: corpus book field not printed');

  await sq('yamakasāl*');
  ok(t4.phrTot>0&&st().startsWith(t4.phrTot.toLocaleString()+' occurrence'),
     'search: wildcard word', 'want '+t4.phrTot+' | '+st());

  // the two sweep shapes on THIS page too — same counts, no k.txt
  { const n0=s.__fetched.length; await sq('*vaggo');
    ok(tV.phrTot>0&&st().startsWith(tV.phrTot.toLocaleString()+' occurrence'),
       'search: *-suffix sweep counts exactly', 'want '+tV.phrTot+' | '+st());
    const sw=s.__fetched.slice(n0).join(' ');
    ok(!/tp\/k\.txt/.test(sw)&&/\/tg\/[a-z_]+\.txt/.test(sw),'search wiring: the *-suffix sweep reads a tg/ shard, not k.txt');
    const n1=s.__fetched.length; await sq('amakasālāna');
    ok(tS.phrTot>0&&st().startsWith(tS.phrTot.toLocaleString()+' occurrence'),
       'search: substring sweep counts exactly', 'want '+tS.phrTot+' | '+st());
    const sw2=s.__fetched.slice(n1).join(' ');
    ok(!/tp\/k\.txt/.test(sw2)&&/\/tg\/[a-z_]+\.txt/.test(sw2),'search wiring: the substring sweep reads a tg/ shard, not k.txt'); }

  await sq('yamakasālānaṁ');
  // `Pāḷi`, not `Tipiṭaka` — the two UIs must name the layer alike
  // (2026-08-08, user request)
  const sseq=[...s.document.querySelectorAll('.hit .lay')].map(e=>e.textContent);
  const LR2={'Pāḷi':0,'Aṭṭhakathā':1,'Ṭīkā':2};
  ok(t3c.phrParas>0 && sseq.length>0 && sseq[0]==='Pāḷi'
     && sseq.every((x,i)=>i===0||LR2[sseq[i-1]]<=LR2[x]),
     'search: rows ordered Pāḷi → Aṭṭhakathā → Ṭīkā', sseq.join(','));

  // per-layer caps: `arati` holds 80/70/29 paragraphs by layer, so a global
  // cap after canon-first ordering starved the other layers entirely
  // (2026-08-08, user-reported with a screenshot).  search.html caps 70/layer.
  const aP=truth(['arati'],'pali-unicode').phrParas,
        aA=truth(['arati'],'atthakatha-unicode').phrParas,
        aT=truth(['arati'],'tika-unicode').phrParas;
  await sq('arati');
  const scnt={};
  for(const e of s.document.querySelectorAll('.hit .lay')) scnt[e.textContent]=(scnt[e.textContent]||0)+1;
  ok(scnt['Pāḷi']===Math.min(70,aP)&&scnt['Aṭṭhakathā']===Math.min(70,aA)&&scnt['Ṭīkā']===Math.min(70,aT),
     'search: every layer draws up to its own cap',
     JSON.stringify(scnt)+' want '+[Math.min(70,aP),Math.min(70,aA),Math.min(70,aT)].join('/'));

  // chips, not a select — the same layer idiom as the reader box
  // (2026-08-08, user request)
  if(typeof s.setLayerChip==='function') s.setLayerChip('tika-unicode');
  await sq('yamakasālānaṁ antare');
  ok(typeof s.setLayerChip==='function'
     && (t6.phrParas+t6.andParas)>0 && s.document.querySelectorAll('.hit').length===t6.phrParas+t6.andParas
     && !!s.document.querySelector('#laychips .lchip.on'),
     'search: layer chip filters', (typeof s.setLayerChip)+' '+s.document.querySelectorAll('.hit').length+' vs '+(t6.phrParas+t6.andParas));
  if(typeof s.setLayerChip==='function') s.setLayerChip('');

  // exact by default, here too — and `tassā` itself, the reader's example:
  // 4,322 occurrences, not the 36,644 of `tassa`+`tassā` merged
  if(typeof s.setFold==='function') s.setFold(false);
  await sq('anīkaratto');
  ok(st().startsWith(XA.occ.toLocaleString()+' occurrence')&&st().includes(' in '+XA.paras+' paragraph'),
     'search exact: anīkaratto counts only anīkaratto', 'want '+XA.occ+'/'+XA.paras+' | '+st());
  ok(/exact/i.test(st()),'search exact: the status names the mode', st());
  await sq('tassā');
  ok(st().startsWith(X['tassā'].occ.toLocaleString()+' occurrence'),
     'search exact: tassā is not tassa', 'want '+X['tassā'].occ+' | '+st());
  ok(typeof s.setFold==='function','search: the fold switch exists');
  if(typeof s.setFold==='function'){
    s.setFold(true); await sq('anikaratto');
    ok(st().startsWith((XA.occ+XB.occ).toLocaleString()+' occurrence')&&/ignored|fold/i.test(st()),
       'search fold: the switch merges the pair and the status says so', st());
    ok(!!s.document.querySelector('#foldbtn.on'),'search fold: the switch state is visible');
    s.setFold(false);
  }
  // a word typed WITHOUT its diacritics must not be a silent "No matches":
  // the status offers the fold switch
  // (`nibbana` itself IS printed once, so it is not the example)
  await sq('patisambhida');
  ok(/ignore|fold/i.test(st()),'search exact: a no-match offers the fold switch', st());

  // search.html's wiring, asserted on its OWN fetch log — the counts above
  // would pass on the legacy path too, and a silent fallback is exactly the
  // drift these two files keep falling into
  const sf=s.__fetched.join(' ');
  ok(/\/tp\/index\.json/.test(sf)&&/\/tp\/[a-z_]+\.json/.test(sf),
     'search wiring: postings shards are fetched');
  ok(!/terms\.compact\.json/.test(sf),
     'search wiring: the 22 MB map is never fetched');
  ok(!/\.idx\.json/.test(sf)&&/\/tx\/[^/]+\/\d+\.json/.test(sf),
     'search wiring: no per-volume idx.json; rows come from tx/ chunks');

  console.log(fails?('FAILED: '+fails+' assertion(s)'):'all green');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('  FAIL  threw: '+(e&&e.message||e)); process.exit(1); });

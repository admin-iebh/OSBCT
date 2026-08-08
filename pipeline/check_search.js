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
function boot(file,base){
  const resolve=mkResolve(base);
  const dom=new JSDOM(fs.readFileSync(file,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
    w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
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
let _T=null;
const T=()=>_T||(_T=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index','terms.compact.json'),'utf8')));
const keysFor=w=>{
  if(w.indexOf('*')>=0){ const rx=new RegExp('^'+w.split('*').map(rxEsc).join('.*')+'$');
    const out=[]; for(const k in T().terms){ if(rx.test(k)){ out.push(k); if(out.length>=500) break; } } return out; }
  if(T().terms[w]) return [w];
  if(w.length<3) return [];
  const out=[]; for(const k in T().terms){ if(k.indexOf(w)>=0){ out.push(k); if(out.length>=500) break; } } return out;
};
// {phrTot, phrParas, andParas, vols} for a query, optionally within one layer
function truth(words,layer){
  const per=words.map(w=>keysFor(w));
  if(per.some(m=>!m.length)) return {phrTot:0,phrParas:0,andParas:0,vols:0};
  const vsets=per.map(m=>new Set(m.flatMap(k=>T().terms[k]||[])));
  let vis=[...vsets[0]].filter(v=>vsets.every(s=>s.has(v)));
  if(layer) vis=vis.filter(v=>T().layers[v]===layer);
  const phRx=new RegExp(words.map(w=>w.indexOf('*')>=0?w.split('*').map(rxEsc).join('\\S*'):rxEsc(w)).join(' '),'g');
  let phrTot=0,phrParas=0,andParas=0; const volsWith=new Set();
  for(const vi of vis){
    const sh=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index',T().vols[vi]+'.idx.json'),'utf8'));
    const maps=per.map(m=>{const mm=new Map(); for(const k of m) for(const [pi,c] of (sh.inv[k]||[])) mm.set(pi,(mm.get(pi)||0)+c); return mm;});
    for(const pi of maps[0].keys()){ if(!maps.every(mm=>mm.has(pi))) continue;
      if(words.length===1){ phrTot+=maps[0].get(pi); phrParas++; volsWith.add(vi); continue; }
      const f=foldS(sh.paras[pi].text);
      phRx.lastIndex=0; let n=0,m; while((m=phRx.exec(f))){ if(!m[0]){phRx.lastIndex++;continue;} n++; }
      if(n>0){phrTot+=n;phrParas++;volsWith.add(vi);} else {andParas++;}
    }
  }
  return {phrTot,phrParas,andParas,vols:volsWith.size};
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
  const t1=truth(['yamakasalanam','antare']);
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
  const t3=truth(['yamakasalanam']);
  const t3c=truth(['yamakasalanam'],'pali-unicode');
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
  const t4=truth(['yamakasal*']);
  await w.doSearch('yamakasal*');
  dd=w.document.getElementById('sdrop');
  ok(t4.phrTot>0 && heads(dd).some(h=>h.startsWith(t4.phrTot.toLocaleString()+' occurrence')),
     'reader: wildcard word', 'want '+t4.phrTot+' | '+heads(dd).join(' / '));
  const t5=truth(['yamakasal*','antare']);
  await w.doSearch('yamakasal* antare');
  dd=w.document.getElementById('sdrop');
  ok(t5.phrTot>0 && heads(dd).some(h=>h.startsWith(t5.phrTot.toLocaleString()+' occurrence')),
     'reader: wildcard inside a phrase', 'want '+t5.phrTot+' | '+heads(dd).join(' / '));

  // 5. the layer chips filter, and the way out is on screen.  Ṭīkā, not the
  // canon: the canon volumes that carry both WORDS carry them in no single
  // PARAGRAPH, so a canon expectation is 0 rows and the assertion would pass
  // vacuously on a build with no filter at all.
  const t6=truth(['yamakasalanam','antare'],'tika-unicode');
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

  await sq('yamakasal*');
  ok(t4.phrTot>0&&st().startsWith(t4.phrTot.toLocaleString()+' occurrence'),
     'search: wildcard word', 'want '+t4.phrTot+' | '+st());

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

  s.document.getElementById('layer').value='tika-unicode';
  await sq('yamakasālānaṁ antare');
  ok((t6.phrParas+t6.andParas)>0 && s.document.querySelectorAll('.hit').length===t6.phrParas+t6.andParas,
     'search: layer select filters', s.document.querySelectorAll('.hit').length+' vs '+(t6.phrParas+t6.andParas));
  s.document.getElementById('layer').value='';

  console.log(fails?('FAILED: '+fails+' assertion(s)'):'all green');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('  FAIL  threw: '+(e&&e.message||e)); process.exit(1); });

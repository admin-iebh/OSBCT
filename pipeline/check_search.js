// GATE: the search box answers a multi-word query, names the book on a row,
// and never counts a non-adjacent hit as the phrase.
//
// WHY.  Reader, 2026-08-08, with a screenshot: a result row said only
// `Pāḷi ¶52`; a query of more than one word was wanted; and "if I type a word
// after searching one it does not search anymore".  The last two were ONE bug:
// the term keys are single words, so a spaced query matched no key, and the
// box painted "No matches" — reported as "stops searching".
//
// WHAT IS ASSERTED, each against ground truth computed HERE from the shards
// with the reference algorithm, never against the reader's own output:
//   1. a two-word PHRASE query paints the phrase count and the phrase rows,
//      and lists paragraphs carrying the words apart SEPARATELY, labelled;
//   2. an occurrence row carries the book resolved from `booktitle/` — on
//      07Di02 that is `Mahāvaggapāḷi`, and NEVER the corpus `book` field
//      (`Pubbenivāsapaṭisaṁyuttakathā`, a kathā one level too deep — the field
//      names the wrong thing in 61 of 118 volumes);
//   3. a single-word query still answers with the exact-term count;
//   4. a multi-word arrival marks the phrase, and where no text node carries
//      the whole phrase, marks each word (`markInEl` fallback).
//
// SELFTEST: `node pipeline/check_search.js --selftest PATH` runs the same
// assertions against another build of reader2.html — point it at the build
// BEFORE the fix (e.g. `git show f82db5ab:site/reader/reader2.html`) and the
// gate must FAIL on assertions 1, 2 and 4.  A gate that has never failed has
// never been shown to guard anything; two versions of `check_fn_markers.js`
// reported their own mistakes as the reader's failures before that rule was
// written down.
//
// Usage:  node pipeline/check_search.js
//         node pipeline/check_search.js --selftest /tmp/reader2_HEAD.html

const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const ROOT=path.dirname(__dirname); const R=path.join(ROOT,'site','reader');
const SELF=process.argv.includes('--selftest');
const READER=SELF?process.argv[process.argv.indexOf('--selftest')+1]
                 :path.join(R,'reader2.html');

const resolve=u=>{u=String(u).split('?')[0];
  if(u.startsWith('../'))return path.join(ROOT,'site',u.slice(3));
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}
  return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(READER,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

// ---- ground truth, straight from the shards --------------------------------
const FOLDM={'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'};
const foldS=s=>(s||'').toLowerCase().replace(/[āīūṁṃṅñṭḍṇḷ]/g,c=>FOLDM[c]||c);
function truth(words){
  const T=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index','terms.compact.json'),'utf8'));
  const sets=words.map(w=>T.terms[w]||[]);
  if(sets.some(s=>!s.length)) return {phrTot:0,phrParas:0,andParas:0};
  let vis=sets[0]; for(const s of sets.slice(1)) vis=vis.filter(v=>s.includes(v));
  const phq=words.join(' ');
  let phrTot=0,phrParas=0,andParas=0;
  for(const vi of vis){
    const sh=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index',T.vols[vi]+'.idx.json'),'utf8'));
    const per=words.map(w=>{const st=new Set(); for(const [pi,c] of (sh.inv[w]||[])) st.add(pi); return st;});
    for(const pi of per[0]){ if(!per.every(s=>s.has(pi))) continue;
      const f=foldS(sh.paras[pi].text);
      let n=0,i=f.indexOf(phq); while(i>=0){n++;i=f.indexOf(phq,i+1);}
      if(n>0){phrTot+=n;phrParas++;} else andParas++;
    }
  }
  return {phrTot,phrParas,andParas};
}

let fails=0;
const ok=(cond,label,detail)=>{ console.log((cond?'  ok    ':'  FAIL  ')+label+(detail?'  ['+detail+']':'')); if(!cond)fails++; };

(async()=>{
  console.log((SELF?'SELFTEST against ':'checking ')+READER);
  const w=boot();
  if(!await ready(w)){ console.log('  FAIL  reader did not boot'); process.exit(1); }

  // 1. two-word phrase, rare on purpose (7 volumes) so the run stays light.
  const t1=truth(['yamakasalanam','antare']);
  await w.doSearch('yamakasālānaṁ antare');
  let dd=w.document.getElementById('sdrop');
  let heads=[...dd.querySelectorAll('.sr-head')].map(h=>h.textContent);
  ok(heads.some(h=>h.startsWith(t1.phrTot.toLocaleString()+' occurrence')),
     'phrase count painted', 'want '+t1.phrTot+' | heads: '+heads.join(' / '));
  ok(t1.andParas===0 || heads.some(h=>h.includes(t1.andParas.toLocaleString()+' paragraph')&&h.includes('not adjacent')),
     'non-adjacent hits listed separately', 'want '+t1.andParas);
  ok(!dd.textContent.includes('No matches'),'a spaced query is not "No matches"');
  const rows1=dd.querySelectorAll('.sresult');
  ok(rows1.length===t1.phrParas+t1.andParas,'row count = phrase paras + AND paras',
     rows1.length+' vs '+(t1.phrParas+t1.andParas));
  ok([...dd.querySelectorAll('.sresult mark')].length>0,'the match is marked in the snippet');

  // 2. the book on a row: 07Di02, whose corpus `book` field is the kathā.
  await w.doSearch('piṇḍapātapaṭikkantānaṁ karerimaṇḍalamāḷe');
  dd=w.document.getElementById('sdrop');
  const wheres=[...dd.querySelectorAll('.sr-where')].map(e=>e.textContent);
  ok(wheres.some(t=>t.includes('Mahāvaggapāḷi')&&t.includes('07Di02')),
     'row names the book from booktitle/', wheres.slice(0,3).join(' | ')||'no .sr-where at all');
  ok(!wheres.some(t=>t.includes('Pubbenivāsa')),
     'row does not print the corpus book field');

  // 3. single word, exact term, count against the shards.
  const T=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index','terms.compact.json'),'utf8'));
  let single=0;
  for(const vi of (T.terms['yamakasalanam']||[])){
    const sh=JSON.parse(fs.readFileSync(path.join(ROOT,'site','index',T.vols[vi]+'.idx.json'),'utf8'));
    for(const [pi,c] of (sh.inv['yamakasalanam']||[])) single+=c;
  }
  await w.doSearch('yamakasālānaṁ');
  dd=w.document.getElementById('sdrop');
  heads=[...dd.querySelectorAll('.sr-head')].map(h=>h.textContent);
  ok(heads.some(h=>h.startsWith(single.toLocaleString()+' occurrence')),
     'single-word count unchanged', 'want '+single+' | heads: '+heads.join(' / '));

  // 4. markInEl: phrase marked as one; words apart marked each.
  const doc=w.document;
  const el1=doc.createElement('div'); el1.textContent='idha yamakasālānaṁ antare pupphitā';
  w.markInEl(el1,'yamakasālānaṁ antare');
  ok(el1.querySelectorAll('mark.shl').length===1,'phrase marked as one run',
     el1.querySelectorAll('mark.shl').length+' marks');
  const el2=doc.createElement('div'); el2.textContent='antare pana kiñci, yamakasālānaṁ pucchā';
  w.markInEl(el2,'yamakasālānaṁ antare');
  ok(el2.querySelectorAll('mark.shl').length===2,'words apart each marked (fallback)',
     el2.querySelectorAll('mark.shl').length+' marks');

  console.log(fails?('FAILED: '+fails+' assertion(s)'):'all green');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('  FAIL  threw: '+(e&&e.message||e)); process.exit(1); });

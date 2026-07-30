// THE FIVE VINAYA NAVS — the checks that hold for all of them, plus the row
// sweep.  Volume-specific counts live in _vin01verify.js and its siblings.
//
//   node --max-old-space-size=4096 _vinnavverify.js <VOL> data
//   node --max-old-space-size=4096 _vinnavverify.js <VOL> rows [from] [to]
//
// THE INVARIANT THAT MATTERS, and it is independent of how the tree was built:
// a printed heading may be absent from the tree only as a REPRINT — that is,
// only if the same label stands in the tree somewhere else.  A label that is
// printed and appears nowhere in the tree is a section the reader cannot reach,
// and no body, apparatus or layout gate can see it: the text is all still
// there.  The declared exceptions are the division names the body reprints
// over each of its parts, which `head_skip` names in the SPEC.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
// !!! A TITLE IS NOT UNIQUE ACROSS NIKĀYAS, and clicking by title alone gave a
// FALSE PASS.  `Mahāvaggapāḷi` is both 03Vin03 (Vinaya) and 07Di02 (Dīgha) —
// two different works the edition really does give the same name, which is why
// `_navdup.js` scopes its no-duplicate-title rule to one nikāya.  This file
// clicked a hardcoded `Vinayapiṭaka` and then the first row labelled with the
// title, so asking it for 07Di02's rows swept 03Vin03's tree instead and
// reported "292 of 292 clicked" for a 156-row volume.  Pick the row whose KEY
// carries the volume, and fall back to the label only when no key is exposed.
// The row carries no key attribute, so the only thing that separates the two
// `Mahāvaggapāḷi` rows is WHERE they sit: scope the search to the span between
// this nikāya's row and the next nikāya's.
const findVol=(w,t,nikaya,others)=>{
  const rows=[...w.document.querySelectorAll('.row')];
  const a=rows.findIndex(r=>lbl(r)===nikaya);
  if(a<0) return rows.find(r=>lbl(r)===t);
  let b=rows.length;
  for(let i=a+1;i<rows.length;i++) if(others.includes(lbl(rows[i]))){b=i;break;}
  return rows.slice(a+1,b).find(r=>lbl(r)===t);
};

const VOL=process.argv[2], MODE=process.argv[3]||'data';
let NIKAYA=null, OTHERS=[];
// the division names the body reprints over each of its parts — the SPEC's
// `head_skip`, restated here so the two files are two readings, not one
const SKIP={'02Vin02':['Bhikkhunivibhaṅge'],
            // 04Vin04 reprints the section's own name in the LOCATIVE over each
            // of its sub-blocks; the fourth is the edition's own misprint
            // ('diṭṭhāyā' for 'diṭṭhiyā', 0-based p71)
            '04Vin04':['Āpattiyā adassane ukkhepanīyakamme',
                       'Āpattiyā appaṭikamme ukkhepanīyakamme',
                       'Pāpikāya diṭṭhiyā appaṭinissagge ukkhepanīyakamme',
                       'Pāpikāya diṭṭhāyā appaṭinissagge ukkhepanīyakamme']};

function printedHeads(){
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const ks=[...new Set([...Object.keys(S),...Object.keys(U)])].sort((a,b)=>a-b);
  const out=[];
  for(const k of ks){
    for(const e of (S[k]||[])) if(e.k!=='gatha'&&e.k!=='booktitle') out.push([e.l,+k]);
    for(const b of (U[k]||[])) if(b.head) out.push([b.head,+k]);
  }
  return out;
}

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  // The CHECKS here were always generic; only the LOOKUP was not — it named
  // the Vinayapiṭaka, so the file could not be pointed at 07Di02 or at any of
  // the twelve canon volumes still to come.  Search every nikāya of the canon
  // layer instead, and keep the one-node invariant as an assertion rather than
  // as an accident of where we looked.
  const canon=nav.layers.find(L=>L.layer==='canon');
  const all=canon.nikayas.flatMap(n=>(n.volumes||[]).filter(v=>v.vol===VOL));
  NIKAYA=(canon.nikayas.find(n=>(n.volumes||[]).some(v=>v.vol===VOL))||{}).nikaya;
  OTHERS=nav.layers.flatMap(L=>(L.nikayas||[]).map(n=>n.nikaya)).filter(n=>n!==NIKAYA);
  console.log('   volume '+VOL+' is in '+NIKAYA);

  if(MODE==='data'){
    A(all.length===1,VOL+' must have exactly one nav node; got '+all.length);
    const bk=all[0];
    A(!bk.suttas&&!bk.pdftoc,'the old font-heuristic keys must be gone');
    A(Array.isArray(bk.tree)&&bk.tree.length>0,'the node must carry a tree');

    const flat=[]; (function walk(ns){for(const n of ns){flat.push([n.label,+n.key.split('#')[1]]);walk(n.kids||[]);}})(bk.tree);
    const heads=printedHeads();
    const key=x=>x[0]+'#'+x[1];
    const inTree=new Set(flat.map(key)), labels=new Set(flat.map(x=>x[0]));
    const skip=new Set(SKIP[VOL]||[]);

    // ---- 1. NO PRINTED HEADING IS LOST ----------------------------------
    const lost=heads.filter(h=>!inTree.has(key(h))&&!labels.has(h[0])&&!skip.has(h[0]));
    A(lost.length===0,lost.length+' printed heading(s) appear nowhere in the tree: '
      +JSON.stringify(lost.slice(0,6)));
    const reprints=heads.filter(h=>!inTree.has(key(h)));
    console.log('   '+heads.length+' printed headings, '+flat.length+' tree rows, '
      +reprints.length+' printed again under a section already in the tree');
    // and every declared skip must really be printed
    for(const s of skip) A(heads.some(h=>h[0]===s),'declared skip never printed: '+s);
    for(const s of skip) A(!labels.has(s),'declared skip is in the tree anyway: '+s);

    // ---- 2. NO ROW IS INVENTED ------------------------------------------
    const printed=new Set(heads.map(key));
    const wrappers=bk.tree.filter(t=>!printed.has(key([t.label,+t.key.split('#')[1]])));
    const invented=flat.filter(x=>!printed.has(key(x))&&!wrappers.some(wp=>wp.label===x[0]));
    A(invented.length===0,invented.length+' row(s) the edition does not print: '
      +JSON.stringify(invented.slice(0,6)));
    // a wrapper row must be a BOOK TITLE the edition prints on its own page
    if(wrappers.length){
      const B=JSON.parse(fs.readFileSync(R+'/booktitle/'+VOL+'.json','utf8'));
      for(const wp of wrappers){
        const o=wp.key.split('#')[1];
        A((B[o]||[]).includes(wp.label),
          'wrapper row '+JSON.stringify(wp.label)+' at ord'+o
          +' must be the title the edition prints there; booktitle has '
          +JSON.stringify(B[o]||null));
      }
    }

    // ---- 3. ORDINALS ----------------------------------------------------
    let prev=-1,back=[];
    for(const [l,o] of flat){ if(o<prev) back.push(l+'@'+o); prev=o; }
    A(back.length===0,'ordinals must not run backwards: '+JSON.stringify(back.slice(0,5)));
    const npara=JSON.parse(fs.readFileSync('site/'+VOL+'.json','utf8')).paragraphs.length;
    A(flat.every(([l,o])=>o>=0&&o<npara),'every key inside 0..'+npara);

    // ---- 4. THE RENDER --------------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,NIKAYA); if(pit){pit.click(); await wait(80);}
    const b=findVol(w,bk.title,NIKAYA,OTHERS);
    A(!!b,'no sidebar row for '+bk.title+' in '+NIKAYA);
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice ------------------------------
  const bk=all[0];
  const from=+(process.argv[4]||0), to=+(process.argv[5]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,NIKAYA); if(pit){pit.click(); await wait(80);}
  const b=findVol(w,bk.title,NIKAYA,OTHERS);
  if(!b){console.log('no sidebar row for '+bk.title+' in '+NIKAYA);process.exit(1);}
  b.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const slice=rows.slice(from,Math.min(to,rows.length));
  let empty=[],whole_open=[],checked=0;
  for(const r of slice){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    else if(n>=whole&&whole>50) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open the WHOLE volume — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

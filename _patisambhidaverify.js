// Paṭisambhidāmagga (26Khu09) — PRESENTATION assertions.
//
// This volume introduces a shape no other has: a NUMBERED UNIT WHOSE CONTENT IS
// PROSE, with no verse lemma to carry it.  Its entry is written
// {"groups": [], "after": [...]}, which relies on `[]` being truthy in JS so
// that block() renders the side-map and suppresses the corpus text.  That is a
// load-bearing subtlety, and nothing else in the project asserts it — so it is
// asserted here, together with the three-level tree and the edition's own
// misprint.
//
//   node --max-old-space-size=4096 _patisambhidaverify.js
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
// Scope any label lookup to its own subtree — "Mātikā", "Niddesa",
// "2. Satipaṭṭhānavāra" and "3. Iddhipādavāra" are each printed more than once
// in this volume, and the whole tree sits in the DOM at once.
const findIn=(el,t)=>[...el.querySelectorAll('.row')].find(r=>lbl(r)===t);

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/26Khu09.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/26Khu09.json','utf8'));
  const H=JSON.parse(fs.readFileSync(R+'/hide/26Khu09.json','utf8'));
  const ps=JSON.parse(fs.readFileSync('site/26Khu09.json','utf8')).paragraphs;
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  const pm=kh.volumes.find(v=>v.vol==='26Khu09');

  // ---- 1. THE PROSE-UNIT SHAPE ----------------------------------------
  const ent=Object.values(V);
  A(ent.length===404,'404 units expected, got '+ent.length);
  A(ent.every(e=>Array.isArray(e.groups)&&e.groups.length===0),
    'every unit must carry an EMPTY groups list — that is what makes block() '+
    'render the side-map instead of the corpus text');
  A(ent.every(e=>Array.isArray(e.after)&&e.after.length),
    'every unit must carry its printed paragraphs in `after`');
  const runon=ent.filter(e=>e.after.length===1&&typeof e.after[0]==='string'&&e.after[0].length>3000);
  A(runon.length===0,runon.length+' units still render as one run-on block');
  const g=ent.reduce((n,e)=>n+e.after.filter(x=>x&&typeof x==='object'&&x.gatha).length,0);
  A(g===20,'20 quoted gāthā blocks expected across the volume, got '+g);
  A(H['351']===1,'ord351 (the leaked "7. Dhammacakkakathā  1. Saccavāra" line) must be hidden');
  // and the colophon that follows it must NOT be anchored to that hidden ordinal
  const U=JSON.parse(fs.readFileSync(R+'/uddana/26Khu09.json','utf8'));
  A(!U['351'],'no side-map block may be anchored to the hidden ord351 — it would never render');

  // ---- 2. THE TREE = the edition's own mātikā, three levels -------------
  A(!!pm&&Array.isArray(pm.tree),'26Khu09 has no tree node');
  A(pm.tree.length===3&&JSON.stringify(pm.tree.map(t=>t.label))===
      JSON.stringify(['1. Mahāvagga','2. Yuganaddhavagga','3. Paññāvagga']),
    'three vaggas expected, got '+JSON.stringify(pm.tree.map(t=>t.label)));
  // MIXED DEPTH IS THE EDITION'S: some kathās have sections, others none.
  const kath=pm.tree.flatMap(t=>t.kids);
  A(kath.some(k=>k.kids.length===0),'no kathā is a bare leaf — the edition prints several');
  A(kath.some(k=>k.kids.length>0),'no kathā has sections — the edition prints many');
  // The edition's own thirty kathās, plus the Mahāvagga's "Mātikā" section,
  // which the body heads but the front mātikā does not list.
  A(kath.filter(k=>/kathā$|tathā$/.test(k.label)).length===30,
    'thirty kathās expected, got '+kath.filter(k=>/kathā$|tathā$/.test(k.label)).length);
  const nk=kath.find(k=>k.label==='1. Ñāṇakathā');
  A(!!nk&&nk.kids.length===48,'Ñāṇakathā sections = '+(nk&&nk.kids.length)+
    ' (the mātikā lists 48 entries for it, several covering ranges such as "20-24.")');
  // A kathā the mātikā gives a page and nothing under: Gatikathā, Kammakathā,
  // Vipallāsakathā, Maggakathā and eleven more are printed that way.
  A(!!kath.find(k=>k.label==='6. Gatikathā'&&k.kids.length===0),
    'Gatikathā must be a bare leaf — the mātikā gives it a page and no sections');
  // …and one the mātikā gives no sections but the BODY heads anyway.  That is
  // not a defect: the heading is printed, so it belongs in the tree, and the
  // nav builder reports every such case instead of dropping it.
  A(!!kath.find(k=>k.label==='5. Vimokkhakathā'&&k.kids.length===1),
    'Vimokkhakathā should carry the one section the body prints ("Niddesa")');
  // the edition's misprint reaches the tree, uncorrected
  A(!!kath.find(k=>k.label==='5. Virāgatathā'),
    "the body's misprinted '5. Virāgatathā' must be kept as the edition sets it");

  // ---- 3. THE RENDER ---------------------------------------------------
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  A(!err,'JS error on boot: '+err);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(80);}}
  const book=find(w,'Paṭisambhidāmaggapāḷi');
  A(!!book,'no Paṭisambhidāmaggapāḷi book row');
  book.click(); await wait(250);
  for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>2000)break;}
  const doc=w.document, txt=doc.querySelector('#scroll').textContent;

  const bt=doc.querySelector('#scroll .head.booktitle'), bs=doc.querySelector('#scroll .head.bookseries');
  A(!!bt&&N(bt.textContent)==='Paṭisambhidāmaggapāḷi','book title not drawn: '+(bt&&bt.textContent));
  A(!!bs&&N(bs.textContent)==='Khuddakanikāya','series line not drawn: '+(bs&&bs.textContent));
  A(doc.querySelectorAll('#scroll .incipit').length===1,'exactly one homage');
  A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>/amo tassa \S+ [Aa]rahato/.test(p.textContent)),
    'the homage is rendered as body text as well as as an incipit');

  // A UNIT IS PROSE: many paragraphs, drawn as prose and not as verse.
  const pros=doc.querySelectorAll('#scroll .gatha-after').length;
  A(pros>200,'prose paragraphs rendered = '+pros+' (the corpus holds one run-on block per unit)');
  // …and its number OPENS its first printed paragraph, inline with the text.
  // USER-REPORTED: the number was emitted as a block-level sibling of the prose
  // <div> and so stacked on a line of its own, which the page never does.
  // Every word was present and in order, so no content gate could see it.
  const cps=[...doc.querySelectorAll('#scroll .para.canon')].filter(p=>p.querySelector('.pn'));
  const stacked=cps.filter(p=>!p.querySelector('.pn').closest('.gatha-after')
                            && !p.querySelector('.pn').closest('.gatha'));
  A(cps.length>300&&stacked.length===0,
    stacked.length+' of '+cps.length+' prose units still stack their number on its own line');
  const p0=cps[0];
  A(/^\s*1\.\s*Sotāvadhāne paññā sutamaye ñāṇaṁ\./.test(
      (p0.querySelector('.gatha-after')||{textContent:''}).textContent.replace(/\s+/g,' ').trim()),
    'the first unit must read "1. Sotāvadhāne paññā sutamaye ñāṇaṁ." on one line, got '+
    ((p0.querySelector('.gatha-after')||{textContent:''}).textContent||'').replace(/\s+/g,' ').trim().slice(0,60));

  // headings, at all three levels, and the section colophons
  A(/1\.\s*Mahāvagga/.test(txt),'the vagga heading is not rendered');
  A(/1\.\s*Ñāṇakathā/.test(txt),'the kathā heading is not rendered');
  A(/1\.\s*Sutamayañāṇaniddesa/.test(txt),'the niddesa heading is not rendered');
  A(/Sutamayañāṇaniddeso paṭhamo/.test(txt),'a section-end colophon is not rendered');
  A(/Mātikā niṭṭhitā/.test(txt),"the Mahāvagga mātikā's own colophon is not rendered");
  // the HANGING-LIST pages: the Mahāvagga mātikā's 73 items are separate units
  A(/Sotāvadhāne paññā sutamaye ñāṇaṁ/.test(txt)&&/Anāvaraṇañāṇaṁ/.test(txt),
    "the Mahāvagga's own mātikā list is not rendered");
  // the leaked heading is a heading, not body text, and not doubled
  A((txt.match(/7\.\s*Dhammacakkakathā/g)||[]).length===1,
    '"7. Dhammacakkakathā" must render exactly once, as a heading');
  A(/1\.\s*Saccavāra/.test(txt),'the vāra sharing its printed line with the kathā is missing');
  // the colophon that the hidden ordinal used to swallow
  A(/Paṭisambhidākathā niṭṭhitā/.test(txt),
    'the Paṭisambhidākathā colophon is not rendered (it was anchored to a hidden ordinal)');
  // quoted verse inside the prose is drawn as verse
  A([...doc.querySelectorAll('#scroll .gatha')].some(e=>/Vatthusaṅkamanā ceva/.test(e.textContent)),
    'gāthā quoted inside the commentary is not drawn as verse');
  // the printed heading no stem reached until the mātikā check found it
  A(/Mūlamūlakādidasaka/.test(txt),'"Mūlamūlakādidasaka" is missing');
  A([...doc.querySelectorAll('#scroll .head')].some(e=>/Mūlamūlakādidasaka/.test(e.textContent)),
    '"Mūlamūlakādidasaka" renders as body text instead of as a heading');
  // the book closes with its uddāna and colophon
  A(/Paññāvaggo tatiyo/.test(txt),'the last vagga colophon is not rendered');
  A(/Paṭisambhidāmaggapāḷi niṭṭhitā/.test(txt),'the book-end colophon is not rendered');
  A(/Kathikānaṁ visālāya, yogīnaṁ ñāṇajotananti/.test(txt.replace(/\s+/g,' ')),
    'the closing Uddānagāthā is not rendered');
  // the printed word index must never reach the body
  A(!/Padānukkamo/.test(txt),"the volume's printed word index is being rendered");

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

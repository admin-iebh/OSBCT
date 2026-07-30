// Dhammasaṅgaṇī (29Abhi01) — PRESENTATION assertions.
//
// The first volume of the Abhidhamma, and everything it introduced that no
// content gate can see:
//   * headings recognised BY FORM, not by a stem list — a title carries no
//     terminal stop, its colophon echoes it with one (Tika / Tikaṁ.);
//   * a volume with NO gāthā at all, so the Rūpakaṇḍa's one-item-per-line
//     lists must render as prose and not as verse;
//   * the corpus splice this volume shares with the Paṭṭhāna — a printed
//     heading glued onto the tail of the previous paragraph;
//   * the title page's series line, which must be drawn as a title and not as
//     a heading of the body.
//
//   node --max-old-space-size=4096 _abhi01verify.js [data|rows]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='29Abhi01', PART=process.argv[2]||'all';

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
  const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
  const B=JSON.parse(fs.readFileSync(R+'/booktitle/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const all=ab.volumes.filter(v=>v.vol===VOL);

  // ---- 1. ONE BOOK, ONE NODE, and the tree the mātikā prints -----------
  A(all.length===1,'29Abhi01 must have exactly one nav node; got '+all.length);
  const bk=all[0];
  A(Array.isArray(bk.tree),'the node must be the `tree` shape (was the old flat pdftoc)');
  A(bk.first===VOL+'#0','book first = '+bk.first);
  A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(
      ['Mātikā','1. Cittuppādakaṇḍa','2. Rūpakaṇḍa','3. Nikkhepakaṇḍa','4. Aṭṭhakathākaṇḍa']),
    'the four kaṇḍas and the opening Mātikā, in printed order; got '
    +JSON.stringify(bk.tree.map(t=>t.label)));
  const flat=[];(function walk(ns){for(const n of ns){flat.push(n);walk(n.kids||[]);}})(bk.tree);
  A(flat.length===146,'146 nav nodes; got '+flat.length);
  // "Mātikā" is printed TWICE — as the volume's own opening mātikā and inside
  // the Rūpakaṇḍa.  Matching the top level by label alone put the second one
  // at the top of the tree; the sequence is consumed in printed order.
  // ---- the second level, and the body's own colophons that prove it -----
  // The thirteen gocchakas and dukas are INSIDE the Dukamātikā, not siblings
  // of it: the block runs from "Dukamātikā" to "Piṭṭhidukaṁ." and the next
  // printed line is the colophon "Abhidhammadukamātikā." that closes it.  The
  // printed mātikā sets all fifteen at ONE indent and so proves nothing.
  const THIRTEEN=['Hetugocchaka','Cūḷantaraduka','Āsavagocchaka','Saññojanagocchaka',
    'Ganthagocchaka','Oghagocchaka','Yogagocchaka','Nīvaraṇagocchaka',
    'Parāmāsagocchaka','Mahantaraduka','Upādānagocchaka','Kilesagocchaka','Piṭṭhiduka'];
  for(const [topL,midL] of [['Mātikā','Dukamātikā'],
                            ['3. Nikkhepakaṇḍa','Dukanikkhepa'],
                            ['4. Aṭṭhakathākaṇḍa','Duka-atthuddhāra']]){
    const top=bk.tree.find(t=>t.label===topL);
    A(!!top,'missing top: '+topL);
    const mid=(top.kids||[]).find(k=>k.label===midL);
    A(!!mid,midL+' must be a child of '+topL);
    A(JSON.stringify((mid.kids||[]).map(k=>k.label))===JSON.stringify(THIRTEEN),
      'the thirteen gocchakas and dukas must sit UNDER '+midL+', in printed '
      +'order; got '+JSON.stringify((mid.kids||[]).map(k=>k.label)));
    A(!(top.kids||[]).some(k=>THIRTEEN.includes(k.label)),
      'none of the thirteen may be a sibling of '+midL);
  }
  // …and the Mātikā's own three, with Suttantikadukamātikā a SIBLING of the
  // Dukamātikā and not swallowed by it
  A(JSON.stringify(bk.tree.find(t=>t.label==='Mātikā').kids.map(k=>k.label))
      ===JSON.stringify(['Tikamātikā','Dukamātikā','Suttantikadukamātikā']),
    'the Mātikā has three second-level sections');
  {
    // the colophon span, read from the printed stream
    const ev=[];
    for(const k of Object.keys(S).sort((a,b)=>a-b)) for(const e of S[k]) if(e.k!=='gatha') ev.push([+k,'h',e.l]);
    for(const k of Object.keys(U).sort((a,b)=>a-b)) for(const b of U[k]){
      if(b.head) ev.push([+k,'h',b.head]);
      if(!b.plain) for(const l of (b.lines||[])) ev.push([+k,'c',l]);
    }
    ev.sort((a,b)=>a[0]-b[0]);
    const ix=(kind,t)=>ev.findIndex(x=>x[1]===kind&&x[2]===t);
    A(ix('h','Dukamātikā')<ix('h','Piṭṭhiduka'),'Dukamātikā opens before Piṭṭhiduka');
    A(ix('h','Piṭṭhiduka')<ix('c','Abhidhammadukamātikā.'),
      'the closing colophon must follow the last of the thirteen');
    A(ix('c','Abhidhammadukamātikā.')<ix('h','Suttantikadukamātikā'),
      'Suttantikadukamātikā must begin only after that colophon closes the block');
  }

  const rk=bk.tree.find(t=>t.label==='2. Rūpakaṇḍa');
  A(rk.kids.some(k=>k.label==='Mātikā'&&k.kids.length===11),
    "the Rūpakaṇḍa's own Mātikā must be a group under it, not a second top");
  A(rk.kids.some(k=>k.label==='Rūpavibhatti'&&k.kids.length===12),'Rūpavibhatti group');
  A(bk.tree[0].key===VOL+'#0','the opening Mātikā starts the book');

  // ---- 2. A VOLUME WITH NO GĀTHĀ --------------------------------------
  const ent=Object.entries(V);
  A(ent.length===1780,'1780 numbered units; got '+ent.length);
  A(ent.every(([k,e])=>Array.isArray(e.groups)&&e.groups.length===0),
    'every unit of this volume is PROSE — no unit may carry a gāthā; '
    +ent.filter(([k,e])=>e.groups&&e.groups.length).length+' do');
  const gb=ent.reduce((n,[k,e])=>n+(e.after||[]).filter(x=>x&&typeof x==='object'&&x.gatha).length,0);
  A(gb===0,'no {gatha} block anywhere in the volume; got '+gb);
  // …and the Rūpakaṇḍa lists, which the verse-run rule reads as a gāthā and
  // whose items are complete sentences, so pāda punctuation cannot save them
  // The Rūpakaṇḍa's eleven divisions have NO numbered unit of their own, so
  // their items live in the uddāna stream of the previous unit, in printed
  // order — one entry per printed item, which is how the edition sets them.
  const prose=[];
  for(const [k,e] of ent) for(const f of ['before','after'])
    for(const x of (e[f]||[])) if(typeof x==='string') prose.push(x);
  for(const k of Object.keys(U)) for(const b of U[k])
    if(b.plain) for(const l of (b.lines||[])) prose.push(l);
  for(const q of ['Atthi rūpaṁ upādā, atthi rūpaṁ no upādā.',
                  'Atthi rūpaṁ itthindriyaṁ, atthi rūpaṁ na itthindriyaṁ.'])
    A(prose.some(x=>x.includes(q)),'a Rūpakaṇḍa list item must render as prose: '+q);
  // …one entry per printed ITEM, not run together into a paragraph
  A(prose.filter(x=>/^Atthi rūpaṁ /.test(x)).length>=38,
    'the duka list must keep one entry per printed item; got '
    +prose.filter(x=>/^Atthi rūpaṁ /.test(x)).length);
  // …and in PRINTED ORDER: the division's heading and opener above its list,
  // its closing line and colophon below it, and only then the next division.
  {
    const b=U['747']||[];
    const ix=t=>b.findIndex(x=>(x.lines||[]).some(l=>l===t));
    const ih=b.findIndex(x=>x.head==='Duka');
    A(ix('Ekakaṁ.')>=0 && ih>ix('Ekakaṁ.'),
      "the Duka heading must follow the Ekaka's colophon");
    A(ix('Atthi rūpaṁ upādā, atthi rūpaṁ no upādā.')>ih,
      'its list must follow its heading');
    A(ix('Evaṁ duvidhena rūpasaṅgaho.')>ix('Atthi rūpaṁ kabaḷīkāro āhāro, atthi rūpaṁ na kabaḷīkāro āhāro.'),
      'its closing line must follow the last item of its list');
    A(ix('Dukaṁ.')>ix('Evaṁ duvidhena rūpasaṅgaho.'),
      'its colophon must come last');
  }
  A(ent.every(([k,e])=>Array.isArray(e.after)&&e.after.length),
    'every prose unit must carry its printed paragraphs in `after`');

  // ---- 3. HEADINGS BY FORM, COLOPHONS BY THE TERMINAL STOP ------------
  const heads=[],colos=[];
  for(const k of Object.keys(S)) for(const e of S[k]) if(e.k!=='gatha') heads.push(e.l);
  for(const k of Object.keys(U)) for(const b of U[k]){
    if(b.head) heads.push(b.head);
    for(const l of (b.lines||[])) if(!b.plain) colos.push(l);
  }
  A(heads.every(h=>!h.endsWith('.')),
    'a heading is a title and carries NO terminal stop; offenders: '
    +JSON.stringify(heads.filter(h=>h.endsWith('.')).slice(0,4)));
  for(const [h,c] of [['Tika','Tikaṁ.'],['Catukka','Catukkaṁ.'],
                      ['Hetugocchaka','Hetugocchakaṁ.'],['Duka','Dukaṁ.']]){
    A(heads.includes(h),'missing heading: '+h);
    A(colos.includes(c),'missing colophon: '+c);
  }
  A(heads.every(h=>!h.includes(',')),'no heading may carry a comma');
  A(Object.keys(H).length===0,
    'nothing should be hidden here — the leak scan must not use the form test '
    +'on corpus paragraphs; got '+JSON.stringify(Object.keys(H).slice(0,6)));

  // ---- 4. THE CORPUS SPLICE THIS VOLUME SHARES WITH THE PAṬṬHĀNA ------
  // The corpus glued "Evaṁ duvidhena rūpasaṅgaho." to "Tividhena rūpasaṅgaho–"
  // and dropped the colophon "Dukaṁ." and the heading "Tika" between them.
  A(colos.includes('Evaṁ duvidhena rūpasaṅgaho.'),'the closing line of the duka section');
  A(colos.includes('Dukaṁ.'),'the colophon the corpus dropped');
  A(heads.includes('Tika'),'the heading the corpus dropped');

  // ---- 5. THE TITLE PAGE'S OWN STACK ----------------------------------
  A(JSON.stringify(B['0'])===JSON.stringify(['Abhidhammapiṭaka','Dhammasaṅgaṇīpāḷi']),
    'the printed stack = '+JSON.stringify(B['0']));
  A(!heads.includes('Abhidhammapiṭaka'),
    'the piṭaka name is the title page\'s series line, not a heading of the body');
  A(Object.keys(I).length===1&&I['0'],'one printed homage, at ord0');

  if(PART!=='rows'){
    const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    for(const t of ['Pāḷi','Abhidhammapiṭaka']){const r=find(w,t); if(r){r.click(); await wait(60);}}
    const b=find(w,'Dhammasaṅgaṇīpāḷi');
    A(!!b,'no Dhammasaṅgaṇīpāḷi book row');
    b.click(); await wait(250);
    for(let k=0;k<80;k++){await wait(60);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>300000)break;}
    const doc=w.document,t=doc.querySelector('#scroll').textContent;
    A(t.length>300000,'the whole book should render as one scroll; got '+t.length);
    A(doc.querySelectorAll('#scroll .incipit').length===1,'exactly one homage');
    A(doc.querySelectorAll('#scroll .gatha').length===0,
      'this volume prints no verse; got '+doc.querySelectorAll('#scroll .gatha').length+' .gatha blocks');
    A(/Abhidhammapiṭaka/.test((doc.querySelector('#scroll .head.bookseries')||{}).textContent||''),
      'the piṭaka name must be drawn as the series line above the book title');
    A(/Dhammasaṅgaṇīpāḷi/.test((doc.querySelector('#scroll .head.booktitle')||{}).textContent||''),
      'the book title must be drawn above the homage');
    for(const q of ['Evaṁ duvidhena rūpasaṅgaho.','Dukaṁ.','Tividhena rūpasaṅgaho'])
      A(t.includes(q),'not rendered: '+q);
    // the four kaṇḍa heads and a sample of each level
    for(const q of ['1. Cittuppādakaṇḍa','2. Rūpakaṇḍa','3. Nikkhepakaṇḍa',
                    '4. Aṭṭhakathākaṇḍa','Suttantikadukamātikā','Piṭṭhiduka'])
      A(t.includes(q),'heading not rendered: '+q);
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>{
        const f=p.querySelector('.pn');
        return f && !f.closest('.gatha') && !f.closest('.gatha-after');
      }),'some unit stacks its number on a line of its own');
  }

  if(PART!=='data'){
    const w=boot(); if(!await ready(w)){console.log('nav never rendered (2)');process.exit(1);}
    for(const t of ['Pāḷi','Abhidhammapiṭaka']){const r=find(w,t); if(r){r.click(); await wait(60);}}
    const b=find(w,'Dhammasaṅgaṇīpāḷi'); b.click(); await wait(200);
    let seen=new Set(),rows=[];
    for(let pass=0;pass<5;pass++){
      rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
      let grew=false;
      for(const r of rows){const k=lbl(r); if(seen.has(k))continue; seen.add(k); r.click(); await wait(5); grew=true;}
      if(!grew) break;
    }
    rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
    A(rows.length>=140,'every tree node should have a row; got '+rows.length);
    const empty=[];
    for(const r of rows){
      r.click(); await wait(5);
      for(let k=0;k<40;k++){await wait(5);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      if(!w.document.querySelectorAll('#scroll .para.canon').length) empty.push(lbl(r));
    }
    A(empty.length===0,empty.length+' of '+rows.length+' nav row(s) open nothing — '
      +JSON.stringify(empty.slice(0,8)));
    const cnt=async(name)=>{
      const r=[...b.parentElement.querySelectorAll('.row')].find(x=>lbl(x)===name);
      if(!r) return -1;
      r.click(); await wait(20);
      for(let k=0;k<40;k++){await wait(10);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      return w.document.querySelectorAll('#scroll .para.canon').length;
    };
    const kanda=await cnt('2. Rūpakaṇḍa'), grp=await cnt('Rūpavibhatti'), leaf=await cnt('Tikaniddesa');
    A(kanda>grp&&grp>leaf&&leaf>0,
      'each level must open a smaller slice than its parent: kaṇḍa '+kanda+
      ', group '+grp+', leaf '+leaf);
  }

  console.log(`\n[${PART}] ${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

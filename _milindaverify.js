// Milindapañha (28Khu11) — PRESENTATION assertions.
//
// Everything this volume introduced that no gate can see, asserted in the same
// change that introduced it (HANDOFF.md's standing lesson):
//   * a numbered unit that IS a gāthā, told from a prose unit that QUOTES one
//     by the hanging-quotation rule — 1 verse unit against 10 prose;
//   * a display block that is PROSE, not verse (the indented sutta quotations);
//   * SECTIONS WITH NO NUMBERED UNIT of their own — the Dhutaṅgapañha, the
//     Opamma Mātikā, the Meṇḍakapañhārambhakathā and its six parts, the
//     Nigamana, and the pañha the edition numbers "(3)" in parentheses —
//     which now render from the uddāna stream of the previous unit;
//   * two printed headings on ONE line set in the BODY column (p245);
//   * the four-level tree, and every one of its rows opening its own text.
//
//   node --max-old-space-size=4096 _milindaverify.js
//
// The nav sweep clicks all 276 rows and takes ~40s on its own, so the script
// also takes a part argument for hosts with a short command budget:
//   node … _milindaverify.js data    (everything except the row sweep)
//   node … _milindaverify.js rows          (the row sweep alone)
//   node … _milindaverify.js rows 0 140    (…and a slice of it)
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='28Khu11';
const PART=process.argv[2]||'all';   // all | data | rows
const R0=process.argv[3]!=null?+process.argv[3]:0;
const R1=process.argv[4]!=null?+process.argv[4]:1e9;

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
  const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  const all=kh.volumes.filter(v=>v.vol===VOL);

  // ---- 1. ONE BOOK, ONE NODE ------------------------------------------
  // The invariant is one node per BOOK, not per volume, and a builder that
  // replaces "the" node of a volume leaves the others behind — that shipped
  // once, on 27Khu10.  This volume holds one book, so exactly one node.
  A(all.length===1,'28Khu11 must have exactly one nav node; got '+all.length+
    ' — '+JSON.stringify(all.map(v=>v.title)));
  const bk=all[0];
  A(!!bk&&Array.isArray(bk.tree),'the node must be the `tree` shape');
  A(bk.first===VOL+'#0','book first = '+(bk&&bk.first));
  A(Object.keys(I).length===1&&I['0'],'one printed homage, at ord0');

  // ---- 2. THE TREE, four levels, checked against the edition -----------
  const tops=bk.tree.map(t=>t.label);
  A(JSON.stringify(tops)===JSON.stringify(
      ['1. Bāhirakathā','2. Milindapañha','4. Meṇḍakapañha','5. Anumānapañha',
       '6. Opammakathāpañha','Nigamana']),
    'kaṇḍa heads as the BODY prints them (no "3.", and "6." not the mātikā\'s '
    +'second "5.") = '+JSON.stringify(tops));
  const flat=[];(function walk(ns){for(const n of ns){flat.push(n);walk(n.kids||[]);}})(bk.tree);
  const vaggas=bk.tree.reduce((a,t)=>a+t.kids.filter(k=>/vagga$/i.test(k.label)).length,0);
  A(vaggas===23,'23 vaggas printed in the body; got '+vaggas);
  A(flat.length===276,'276 nav nodes; got '+flat.length);
  // four levels: a kaṇḍa -> a vagga -> a pañha
  const mv=bk.tree.find(t=>t.label==='2. Milindapañha');
  A(mv.kids.length===9,'2. Milindapañha has 7 vaggas + pucchāvisajjanā + '
    +'ārambhakathā = 9; got '+mv.kids.length);
  A((mv.kids.find(k=>k.label==='1. Mahāvagga')||{kids:[]}).kids.length===16,
    'Mahāvagga has 16 pañhas');
  A((mv.kids.find(k=>k.label==='Meṇḍakapañhārambhakathā')||{kids:[]}).kids.length===6,
    'Meṇḍakapañhārambhakathā has its six printed parts');
  A(bk.tree.find(t=>t.label==='6. Opammakathāpañha').kids.some(k=>k.label==='Mātikā'),
    'the Opammakathā mātikā is a section of its own');
  // the edition's own misprints, preserved as each page sets them
  A(flat.some(n=>n.label==='6. Satapattaṅgapañhā'),
    "the body's long-ā 'Satapattaṅgapañhā' must survive in the tree");
  A(flat.some(n=>n.label==='6. Apuññapañha'),
    "the body's 'Apuññapañha' (mātikā: 'Apaññapañha') must survive");

  // ---- 3. UNITS: one gāthā, the rest prose ------------------------------
  const ent=Object.entries(V);
  A(ent.length===258,'258 numbered units (261 corpus ¶ less 3 leaked headings); got '+ent.length);
  const vs=ent.filter(([k,e])=>e.groups&&e.groups.length);
  A(vs.length===1&&vs[0][0]==='0',
    'exactly ONE unit is itself a gāthā — the opening "Milindo nāma so rājā" '
    +'at ord0; got '+JSON.stringify(vs.map(x=>x[0])));
  A(vs[0][1].groups[0].length===10,
    'the opening gāthā keeps all ten printed pādas; got '+vs[0][1].groups[0].length);
  // the ten units the hanging-quotation rule keeps as PROSE
  for(const k of ['165','181','221','229','241']){
    const e=V[k]; if(!e) continue;
    A(!(e.groups&&e.groups.length),
      'ord'+k+' opens "…bhāsitampetaṁ Bhagavatā–" and QUOTES a gāthā; it must '
      +'not itself be stored as one');
  }
  A(ent.filter(([k,e])=>!e.groups||!e.groups.length).every(([k,e])=>
      Array.isArray(e.after)&&e.after.length),
    'every prose unit must carry its printed paragraphs in `after`');
  const gb=ent.reduce((n,[k,e])=>n+(e.after||[]).filter(x=>x&&typeof x==='object'&&x.gatha).length,0);
  A(gb>50,'quoted gāthā blocks inside the prose = '+gb);

  // ---- 4. A DISPLAY BLOCK IS NOT ALWAYS VERSE ---------------------------
  // The edition indents long PROSE quotations exactly as it indents a gāthā.
  // Every one of these was being stored as a {"gatha": …} block and drawn as
  // italic verse with the printed line breaks kept.
  const allg=[];
  for(const [k,e] of ent) for(const x of (e.after||[]))
    if(x&&typeof x==='object'&&x.gatha) allg.push(x.gatha.join(' '));
  for(const q of ['Sāmampi kho etaṁ Sīvaka veditabbaṁ',
                  'bahuppadā vā rūpino vā arūpino vā',
                  'ayaṁ dukkhasamudayo”ti vitakkeyyātha',
                  'itarītarapiṇḍapātasantuṭṭhiyā ca vaṇṇavādī'])
    A(!allg.some(g=>g.includes(q)),
      'a PROSE quotation is stored as a gāthā: '+q);
  A(allg.some(g=>g.includes('Sāmayiko ca kusalo, paṭibhāne ca kovido')),
    'a real quoted gāthā must still be stored as one');

  // ---- 5. LEAKED CORPUS HEADINGS ----------------------------------------
  A(JSON.stringify(Object.keys(H).sort((a,b)=>a-b))===JSON.stringify(['38','98','162']),
    'the three corpus paragraphs that are really printed headings must be '
    +'hidden; got '+JSON.stringify(Object.keys(H)));

  // ---- 6. SECTIONS WITH NO NUMBERED UNIT --------------------------------
  // Each is a heading the page sets with no "N." unit under it, so it lives in
  // the uddāna stream of the PREVIOUS unit.  Before this they piled up in the
  // NEXT unit's `before`, all their headings stacked above all their text.
  const uh=[];for(const k of Object.keys(U)) for(const b of U[k]) if(b.head) uh.push([k,b.head]);
  for(const [ord,h] of [['110','Milindapañhapucchāvisajjanā'],
                        ['110','Meṇḍakapañhārambhakathā'],
                        ['110','Ācariyaguṇa'],['110','Upāsakaguṇa'],
                        ['164','3. Gihipabbajitasammāpaṭipattipañha'],
                        ['193','2. Dhutaṅgapañha'],['193','6. Opammakathāpañha'],
                        ['193','Mātikā'],['260','Nigamana']])
    A(uh.some(x=>x[0]===ord&&x[1]===h),'missing orphan-section head at ord'+ord+': '+h);
  A(uh.every(x=>x[1]!==null),'no null heads');
  // …and the INTERLEAVING: Ācariyaguṇa must keep its own text, which is the
  // paragraph the page sets under it and not the one under Upāsakaguṇa.
  const b110=U['110'];
  const ia=b110.findIndex(b=>b.head==='Ācariyaguṇa');
  const iu=b110.findIndex(b=>b.head==='Upāsakaguṇa');
  A(ia>=0&&iu>ia,'Ācariyaguṇa must precede Upāsakaguṇa');
  A(iu-ia>=2,'Ācariyaguṇa must keep at least one paragraph of its own before '
    +'Upāsakaguṇa opens; gap = '+(iu-ia));
  A(/mantisahāyo/.test((b110[ia].lines||[]).join(' ')),
    'Ācariyaguṇa keeps the paragraph the page sets under IT');
  A(/sampaṭicchitvā dasa upāsakassa/.test((b110[iu].lines||[]).join(' ')),
    'Upāsakaguṇa opens its own printed paragraph');

  // ---- 7. THE BOOK'S CLOSE, in printed order ----------------------------
  const tail=U['260'];
  A(!!tail&&tail.length>3,'the Nigamana and the closing gāthā must be stored');
  A(tail[tail.length-1].lines.join(' ')==='Milindapañho niṭṭhito.',
    'the book-end colophon must come last; got '+
    JSON.stringify(tail[tail.length-1].lines));
  A(tail.some(b=>b.head==='Nigamana'&&(b.lines||[]).some(l=>/Iti chasu kaṇḍesu/.test(l))),
    'the Nigamana heading must carry its own opening paragraph');
  A(tail.some(b=>!b.plain&&(b.lines||[]).some(l=>/Metteyyaṁ’nāgate passe/.test(l))),
    'the closing gāthā must be stored as verse');

  // ---- 8. TWO HEADINGS ON ONE LINE, IN THE BODY COLUMN ------------------
  // p245 sets "1. Buddhavagga        1. Dvinnaṁ Buddhānaṁ anuppajjamānapañha"
  // at indent 5, not centred, and it was read as the Anumānapañha's first
  // NUMBERED UNIT — which took an ordinal and desynced every unit after it.
  const s163=(S['163']||[]).map(e=>e.l);
  A(s163.includes('1. Buddhavagga')&&s163.includes('1. Dvinnaṁ Buddhānaṁ anuppajjamānapañha'),
    'the p245 double heading must be split into two; got '+JSON.stringify(s163));

  // ---- 9. THE RENDER ----------------------------------------------------
  if(PART!=='rows'){
    const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(80);}}
    const b=find(w,'Milindapañhapāḷi');
    A(!!b,'no Milindapañhapāḷi book row');
    b.click(); await wait(300);
    for(let k=0;k<80;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>200000)break;}
    const doc=w.document, t=doc.querySelector('#scroll').textContent;
    A(t.length>400000,'the whole book should render as one scroll; got '+t.length+' chars');
    A(doc.querySelectorAll('#scroll .incipit').length===1,'exactly one homage');
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>/amo tassa \S+ [Aa]rahato/.test(p.textContent)),
      'the homage is rendered as body text as well as as an incipit');
    A(/Milindapañhapāḷi/.test((doc.querySelector('#scroll .head.booktitle')||{}).textContent||''),
      'the book title must be drawn above the homage');
    for(const s of ['Pubbayogādi','Meṇḍakapañhārambhakathā','Ācariyaguṇa',
                    'Upāsakaguṇa','Nigamana','2. Dhutaṅgapañha',
                    '3. Gihipabbajitasammāpaṭipattipañha'])
      A(t.includes(s),'not rendered: '+s);
    A(/Milindapañho niṭṭhito\./.test(t),'the book-end colophon is not rendered');
    A((t.match(/Imasmiṁ vagge/g)||[]).length===15,
      'the edition closes 15 of its 22 vaggas with a count of its pañhas; '
      +'rendered '+(t.match(/Imasmiṁ vagge/g)||[]).length);
    // the opening gāthā is verse, with its number hanging inside it
    const first=doc.querySelectorAll('#scroll .para.canon')[0];
    A(!!first.querySelector('.gatha'),'the opening unit must render as a gāthā');
    A(!!(first.querySelector('.pn')||{}).closest&&!!first.querySelector('.pn').closest('.gatha'),
      'its number must hang inside the gāthā, not stack above it');
    // …and no prose unit stacks its number on a line of its own
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>{
        const f=p.querySelector('.pn');
        return f && !f.closest('.gatha') && !f.closest('.gatha-after');
      }),'some unit stacks its number on a line of its own');
    // a prose unit that quotes verse: the question is prose, the quotation verse
    A(![...doc.querySelectorAll('#scroll .gatha')].some(g=>/bhāsitampetaṁ Bhagavatā–\s*$/.test(N(g.textContent))),
      'a prose unit\'s citation line is drawn as verse');
    A(![...doc.querySelectorAll('#scroll .gatha')].some(g=>/Sāmampi kho etaṁ Sīvaka/.test(g.textContent)),
      'an indented PROSE quotation is drawn as verse');
    // the orphan-section heads must not be drawn smaller than the sections
    // they head
    const nh=[...doc.querySelectorAll('#scroll .head')].find(h=>N(h.textContent)==='Nigamana');
    A(!!nh&&!nh.classList.contains('vatthu'),
      'a section head must not be drawn at vatthu weight');
  }

  // ---- 10. EVERY NAV ROW MUST OPEN SOMETHING ---------------------------
  // A row that opens nothing, or opens its parent's whole text, is a SPAN bug,
  // not a data bug.  Both shapes shipped once (27Khu10), and neither is
  // visible to any content gate.
  if(PART!=='data'){
    const w=boot(); if(!await ready(w)){console.log('nav never rendered (2)');process.exit(1);}
    for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(60);}}
    const b=find(w,'Milindapañhapāḷi'); b.click(); await wait(200);
    // expand every level of the tree
    let seen=new Set(), rows=[];
    for(let pass=0;pass<6;pass++){
      rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
      let grew=false;
      for(const r of rows){ const k=lbl(r); if(seen.has(k)) continue; seen.add(k); r.click(); await wait(5); grew=true; }
      if(!grew) break;
    }
    rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
    A(rows.length>=270,'every tree node should have a row; got '+rows.length);
    const empty=[]; const slice=rows.slice(R0,R1);
    for(const r of slice){
      r.click(); await wait(5);
      for(let k=0;k<40;k++){await wait(5);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      if(!w.document.querySelectorAll('#scroll .para.canon').length) empty.push(lbl(r));
    }
    A(empty.length===0, empty.length+' of '+slice.length+
      ' nav row(s) open nothing — '+JSON.stringify(empty.slice(0,8)));
    // a child must open ITS OWN slice, not its parent's
    const cnt=async(name)=>{
      const r=[...b.parentElement.querySelectorAll('.row')].find(x=>lbl(x)===name);
      if(!r) return -1;
      r.click(); await wait(20);
      for(let k=0;k<40;k++){await wait(10);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      return w.document.querySelectorAll('#scroll .para.canon').length;
    };
    if(R1<1e9&&R1<rows.length){ console.log(`\n[rows ${R0}-${Math.min(R1,rows.length)}] ${pass} passed, ${fail} failed`); process.exit(fail?1:0); }
    const kanda=await cnt('2. Milindapañha'), vagga=await cnt('1. Mahāvagga'),
          panha=await cnt('1. Paññattipañha');
    A(kanda>vagga&&vagga>panha&&panha>0,
      'each level must open a smaller slice than its parent: kaṇḍa '+kanda+
      ', vagga '+vagga+', pañha '+panha);
    A(vagga===16,'Mahāvagga should open its own 16 pañhas; got '+vagga);
  }

  console.log(`\n[${PART}] ${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

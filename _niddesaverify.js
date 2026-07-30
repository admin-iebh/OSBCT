// Mahāniddesa (24Khu07) + Cūḷaniddesa (25Khu08) — PRESENTATION assertions.
//
// Both volumes are 0/0/0/0 on the body harness and 0/0/2 and 0/0/0 on the
// apparatus one.  Neither of those can see whether a line is in the right ROLE,
// and this project has now shipped that defect five times at 0/0/0/0.  These
// volumes introduce a structure no other volume has — a numbered section whose
// content is PROSE COMMENTARY rather than verse — so every rule about how that
// is drawn is asserted here, in the same change that introduced it.
//
//   node _niddesaverify.js
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim().toLowerCase();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const rows=w=>[...w.document.querySelectorAll('.row')];
const find=(w,t)=>rows(w).find(r=>lbl(r)===t);
// A nav lookup by bare label must be scoped to its own subtree: labels such as
// "Pārāyanavagga" and "Paṭhamavagga" are not unique in the sidebar, and the
// whole tree is in the DOM at once.  This is the 22Khu05 lesson, and 25Khu08
// prints "Pārāyanavagga" TWICE at the same depth, so it matters here twice over.
const findIn=(el,t)=>[...el.querySelectorAll('.row')].find(r=>lbl(r)===t);
async function open(w,names){                      // click a path of labels
  let host=w.document; let r=null;
  for(const n of names){
    r=findIn(host,n); if(!r) return null;
    r.click(); await wait(140);
    host=r.parentElement;
  }
  for(let k=0;k<60;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
  return r;
}

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  const mn=kh.volumes.find(v=>v.vol==='24Khu07'), cn=kh.volumes.find(v=>v.vol==='25Khu08');

  // ---- 1. TREE SHAPE = the edition's own mātikā -------------------------
  A(!!mn&&!!mn.tree,'24Khu07 has no tree node');
  A(mn.tree.length===1&&mn.tree[0].label==='1. Aṭṭhakavagga',
    '24Khu07 top rows = '+JSON.stringify((mn.tree||[]).map(t=>t.label)));
  A(mn.tree[0].kids.length===16,'Aṭṭhakavagga sections = '+mn.tree[0].kids.length+', the mātikā lists 16');
  A(JSON.stringify(mn.tree[0].kids.map(k=>parseInt(k.label,10)))===JSON.stringify(Array.from({length:16},(_,i)=>i+1)),
    'the 16 suttaniddesas must be numbered 1-16 in order');
  A(cn.tree.length===2&&cn.tree.every(t=>t.label==='Pārāyanavagga'),
    '25Khu08 must print TWO rows both headed Pārāyanavagga, got '+JSON.stringify(cn.tree.map(t=>t.label)));
  A(cn.tree[0].kids.length===19&&cn.tree[1].kids.length===19,
    '25Khu08 section counts = '+JSON.stringify(cn.tree.map(t=>t.kids.length))+', the mātikā lists 19 + 19');
  // MIXED DEPTH IS THE EDITION'S: only the 19th section has vaggas.
  const withKids=cn.tree[1].kids.filter(k=>k.kids.length);
  A(withKids.length===1&&/Khaggavis/.test(withKids[0].label)&&withKids[0].kids.length===4,
    'only Khaggavisāṇasuttaniddesa may carry vaggas, and it has four; got '+
    JSON.stringify(withKids.map(k=>[k.label,k.kids.length])));
  A(JSON.stringify(withKids[0].kids.map(k=>k.label))===
    JSON.stringify(['Paṭhamavagga','Dutiyavagga','Tatiyavagga','Catutthavagga']),
    'Khaggavisāṇa vaggas = '+JSON.stringify(withKids[0].kids.map(k=>k.label)));
  // The first Pārāyanavagga row is the vagga's TEXT and must stop before the
  // niddesa begins; the reader bounds a node at its next sibling, so the two
  // keys are what enforce the standing book-boundary rule here.
  A(cn.tree[0].key==='25Khu08#0'&&cn.tree[1].key==='25Khu08#174',
    'Pārāyanavagga rows must start at #0 and #174, got '+cn.tree[0].key+' / '+cn.tree[1].key);

  // ---- 2. SIDE-MAP SHAPE: a section is a LEMMA plus PROSE ---------------
  for(const vol of ['24Khu07','25Khu08']){
    const V=JSON.parse(fs.readFileSync(R+'/verse/'+vol+'.json','utf8'));
    const nid=Object.values(V).filter(e=>Array.isArray(e.after)&&e.after.length);
    A(nid.length>150,vol+': only '+nid.length+' sections carry commentary');
    // Every commentary entry must be a LIST of printed paragraphs — one entry
    // per printed paragraph — and never a single run-on block, which is what
    // the corpus holds and what this rebuild exists to undo.
    const runon=nid.filter(e=>e.after.length===1&&typeof e.after[0]==='string'&&e.after[0].length>3000);
    A(runon.length===0,vol+': '+runon.length+' sections still render as one run-on block');
    // Gāthā quoted INSIDE the commentary must be {gatha:[…]} objects, not prose.
    const g=nid.reduce((n,e)=>n+e.after.filter(x=>x&&typeof x==='object'&&x.gatha).length,0);
    A(g>100,vol+': only '+g+' quoted gāthā blocks in the commentary');
    // The lemma itself is the entry's `groups`, so its number hangs beside the
    // first pāda rather than sitting on a line of its own (block() suppresses
    // the outer number whenever groups is non-empty).
    A(Object.values(V).every(e=>Array.isArray(e.groups)&&e.groups.length),
      vol+': some entries have no lemma verse in `groups`');
  }
  // The edition MISPRINTS the Khaggavisāṇa opening lemma as "211." where the
  // sequence requires 121.  It is preserved verbatim on both sides, and this
  // asserts that a later change cannot silently "correct" it.
  {
    const ps=JSON.parse(fs.readFileSync('site/25Khu08.json','utf8')).paragraphs;
    A(ps[294].n===211&&ps[293].n===120&&ps[295].n===122,
      "the edition's 211-for-121 misprint must survive: got "+
      [ps[293].n,ps[294].n,ps[295].n].join('/'));
    // The lemma text is stored WITHOUT its number (every volume does this — the
    // number is drawn from the corpus `n`), so what has to hold is that the
    // printed lemma whose number the edition sets as "211." is paired with the
    // ordinal that carries n=211.  Pairing by POSITION is what makes that true;
    // a number-keyed map would have put it somewhere else entirely.
    const V=JSON.parse(fs.readFileSync(R+'/verse/25Khu08.json','utf8'));
    A(/^Sabbesu bhūtesu nidhāya daṇḍaṁ/.test(V['294'].groups[0][0]),
      'ord294 must hold the Khaggavisāṇa opening lemma, got '+V['294'].groups[0][0].slice(0,30));
  }
  // 24Khu07's two back-matter word-index paragraphs must not render.
  {
    const H=JSON.parse(fs.readFileSync(R+'/hide/24Khu07.json','utf8'));
    A(H['210']&&H['211'],'24Khu07 ord210/211 (the printed word index) must be hidden');
  }

  // ---- 3. THE RENDER --------------------------------------------------
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  A(!err,'JS error on boot: '+err);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(80);}}

  const bookRow=find(w,'Mahāniddesapāḷi');
  A(!!bookRow,'no Mahāniddesapāḷi book row');
  bookRow.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
  let doc=w.document, scroll=doc.querySelector('#scroll');
  let txt=scroll.textContent;

  // the title page stack, then the homage, then the first heading — in that order
  const bt=doc.querySelector('#scroll .head.booktitle'), bs=doc.querySelector('#scroll .head.bookseries');
  A(!!bt&&N(bt.textContent)==='mahāniddesapāḷi','book title not drawn: '+(bt&&bt.textContent));
  A(!!bs&&N(bs.textContent)==='khuddakanikāya','series line not drawn: '+(bs&&bs.textContent));
  A(doc.querySelectorAll('#scroll .incipit').length===1,
    'exactly one homage: '+doc.querySelectorAll('#scroll .incipit').length);
  {
    const order=[...doc.querySelectorAll('#scroll .head.bookseries,#scroll .head.booktitle,#scroll .incipit')]
      .map(e=>e.classList.contains('incipit')?'incipit'
             :e.classList.contains('booktitle')?'booktitle':'bookseries');
    A(order[0]==='bookseries'&&order[1]==='booktitle'&&order[2]==='incipit',
      'printed order series -> title -> homage, got '+JSON.stringify(order));
  }
  // the homage must never also appear as body text
  A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>/amo tassa \S+ [Aa]rahato/.test(p.textContent)),
    'the homage is rendered as body text as well as as an incipit');

  // A NIDDESA SECTION IS DRAWN AS: heading -> lemma gāthā -> prose paragraphs,
  // with gāthā quoted inside the prose set as verse.  This is the whole point
  // of the rebuild and nothing else in the project asserts it.
  A(/1\.\s*Aṭṭhakavagga/.test(txt),'the vagga heading is not rendered');
  A(/1\.\s*Kāmasuttaniddesa/.test(txt),'the first suttaniddesa heading is not rendered');
  const g0=doc.querySelectorAll('#scroll .gatha').length;
  const p0=doc.querySelectorAll('#scroll .gatha-after').length;
  A(g0>0&&p0>0,'lemma/quoted gāthā = '+g0+', prose paragraphs = '+p0);
  A(p0>g0,'the Niddesa is mostly prose: prose paragraphs '+p0+' vs gāthā blocks '+g0);
  // the lemma's number hangs INSIDE the first .gatha, never on its own line
  A(doc.querySelectorAll('#scroll .gatha .pn').length>0,'no verse number hanging beside a lemma');
  // the quoted verse "Addasaṁ kāma te mūlaṁ…" is set as verse, not as prose
  A([...doc.querySelectorAll('#scroll .gatha')].some(e=>/Addasaṁ kāma te mūlaṁ/.test(e.textContent)),
    'the gāthā quoted inside the commentary is not drawn as verse');
  // a section-end colophon renders, and is not swallowed into the commentary
  A(/Kāmasuttaniddeso paṭhamo/.test(txt),'the section-end colophon is not rendered');
  // "Atha Guhaṭṭhakasuttaniddesaṁ vakkhati–" is printed BELOW its own heading
  {
    const i=txt.indexOf('2. Guhaṭṭhakasuttaniddesa'), j=txt.indexOf('Atha guhaṭṭhakasuttaniddesaṁ vakkhati');
    A(i>=0&&j>i,'the section opener must render below its heading, not above it (heading at '+i+', opener at '+j+')');
  }
  // the printed word index must be nowhere in the render
  A(!/Saṁvaṇṇitapadānaṁ anukkamaṇikā/.test(txt)&&!/Padānukkamo/.test(txt),
    "24Khu07's printed word index is being rendered as body text");
  A(/Mahāniddesapāḷi niṭṭhitā/.test(txt),'the book-end colophon is not rendered');

  // ---- 4. 25Khu08: the two Pārāyanavagga rows must not bleed ------------
  {
    const w2=boot(); if(!await ready(w2)){console.log('nav never rendered (2)');process.exit(1);}
    for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w2,t); if(r){r.click(); await wait(80);}}
    const bk=find(w2,'Cūḷaniddesapāḷi'); A(!!bk,'no Cūḷaniddesapāḷi book row');
    bk.click(); await wait(200);
    const host=bk.parentElement;
    const both=[...host.querySelectorAll('.row')].filter(r=>lbl(r)==='Pārāyanavagga');
    A(both.length===2,'two Pārāyanavagga rows in the sidebar, got '+both.length);
    both[0].click(); await wait(400);
    for(let k=0;k<60;k++){await wait(80);const s=w2.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
    const t1=w2.document.querySelector('#scroll').textContent;
    A(/Kosalānaṁ purā rammā/.test(t1),'the first row must open the Pārāyanavagga TEXT');
    // the standing book-boundary rule: it must stop before the niddesa
    A(!/Kenassu nivuto lokoti lokoti nirayaloko/.test(t1),
      'the Pārāyanavagga text row bleeds into the niddesa');
    // its two unnumbered sections are headings, not colophons
    A(/Pārāyanatthutigāthā/.test(t1)&&/Pārāyanānugītigāthā/.test(t1),
      "the two unnumbered sections are missing from the text row");
    both[1].click(); await wait(400);
    for(let k=0;k<60;k++){await wait(80);const s=w2.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
    const t2=w2.document.querySelector('#scroll').textContent;
    A(/1\.\s*Ajitamāṇavapucchāniddesa/.test(t2),'the second row must open the NIDDESA');
    A(!/Kosalānaṁ purā rammā/.test(t2),'the niddesa row bleeds back into the text');
    A(/Cūḷaniddesapāḷi niṭṭhitā/.test(t2),'the book-end colophon is not rendered');
    A(/Catuttho vaggo/.test(t2),"Khaggavisāṇa's fourth vagga colophon is not rendered");
    // the edition's 211-for-121 misprint must reach the PAGE, not just the data
    A(/211\.\s*Sabbesu bhūtesu nidhāya daṇḍaṁ/.test(t2.replace(/\s+/g,' ')),
      "the edition's misprinted \"211.\" must render on its own lemma");
  }

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

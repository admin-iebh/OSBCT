// Netti + Peṭakopadesa (27Khu10) — PRESENTATION assertions.
//
// Two books in one physical volume, so the STANDING BOUNDARY RULE is asserted
// here first: each must render its own text and stop at its own colophon.
// The volume also introduces a numbered unit that is SOMETIMES A GĀTHĀ and
// sometimes prose, interleaved in one series — a shape no other volume has —
// so how each is drawn is asserted too.
//
//   node --max-old-space-size=4096 _nettiverify.js
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
async function openBook(w,title){
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(80);}}
  const b=find(w,title); if(!b) return null;
  b.click(); await wait(250);
  for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>2000)break;}
  return w.document.querySelector('#scroll').textContent;
}

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/27Khu10.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/27Khu10.json','utf8'));
  const I=JSON.parse(fs.readFileSync(R+'/incipit/27Khu10.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  const nt=kh.volumes.find(v=>v.vol==='27Khu10'&&v.title==='Nettipāḷi');
  const pk=kh.volumes.find(v=>v.vol==='27Khu10'&&v.title==='Peṭakopadesapāḷi');

  // ---- 1. TWO BOOKS, each with EXACTLY ONE node -------------------------
  // USER-REPORTED: the sidebar showed Peṭakopadesapāḷi TWICE.  A physical
  // volume holding two books already has two nav nodes (build_khuddaka_nav.py
  // splits the 21 Khuddaka books across the 11 volumes), and the new builder
  // replaced only the FIRST, leaving the old node behind in its `nipata`/
  // `vaggas` shape.  Several volumes legitimately carry many nodes — 18Khu01
  // has five, one per book — so the invariant is not one node per VOLUME but
  // one per BOOK, and that is what is asserted.
  const all27=kh.volumes.filter(v=>v.vol==='27Khu10');
  A(all27.length===2,'27Khu10 must have exactly two nav nodes, one per book; got '+
    all27.length+' — '+JSON.stringify(all27.map(v=>v.title)));
  A(all27.every(v=>Array.isArray(v.tree)),
    'every 27Khu10 node must be the new `tree` shape; got '+
    JSON.stringify(all27.map(v=>Object.keys(v).filter(k=>['tree','nipata','vaggas','nipatas'].includes(k)))));
  A(new Set(all27.map(v=>v.title)).size===2,'the two nodes must not share a title');
  A(!!nt&&!!pk,'both books need their own nav node or BOOKSPAN cannot bound them');
  A(nt.first==='27Khu10#0'&&pk.first==='27Khu10#151',
    'book firsts = '+(nt&&nt.first)+' / '+(pk&&pk.first));
  A(Object.keys(I).length===2&&I['0']&&I['151'],
    'each book prints its own homage: '+JSON.stringify(Object.keys(I)));
  A(nt.tree.length===4&&JSON.stringify(nt.tree.map(t=>t.label))===JSON.stringify(
      ['1. Saṅgahavāra','2. Uddesavāra','3. Niddesavāra','4. Paṭiniddesavāra']),
    'Netti vāras = '+JSON.stringify(nt.tree.map(t=>t.label)));
  A(nt.tree[3].kids.length===34,
    'Paṭiniddesavāra sections = '+nt.tree[3].kids.length+' (16 vibhaṅga + 16 sampāta + 2)');
  A(pk.tree.length===8&&pk.tree.every(t=>t.kids.length===0),
    'Peṭakopadesa = 8 flat bhūmis, got '+pk.tree.length);
  // the edition's misprint survives on the page it is printed on
  A(!!nt.tree[3].kids.find(k=>k.label==='13. Sodhanahāravibhaṅga'),
    "the BODY's '13. Sodhanahāravibhaṅga' spelling must be what the tree shows");

  // ---- 2. UNITS: some are gāthā, some are prose -------------------------
  const ent=Object.values(V);
  A(ent.length===271,'271 units expected, got '+ent.length);
  const vs=ent.filter(e=>e.groups&&e.groups.length);
  const pr=ent.filter(e=>!e.groups||!e.groups.length);
  A(vs.length>0&&pr.length>0,
    'both shapes must occur: '+vs.length+' verse units, '+pr.length+' prose units');
  A(vs.every(e=>e.groups[0].length>=2),
    'a verse unit must hold its pādas, not just its first line');
  A(pr.every(e=>Array.isArray(e.after)&&e.after.length),
    'every prose unit must carry its printed paragraphs in `after`');
  const g=ent.reduce((n,e)=>n+(e.after||[]).filter(x=>x&&typeof x==='object'&&x.gatha).length,0);
  A(g>150,'quoted gāthā blocks inside the prose = '+g+' (the corpus dropped 409 printed lines)');

  // ---- 2a. !!! THE VERSE/PROSE CLASSIFICATION, corrected 2026-07-26w ----
  // This volume SHIPPED with 66 of its 271 units drawn as verse, and 46 of
  // those are prose: the catechetical question glued to the quoted gāthā's
  // first pāda, with the rest of the gāthā left as a separate block below it.
  // Its body gate was 0/0/0/0 throughout — every word present, contiguous and
  // unique — so nothing but an assertion about the ROLE can hold this.
  const FORMULA=/^(?:Tattha katam|Tatthimāni\b|Tatridaṁ\b|Manopubbaṅgamā dhammāti gāthā\.)/;
  A(vs.length===20,'exactly 20 units are genuine gāthā (was 66); got '+vs.length);
  A(!vs.some(e=>FORMULA.test(e.groups[0][0])),
    'no unit drawn as verse may open with the catechetical formula: '
    +JSON.stringify(vs.filter(e=>FORMULA.test(e.groups[0][0]))
                      .map(e=>e.groups[0][0]).slice(0,3)));
  // the 46 are prose and their question is the FIRST paragraph of `after`,
  // with the quotation that answers it as a gāthā block of its own
  const qs=pr.filter(e=>typeof e.after[0]==='string'&&FORMULA.test(e.after[0]));
  A(qs.length>=46,'the 46 reclassified questions must open their own `after`; got '+qs.length);
  // NO ONE-LINE GĀTHĀ.  A quotation's first line hangs LEFT of its pādas, and
  // if it is not joined to them it becomes either a one-line verse block or a
  // one-line prose paragraph above the rest of the gāthā.
  const all=[].concat(...ent.map(e=>(e.groups||[]).concat(
    (e.after||[]).filter(x=>x&&typeof x==='object'&&x.gatha).map(x=>x.gatha))));
  A(!all.some(b=>b.length<2),
    'no gāthā block may be a single line; got '+all.filter(b=>b.length<2).length);
  // AND THE EDITION'S OWN FRAME PROSE MUST NOT BE DRAWN AS VERSE.  It sets
  // "Tattha katamo assādo–" above each quotation and "Ayaṁ assādo." below it,
  // both centred; 23 such lines were inside gāthā blocks and 2 remain, both
  // recorded in HANDOFF.md — so this asserts the NUMBER, which is the only
  // honest form for a residue.
  const FRAME=/^(?:Idaṁ|Ayaṁ)\s+\S*(?:bhāgiyaṁ|adhiṭṭhāna\S*|assādo|ādīnavo|nissaraṇaṁ)/;
  const fr=all.reduce((n,b)=>n+b.filter(l=>FRAME.test(l)).length,0);
  A(fr===2,'frame lines still drawn as verse = '+fr+' (was 23; the 2 that remain '
    +'are named in HANDOFF.md — if this moves, read that entry)');
  // the book's opening section, printed BEFORE its first numbered unit
  A(Array.isArray(S['0'])&&S['0'].some(e=>e.l==='1. Saṅgahavāra')
    &&S['0'].some(e=>e.k==='gatha'&&/Yaṁ loko pūjayate/.test(e.l)),
    "the Saṅgahavāra's heading and gāthā must sit in sections[0], in printed order");
  A(S['0'].some(e=>e.k==='gatha'&&e.l==='Saṅgahavāro.'),
    'its closing colophon must keep its printed place and NOT be a heading class');

  // ---- 3. THE RENDER, and the standing boundary rule --------------------
  {
    const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const t=await openBook(w,'Nettipāḷi');
    A(!!t,'no Nettipāḷi book row');
    A(/Yaṁ loko pūjayate/.test(t),"the Saṅgahavāra's opening gāthā is not rendered");
    A(/1\.\s*Saṅgahavāra/.test(t)&&/4\.\s*Paṭiniddesavāra/.test(t),'vāra headings missing');
    A(/Saṅgahavāro\./.test(t),'the Saṅgahavāra colophon is not rendered');
    A(/Nettipakaraṇaṁ niṭṭhitaṁ/.test(t),'the Netti book-end colophon is not rendered');
    // STANDING RULE: it must stop at its own end
    A(!/Ariyasaccappakāsanapaṭhamabhūmi/.test(t)&&!/Peṭakopadesapakaraṇaṁ/.test(t),
      'the Netti bleeds into the Peṭakopadesa');
    const doc=w.document;
    A(doc.querySelectorAll('#scroll .incipit').length===1,'exactly one homage in the Netti');
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>/amo tassa \S+ [Aa]rahato/.test(p.textContent)),
      'the homage is rendered as body text as well as as an incipit');
    // a numbered unit that IS a gāthā hangs its number beside the first pāda
    const vp=[...doc.querySelectorAll('#scroll .para.canon')]
      .filter(p=>p.querySelector('.gatha')&&p.querySelector('.pn'));
    A(vp.some(p=>p.querySelector('.pn').closest('.gatha')),
      'no verse unit hangs its number inside its gāthā');
    // …and a prose unit opens its first paragraph with it, inline
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>{
        const f=p.querySelector('.pn');
        return f && !f.closest('.gatha') && !f.closest('.gatha-after');
      }),'some unit still stacks its number on a line of its own');
  }
  {
    const w=boot(); if(!await ready(w)){console.log('nav never rendered (2)');process.exit(1);}
    const t=await openBook(w,'Peṭakopadesapāḷi');
    A(!!t,'no Peṭakopadesapāḷi book row');
    A(/1\.\s*Ariyasaccappakāsanapaṭhamabhūmi/.test(t),'the first bhūmi heading is missing');
    A(/8\.\s*Suttavebhaṅgiya/.test(t),'the eighth bhūmi heading is missing');
    A(/Peṭakopadesapakaraṇaṁ niṭṭhitaṁ/.test(t),'the book-end colophon is not rendered');
    // STANDING RULE, the other way
    A(!/Yaṁ loko pūjayate/.test(t)&&!/Nettipakaraṇaṁ/.test(t),
      'the Peṭakopadesa bleeds back into the Netti');
    A(w.document.querySelectorAll('#scroll .incipit').length===1,
      'exactly one homage in the Peṭakopadesa');
  }

  // ---- 4. EVERY NAV ROW MUST OPEN SOMETHING, and only its own -----------
  // USER-REPORTED: clicking "1. Saṅgahavāra" or "2. Uddesavāra" showed nothing.
  // Two causes, both in the reader's span arithmetic and both invisible to
  // every content gate, since the text was present and correct in the data.
  //  (a) A node's span ended where the NEXT SIBLING starts, so a node whose
  //      neighbour shares its ordinal got a span of ZERO LENGTH.  The Netti's
  //      Saṅgahavāra has no numbered unit at all — its ten gāthā are display
  //      material on the Uddesavāra's first paragraph — so both sat at #0.
  //  (b) VAGGASPAN was keyed by the node's KEY, and a parent and its first
  //      child share one (Paṭiniddesavāra and Desanāhāravibhaṅga both at #30),
  //      so the child could not record its own span and opened all 121
  //      paragraphs of its parent.
  {
    const w=boot(); if(!await ready(w)){console.log('nav never rendered (3)');process.exit(1);}
    for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(80);}}
    for(const bk of ['Nettipāḷi','Peṭakopadesapāḷi']){
      const b=find(w,bk); b.click(); await wait(200);
      const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
      let empty=[];
      for(const r of rows){
        r.click(); await wait(150);
        for(let k=0;k<25;k++){await wait(60);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
        if(!w.document.querySelectorAll('#scroll .para.canon').length) empty.push(lbl(r));
      }
      A(empty.length===0, bk+': '+empty.length+' nav row(s) open nothing — '+JSON.stringify(empty.slice(0,6)));
    }
    // and a child must open ITS OWN slice, not its parent's
    const b=find(w,'Nettipāḷi'); b.click(); await wait(200);
    const cnt=async(name)=>{
      const r=[...b.parentElement.querySelectorAll('.row')].find(x=>lbl(x)===name);
      r.click(); await wait(200);
      for(let k=0;k<25;k++){await wait(60);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      return w.document.querySelectorAll('#scroll .para.canon').length;
    };
    const par=await cnt('4. Paṭiniddesavāra'), kid=await cnt('1. Desanāhāravibhaṅga');
    A(par>100&&kid<20&&kid<par,
      'Desanāhāravibhaṅga must open its own text, not its parent\'s: parent '+par+
      ' paragraphs, child '+kid);
  }

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

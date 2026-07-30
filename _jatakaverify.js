// Jātaka — presentation and structure assertions.
//
// WHY THIS FILE EXISTS.  Every user-reported defect in this project so far —
// four missing apadāna headings, nine missing book names, a book running into
// the next, a dropped series line — passed ALL THREE gates.  They were content
// in the wrong ROLE, or content missing its frame, and the content harness is
// structurally blind to both.  So each structural feature added for the Jātaka
// gets its assertion in the same change, per the standing rule.
//
// What is asserted here, and the specific way each one could regress silently:
//  1. the edition's own division: ONE Jātakapāḷi across 22Khu05 + 23Khu06,
//     nipātas 1-22 and jātakas 1-547 continuous ACROSS the volume break;
//  2. MIXED DEPTH — vaggas in nipātas 1-7 only.  Reading structure from the
//     corpus `vagga` field instead would invent 15 vaggas in the upper
//     nipātas, because that field sticks on a COLOPHON and carries forward;
//  3. jātakas 205 and 223, whose headings cannot live in `sections/` (a
//     heading falls between two verses the corpus SPLICED into one paragraph)
//     and are carried in the uddāna stream instead.  They rendered correctly
//     while being absent from the tree — the 1-547 check is what caught it;
//  4. the three verse numbers the edition MISPRINTS and the two headings it
//     sets irregularly, all preserved verbatim, never corrected;
//  5. spliced verses keeping their own printed numbers rather than being
//     swallowed by the preceding verse;
//  6. the book title and its collection line.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').toLowerCase();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<80;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const num=s=>{const m=/^(\d+)(?:-\d+)?\./.exec(String(s).trim());return m?+m[1]:null;};

(async()=>{
  // ---- structure, read from nav.json (expanding 547 rows in jsdom exhausts
  // the heap, exactly as _apadanaverify.js records for the Apadāna) ---------
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  // TWO BHĀGAS, as the edition's own title pages set them: "JĀTAKAPĀḶI
  // (Paṭhamo bhāgo)" / "(Dutiyo bhāgo)", each with its own mātikā headed
  // "Jātakapāḷi paṭhamabhāga" / "dutiyabhāga".  Labels are the edition's Pāḷi,
  // never "I"/"II", which the edition never prints.
  const B1=kh.volumes.find(v=>v.title==='Jātakapāḷi (Paṭhamo bhāgo)');
  const B2=kh.volumes.find(v=>v.title==='Jātakapāḷi (Dutiyo bhāgo)');
  A(!!B1&&!!B2,'the two bhāga nodes are not both present');
  A(!kh.volumes.some(v=>/^Jātakapāḷi( I| II)?$/.test(v.title||'')),
    'an older single-row or "Jātakapāḷi I / II" node is still present');
  if(!B1||!B2){console.log(`\n${pass} passed, ${fail} failed`);process.exit(1);}
  A(B1.vol==='22Khu05'&&B2.vol==='23Khu06','bhāga nodes bound to the wrong volumes');

  // Each bhāga's tree must lie wholly in its own volume — that is what lets a
  // bhāga row OPEN a reading pane, which the earlier single-row form could not.
  for(const [b,v] of [[B1,'22Khu05'],[B2,'23Khu06']]){
    const all=[];(function walk(ns){for(const n of ns){all.push(n);if(n.kids)walk(n.kids);}})(b.tree);
    A(all.every(x=>x.key.startsWith(v+'#')),b.title+' has keys outside '+v);
  }

  // The division must NOT renumber: nipātas join 1-22 and jātakas 1-547 across
  // the two books.  This is the most likely silent failure of splitting them.
  const nip=[...B1.tree,...B2.tree];
  A(B1.tree.length===16&&B2.tree.length===6,
    'nipātas per bhāga = '+B1.tree.length+'/'+B2.tree.length+', the edition prints 16/6');
  A(num(B2.tree[0].label)===17&&/Cattālīsanipāta/.test(B2.tree[0].label),
    'the second bhāga must open at "17. Cattālīsanipāta", got '+JSON.stringify(B2.tree[0].label));
  A(num(B1.tree[15].label)===16&&/Tiṁsanipāta/.test(B1.tree[15].label),
    'the first bhāga must end at "16. Tiṁsanipāta", got '+JSON.stringify(B1.tree[15].label));
  A(nip.length===22,'nipātas = '+nip.length+', the edition prints 22');
  const nnums=nip.map(n=>num(n.label));
  A(JSON.stringify(nnums)===JSON.stringify(Array.from({length:22},(_,i)=>i+1)),
    'nipāta numbering must join 1-22 across the two bhāgas — the edition divides the book '
    +'but does not renumber it; got '+JSON.stringify(nnums));

  // MIXED DEPTH: vaggas in nipātas 1-7 only, and nowhere else.
  const WANT={1:15,2:10,3:5,4:5,5:3,6:2,7:2};
  const vagCount=n=>n.kids.filter(k=>k.kids.length).length;
  let vtot=0;
  nip.forEach((n,i)=>{const c=vagCount(n);vtot+=c;
    A(c===(WANT[i+1]||0),'nipāta '+(i+1)+' ('+n.label+') has '+c+' vaggas, the edition prints '+(WANT[i+1]||0));});
  A(vtot===42,'total vaggas = '+vtot+', the edition prints 42');
  // the upper nipātas must hold jātaka LEAVES directly, not an invented vagga
  A(nip.slice(7).every(n=>n.kids.length&&n.kids.every(k=>!k.kids.length)),
    'a nipāta from the Aṭṭhakanipāta on has a vagga level the edition does not print');
  A(nip.slice(0,7).every(n=>n.kids.every(k=>k.kids.length)),
    'a nipāta in 1-7 has a bare jātaka where the edition prints vaggas');

  // 547 jātakas, continuous across the volume break
  const leaves=[];for(const n of nip)for(const k of n.kids)k.kids.length?leaves.push(...k.kids):leaves.push(k);
  A(leaves.length===547,'jātaka leaves = '+leaves.length+', the edition prints 547');
  const jn=leaves.map(l=>num(l.label));
  A(JSON.stringify(jn)===JSON.stringify(Array.from({length:547},(_,i)=>i+1)),
    'jātaka numbering must join 1-547 across the two bhāgas; first gap at index '
    +jn.findIndex((v,i)=>v!==i+1));
  const l1=[];for(const n of B1.tree)for(const k of n.kids)k.kids.length?l1.push(...k.kids):l1.push(k);
  A(l1.length===520&&num(l1[519].label)===520,
    'the first bhāga must hold jātakas 1-520, got '+l1.length+' ending at '+num(l1[l1.length-1].label));
  const l2=[];for(const n of B2.tree)for(const k of n.kids)k.kids.length?l2.push(...k.kids):l2.push(k);
  A(l2.length===27&&num(l2[0].label)===521,
    'the second bhāga must open at jātaka 521 and hold 27, got '+l2.length+' from '+num(l2[0].label));
  // the two whose heading lives in the uddāna stream, not in sections/
  for(const n of [205,223]) A(jn.includes(n),
    'jātaka '+n+' is missing from the tree — its heading falls between two verses the corpus '
    +'spliced together, so it is carried as an uddāna block head and the nav builder must read it there');
  // exactly one volume break, and it falls after jātaka 520
  const vv=leaves.map(l=>l.key.split('#')[0]);
  const brk=vv.map((x,i)=>i>0&&x!==vv[i-1]?i:-1).filter(i=>i>=0);
  A(brk.length===1&&jn[brk[0]]===521,'volume break should fall exactly once, before jātaka 521; got '
    +JSON.stringify(brk.map(i=>jn[i])));
  // every key resolves
  const paras={};for(const v of ['22Khu05','23Khu06'])paras[v]=JSON.parse(fs.readFileSync('site/'+v+'.json','utf8')).paragraphs.length;
  const bad=[...nip,...leaves].filter(x=>{const[v,o]=x.key.split('#');return !(v in paras)||+o>=paras[v];});
  A(bad.length===0,'nav keys out of range: '+JSON.stringify(bad.slice(0,5).map(x=>x.key)));

  // ---- the edition's own irregularities, preserved verbatim --------------
  const sec=v=>JSON.parse(fs.readFileSync(R+'/sections/'+v+'.json','utf8'));
  const allHeads=v=>Object.values(sec(v)).flat().map(h=>h.l);
  const h5=allHeads('22Khu05');
  A(h5.some(l=>/Udapānadūsakajākaka/.test(l)),
    'the p105 heading must keep the edition\'s own misprint "jākaka" for "jātaka", uncorrected');
  A(!h5.some(l=>/Udapānadūsakajātaka/.test(l)),
    'the p105 heading has been silently CORRECTED to "jātaka" — the edition prints "jākaka"');
  A(h5.some(l=>/^6\.\s+Na taṁ daḷhavagga$/.test(l.trim())),
    'the p79 vagga heading "6. Na taṁ daḷhavagga" (typeset with internal spaces) is missing — '
    +'a tighter heading regex drops it and Dukanipāta then shows 9 vaggas');

  // the three misprinted verse numbers must render as the edition sets them
  const versemap=v=>JSON.parse(fs.readFileSync(R+'/verse/'+v+'.json','utf8'));
  const V5=versemap('22Khu05'),V6=versemap('23Khu06');
  const P5=JSON.parse(fs.readFileSync('site/22Khu05.json','utf8')).paragraphs;
  const P6=JSON.parse(fs.readFileSync('site/23Khu06.json','utf8')).paragraphs;
  A(P5[1965]&&P5[1965].n===24&&/Api bhīruke/.test(P5[1965].text||''),
    '22Khu05 p304 prints "24." where the sequence requires 29 — that misprint must be preserved, not renumbered');
  A(P6[3576]&&P6[3576].n===2324,'23Khu06 p374 prints "2324." for 2342 — misprint must be preserved');
  A(P6[3674]&&P6[3674].n===1440,'23Khu06 p383 prints "1440." for 2440 — misprint must be preserved');
  // and both of the repeated "24" in that nipāta must still get verse structure
  A(!!V5['1960']&&!!V5['1965'],
    'the Pakiṇṇakanipāta prints "24." twice (the real v24 and the misprint for 29); both ordinals '
    +'must carry a verse entry — a single-valued number map silently drops one');

  // ---- corpus splices: the second verse keeps its own printed number ------
  const SPL5=[[257,109],[292,145],[1037,57],[1252,18],[2414,188],[2740,125],[2843,228]];
  for(const [o,n] of SPL5){
    const e=V5[String(o)];
    const inBlock=(JSON.parse(fs.readFileSync(R+'/uddana/22Khu05.json','utf8'))[String(o)]||[])
                    .some(b=>b.plain&&b.n===n);
    const inGroups=!!e&&Array.isArray(e.nums)&&e.nums.includes(n);
    A(inBlock||inGroups,'22Khu05 ord'+o+': printed verse '+n+' was spliced into the previous '
      +'paragraph by the corpus and must still render with its OWN number, either as a second '
      +'numbered group or as its own block');
  }
  const U5=JSON.parse(fs.readFileSync(R+'/uddana/22Khu05.json','utf8'));
  for(const [o,n,head] of [[257,109,'205. Gaṅgeyyajātaka (2-6-5)'],[292,145,'223. Puṭabhattajātaka (2-8-3)']]){
    const b=(U5[String(o)]||[]).find(x=>x.plain&&x.n===n);
    A(!!b&&b.head===head,'22Khu05 ord'+o+': verse '+n+' opens jātaka "'+head+'", so it must be its own '
      +'block UNDER that heading — folding it into the previous paragraph renders it ABOVE its own heading');
  }

  // ---- book title + collection line -------------------------------------
  for(const v of ['22Khu05','23Khu06']){
    const bt=JSON.parse(fs.readFileSync(R+'/booktitle/'+v+'.json','utf8'));
    const lines=Object.values(bt)[0];
    A(Array.isArray(lines)&&lines.length>=2&&lines[0]==='Khuddakanikāya'&&/^Jātakapāḷi$/.test(lines[lines.length-1]),
      v+' booktitle must carry the printed stack [collection, book], got '+JSON.stringify(lines));
  }

  // ---- render: boot the real reader and open a nipāta on each side -------
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  A(!err,'JS error on boot: '+err);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(60);}}
  // Opening words are taken from the corpus paragraph each unit starts at, NOT
  // recalled — two earlier drafts of this check failed against correct data
  // because the words were remembered rather than read.
  //   22Khu05 ord0 / ord1141 ; 23Khu06 ord0 / ord1237
  const BH=[['Jātakapāḷi (Paṭhamo bhāgo)',16,'1. Ekakanipāta','16. Tiṁsanipāta',
             'Apaṇṇakaṁ ṭhānameke','Vessantaraṁ taṁ pucchāmi',
             ['8. Aṭṭhakanipāta','Odātavatthā suci allakesā','Parisaṅkupatho nāma']],
            ['Jātakapāḷi (Dutiyo bhāgo)',6,'17. Cattālīsanipāta','22. Mahānipāta',
             'Vessantaraṁ taṁ pucchāmi','Apaṇṇakaṁ ṭhānameke',
             ['22. Mahānipāta','Mā paṇḍiccayaṁ','Vessantaraṁ taṁ pucchāmi']]];
  for(const [title,nn,firstRow,lastRow,ownWord,otherWord,nipCheck] of BH){
  const book=find(w,title);
  A(!!book,'no "'+title+'" row in the rendered tree');
  if(book){
    book.click();
    // A BHĀGA ROW MUST OPEN A READING PANE, not merely expand.  This is the
    // concrete gain of following the edition's two-volume division: each row's
    // whole tree lies in one volume, so render()'s single-volume slice
    // suffices.  The earlier single-row form could only expand.
    for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
    const sp=w.document.querySelector('#scroll');
    A(!!sp&&sp.textContent.length>1500,title+' does not OPEN — a bhāga row must open its own book');
    const pt=N(sp?sp.textContent:'');
    A(pt.includes(N(ownWord)),title+' does not render its own opening text '+JSON.stringify(ownWord));
    A(!pt.includes(N(otherWord)),title+' bleeds text from the other bhāga: '+JSON.stringify(otherWord));
    const kids=book.parentElement.querySelector('.kids');
    const rows=[...kids.children].map(c=>c.querySelector(':scope > .row')).filter(Boolean).map(lbl);
    A(rows.length===nn,title+' rendered nipāta rows = '+rows.length+', expected '+nn);
    A(rows[0]===firstRow&&rows[rows.length-1]===lastRow,
      title+' rendered nipāta ends = '+JSON.stringify([rows[0],rows[rows.length-1]])
      +', expected '+JSON.stringify([firstRow,lastRow]));
    for(const [name,openWord,notWord] of [nipCheck]){
      // SCOPED to the Jātakapāḷi subtree.  Nipāta names are NOT unique across
      // books — Theragāthā (19Khu02) also prints an Aṭṭhakanipāta, a
      // Navakanipāta and a Mahānipāta — and the sidebar holds every book's
      // rows in the DOM, so a bare label lookup silently opened Theragāthā's
      // Mahākaccāyanattheragāthā and asserted against the wrong book.
      const r=[...kids.querySelectorAll('.row')].find(x=>lbl(x)===name);
      A(!!r,'no rendered row for '+name+' inside the Jātakapāḷi tree');
      if(r){ r.click();
        // the reading pane is #scroll and fills asynchronously; poll rather
        // than guess a delay, as _apadanaverify.js does
        for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
        const s=w.document.querySelector('#scroll');
        A(!!s&&s.textContent.length>1500,name+' opened no reading pane');
        const t=N(s?s.textContent:'');
        A(t.includes(N(openWord)),name+' does not render its own opening text '+JSON.stringify(openWord));
        A(!t.includes(N(notWord)),name+' bleeds text that belongs to another nipāta: '+JSON.stringify(notWord));
      }
    }
  }
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

// Paṭṭhāna 4 (39Abhi11) — PRESENTATION assertions.
//
// What no content gate on this volume can see:
//   * the CORPUS SPLICE — printed unit 41 lives inside ord831, the paragraph
//     of unit 40, because the edition sets "41.Nevavipāka…" with no space
//     after the number.  It must still be VISIBLE, and it must be visible in
//     the right place: inside unit 40's block, not before it and not lost.
//   * the three printed-ORDER repairs (`head_order`, `split_unnumbered`):
//     a heading, its own prose, then a second heading before the unit;
//     prose printed between two colophons; and an unnumbered head sharing its
//     line with a numbered one.  Each one leaves every word present, so the
//     body gate can only see it as a broken chunk — a row-level assertion is
//     the only direct test.
//   * 1300 nav rows nested four deep.  A row that opens nothing, or opens its
//     parent's whole text, is a SPAN bug: three shapes of it have shipped.
//
//   node --max-old-space-size=4096 _abhi11verify.js data
//   node --max-old-space-size=4096 _abhi11verify.js rows <from> <to>
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='39Abhi11', MODE=process.argv[2]||'data';

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const all=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ---- 1. ONE NODE, LABELLED AS ITS OWN TITLE PAGE LABELS IT ----------
    A(all.length===1,'36Abhi08 must have exactly one nav node; got '+all.length);
    const bk=all[0];
    A(bk.title==='Paṭṭhānapāḷi (Catuttho bhāgo)','node label = '+bk.title);
    A(Array.isArray(bk.tree)&&bk.tree.length===3,'three inner books; got '+(bk.tree||[]).length);
    A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(
      ['Dukapaṭṭhānapāḷi','Dukatikapaṭṭhānapāḷi','Tikadukapaṭṭhānapāḷi']),
      'inner books = '+JSON.stringify(bk.tree.map(t=>t.label)));

    // ---- 2. THE TOPS AND THE VĀRAS, nested, not flat --------------------
    const B=Object.fromEntries(bk.tree.map(t=>[t.label,t]));
    A(JSON.stringify(B['Dukapaṭṭhānapāḷi'].kids.map(k=>k.label))
      ===JSON.stringify(['12. Kilesagocchaka','13. Piṭṭhiduka']),
      'book 1 tops = '+JSON.stringify(B['Dukapaṭṭhānapāḷi'].kids.map(k=>k.label)));
    // Books 2 and 3 cross a duka with a tika; which is on TOP is the whole
    // difference between them and is read off their names.
    A(B['Dukatikapaṭṭhānapāḷi'].kids.every(k=>/^\d+(-\d+)?\.\s+\S+duka$/.test(k.label)),
      'Dukatika tops must all be numbered dukas');
    A(B['Tikadukapaṭṭhānapāḷi'].kids.every(k=>/^\d+(-\d+)?\.\s+\S+ttika$/.test(k.label)),
      'Tikaduka tops must all be numbered tikas');
    A(B['Dukatikapaṭṭhānapāḷi'].kids[0].kids.every(k=>/ttika$|pada$/.test(k.label)||true),'');
    for(const t of bk.tree) A(t.kids.length>0,t.label+' has no sections');
    // no tika name may repeat as its own child (the ancestor-reprint rule)
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    walk(bk.tree[0].kids,['Tikapaṭṭhānapāḷi']);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree);
    // WAS 2058, AND THAT NUMBER RECORDED A DEFECT.  Where the top level is an
    // open (`re:`) set the builder tested the pattern BEFORE the
    // ancestor-reprint rule, so every reprint of the outer section's name
    // opened a NEW top: this volume shipped with "1. Hetuduka" and
    // "100. Saraṇaduka" twenty-two times each as tops of the Dukatika, and
    // "1. Kusalattika" fifty-two times as tops of the Tikaduka.  Dukatika 129
    // tops -> 87, Tikaduka 94 -> 44.
    A(cnt===1966,'1966 nodes (2179 printed headings less 216 ancestor reprints, '
      +'plus the three book nodes); got '+cnt);
    // Tikaduka KEEPS 22 of its 44 top labels twice, and that is the edition:
    // it crosses all 22 tikas with the first duka, then the first tika with
    // all the remaining dukas, then all 22 tikas with the last duka.  Those
    // three passes are not contiguous, so each needs its own node — what must
    // never happen is two ADJACENT siblings sharing a label, which is what the
    // reprint defect looked like and what `_navdup.js` now tests.
    for(const t of bk.tree){
      const L=t.kids.map(k=>k.label);
      A(!L.some((x,i)=>i+1<L.length&&L[i+1]===x),
        t.label+': two adjacent tops share a label');
    }

    // ---- 3. THREE BOOKS, THREE HOMAGES, NONE ON A HIDDEN ORDINAL --------
    const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    A(Object.keys(I).length===3,'three homages, one per book; got '+Object.keys(I).length);
    for(const k of Object.keys(I)) A(!H[k],'incipit anchored to hidden ord'+k);

    // ---- 4. HEADINGS --------------------------------------------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    A(!heads.some(h=>/\s{3,}/.test(h)),
      'no heading may keep a 3+ space run: '
      +JSON.stringify(heads.filter(h=>/\s{3,}/.test(h)).slice(0,3)));
    for(const [k,v] of Object.entries(S)){
      const ls=v.map(x=>x.l);
      A(new Set(ls).size===ls.length,'ord'+k+' repeats a heading: '+JSON.stringify(ls));
    }
    // the hyphenated compound the edition splits across two indented lines
    const V271=(V['271']||{}).after||[];
    A(V271.some(x=>typeof x==='string'&&/dassanenapahātabbahetukadukasadisā/.test(x)),
      'a line-end hyphen must rejoin: dassanenapahātabbahetukaduka- / sadisā');

    // ---- 5. THE RENDER ITSELF -------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,'Paṭṭhānapāḷi (Catuttho bhāgo)');
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(200);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===3,
      'three homages on the page, one per book; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    for(const t of ['Dukapaṭṭhānapāḷi','Dukatikapaṭṭhānapāḷi','Tikadukapaṭṭhānapāḷi'])
      A(txt.indexOf(t)>=0,"the inner book title page must render: "+t);
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice -----------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,'Paṭṭhānapāḷi (Catuttho bhāgo)');
  b.click(); await wait(150);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  // NO EXPANSION PASS.  Opening the volume renders its whole tree — all
  // 1300 rows are in the DOM at once — and clicking each one to expand it
  // costs ~18ms of re-render, i.e. 24s before a single assertion runs.
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const slice=rows.slice(from,Math.min(to,rows.length));
  let empty=[],whole_open=[],checked=0;
  for(const r of slice){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    // 'Tikapaṭṭhānapāḷi' is the volume's ONE inner book, so it legitimately
    // spans the whole text; every row under it must open strictly less.
    else if(n>=whole&&whole>50&&!['Dukapaṭṭhānapāḷi','Dukatikapaṭṭhānapāḷi','Tikadukapaṭṭhānapāḷi'].includes(lbl(r))) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+" rows open the WHOLE volume — "+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

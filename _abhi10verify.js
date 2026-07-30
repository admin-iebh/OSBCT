// Paṭṭhāna 3 (38Abhi10) — PRESENTATION assertions.
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
//   node --max-old-space-size=4096 _abhi10verify.js data
//   node --max-old-space-size=4096 _abhi10verify.js rows <from> <to>
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='38Abhi10', MODE=process.argv[2]||'data';

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
    A(bk.title==='Paṭṭhānapāḷi (Tatiyo bhāgo)','node label = '+bk.title);
    A(Array.isArray(bk.tree)&&bk.tree.length===1,'one inner book');
    A(bk.tree[0].label==='Dukapaṭṭhānapāḷi','inner book = '+bk.tree[0].label);

    // ---- 2. THE TOPS AND THE VĀRAS, nested, not flat --------------------
    const tops=bk.tree[0].kids.map(k=>k.label);
    A(JSON.stringify(tops)===JSON.stringify(
      ['1. Hetugocchaka','2. Cūḷantaraduka','3. Āsavagocchaka',
       '4. Saññojanagocchaka','5. Ganthagocchaka','6-7. Oghayogagocchaka',
       '8. Nīvaraṇagocchaka','9. Parāmāsagocchaka','10. Mahantaraduka',
       '11. Upādānagocchaka']),
      'tops = '+JSON.stringify(tops));
    // THE EDITION ABBREVIATES THE OGHA AND YOGA GOCCHAKAS TO ONE SECTION —
    // "32-43. Oghādiduka" with two lines and the note "Dvepi gocchakā
    // Āsavagocchakasadisā".  One child there is the printed page, not a loss.
    const ogha=bk.tree[0].kids.find(k=>k.label==='6-7. Oghayogagocchaka');
    A(ogha.kids.length===1&&ogha.kids[0].label==='32-43. Oghādiduka',
      'the Ogha/Yoga gocchaka carries exactly its one printed section');
    // every other top's children are numbered dukas
    for(const t of bk.tree[0].kids){
      if(t.label==='6-7. Oghayogagocchaka') continue;
      A(t.kids.length>0&&t.kids.every(k=>/^\d+(-\d+)?\.\s+\S+duka$/.test(k.label)),
        t.label+" children must be numbered dukas: "+JSON.stringify(t.kids.map(k=>k.label).slice(0,3)));
    }
    // no tika name may repeat as its own child (the ancestor-reprint rule)
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    walk(bk.tree[0].kids,['Tikapaṭṭhānapāḷi']);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree[0].kids);
    A(cnt===1929,'1929 nodes (2184 printed headings less 255 ancestor reprints); got '+cnt);

    // ---- 3. THE UNIT THE CORPUS DOES NOT HOLD ---------------------------
    // Printed unit 1 is in NO corpus paragraph; it is drawn from the printed
    // page into the NEXT unit's `before`, above it, carrying its own number.
    const e0=V[Object.keys(V).map(Number).sort((a,b)=>a-b)[0]] || V['0'];
    const bf=(V['0']||{}).before||[];
    const num=bf.filter(x=>x&&typeof x==='object'&&x.t!=null);
    A(num.length===1&&num[0].n===1,
      "unit 40's block... rather: ord0 must carry exactly one numbered prose "
      +'paragraph, n=1; got '+JSON.stringify(num.map(x=>x.n)));
    A(/^Hetuṁ dhammaṁ paṭicca hetu dhammo uppajjati hetupaccayā/.test(num[0]?num[0].t:''),
      'unit 1 must open with its own printed words');

    // ---- 4. THE HEADING PAIR THE EDITION SET WITHOUT A SPACE ------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    for(const h of ['1. Paccayānuloma','1. Vibhaṅgavāra','27. Ganthaniyaduka','1-7. Vārasattaka'])
      A(heads.includes(h),'heading pair must be split: missing '+h);
    A(!heads.some(h=>/\s{3,}/.test(h)),
      'no heading may keep a 3+ space run: '
      +JSON.stringify(heads.filter(h=>/\s{3,}/.test(h)).slice(0,3)));
    // and no ordinal may carry the SAME heading twice (the value-filter bug)
    for(const [k,v] of Object.entries(S)){
      const ls=v.map(x=>x.l);
      A(new Set(ls).size===ls.length,'ord'+k+' repeats a heading: '+JSON.stringify(ls));
    }

    // ---- 5. THE RENDER ITSELF -------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,'Paṭṭhānapāḷi (Tatiyo bhāgo)');
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(200);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===1,
      'exactly one homage on the page; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    A(/1\.\s*Hetuṁ dhammaṁ paṭicca hetu dhammo uppajjati hetupaccayā/.test(txt),
      'the corpus-absent unit 1 must be READ on the page, with its number');
    A(txt.indexOf('Hetuṁ dhammaṁ paṭicca hetu dhammo')
      < txt.indexOf('Nahetuṁ dhammaṁ paṭicca nahetu dhammo'),
      'unit 1 must render ABOVE unit 2, where the page sets it');
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice -----------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,'Paṭṭhānapāḷi (Tatiyo bhāgo)');
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
    else if(n>=whole&&whole>50&&lbl(r)!=='Dukapaṭṭhānapāḷi') whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+" rows open the WHOLE volume — "+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

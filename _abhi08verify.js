// Paṭṭhāna 1 (36Abhi08) — PRESENTATION assertions.
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
//   node --max-old-space-size=4096 _abhi08verify.js data
//   node --max-old-space-size=4096 _abhi08verify.js rows <from> <to>
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='36Abhi08', MODE=process.argv[2]||'data';

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
    A(bk.title==='Paṭṭhānapāḷi (Paṭhamo bhāgo)','node label = '+bk.title);
    A(Array.isArray(bk.tree)&&bk.tree.length===1,'one inner book');
    A(bk.tree[0].label==='Tikapaṭṭhānapāḷi','inner book = '+bk.tree[0].label);

    // ---- 2. THE TOPS AND THE VĀRAS, nested, not flat --------------------
    const tops=bk.tree[0].kids.map(k=>k.label);
    A(JSON.stringify(tops)===JSON.stringify(
      ['1. Paccayuddesa','2. Paccayaniddesa','Pucchāvāra','1. Kusalattika',
       '2. Vedanāttika','3. Vipākattika','4. Upādinnattika','5. Saṁkiliṭṭhattika']),
      'tops = '+JSON.stringify(tops));
    const VARA=['1. Paṭiccavāra','2. Sahajātavāra','3. Paccayavāra','4. Nissayavāra',
                '5. Saṁsaṭṭhavāra','6. Sampayuttavāra','7. Pañhāvāra'];
    for(const t of ['1. Kusalattika','2. Vedanāttika','3. Vipākattika','4. Upādinnattika']){
      const n=bk.tree[0].kids.find(k=>k.label===t);
      A(JSON.stringify(n.kids.map(k=>k.label))===JSON.stringify(VARA),
        t+' must carry the seven vāras: '+JSON.stringify(n.kids.map(k=>k.label)));
    }
    // no tika name may repeat as its own child (the ancestor-reprint rule)
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    walk(bk.tree[0].kids,['Tikapaṭṭhānapāḷi']);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree[0].kids);
    A(cnt===1300,'1300 nodes (1351 printed headings less 51 ancestor reprints); got '+cnt);

    // ---- 3. THE CORPUS SPLICE MUST BE VISIBLE, AND INSIDE UNIT 40 -------
    const e=V['831'];
    A(!!e,'ord831 must carry a verse-map entry');
    const num=(e.after||[]).filter(x=>x&&typeof x==='object'&&x.t!=null);
    A(num.length===1&&num[0].n===41,
      'unit 40 must carry exactly one numbered prose paragraph, n=41; got '
      +JSON.stringify(num.map(x=>x.n)));
    A(/^Nevavipākanavipākadhammadhammaṁ paṭicca/.test(num[0]?num[0].t:''),
      "unit 41 must open with its own printed words: "+(num[0]?num[0].t.slice(0,40):''));
    A((e.after||[]).indexOf(num[0])===3,
      'unit 41 must sit where the page sets it — after unit 40\'s three '
      +'sub-blocks; index '+(e.after||[]).indexOf(num[0]));

    // ---- 4. THE TWO-COLUMN HEADING, SPLIT --------------------------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    for(const h of ['Pucchāvāra','1. Paccayānuloma','Ekamūlaka','1. Kusalapada'])
      A(heads.includes(h),'the two-column heading must be split: missing '+h);
    A(!heads.some(h=>/\s{3,}/.test(h)),
      'no heading may keep a 3+ space run: '+JSON.stringify(heads.filter(h=>/\s{3,}/.test(h)).slice(0,3)));

    // ---- 5. THE RENDER ITSELF -------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,'Paṭṭhānapāḷi (Paṭhamo bhāgo)');
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(200);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A(/41\.\s*Nevavipākanavipākadhammadhammaṁ paṭicca/.test(txt),
      'unit 41 must be READ on the page with its number, not only present in '
      +'the map');
    // the prose printed between two colophons must follow the first one
    const i1=txt.indexOf('Nissayavāre paccanīyānulomaṁ.');
    const i2=txt.indexOf('Paccayattaṁ nāma nissayattaṁ');
    const i3=txt.indexOf('Nissayavāro.');
    A(i1>0&&i2>i1&&i3>i2,
      'printed order colophon/prose/colophon: '+i1+' '+i2+' '+i3);
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice -----------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,'Paṭṭhānapāḷi (Paṭhamo bhāgo)');
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
    else if(n>=whole&&whole>50&&lbl(r)!=='Tikapaṭṭhānapāḷi') whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+" rows open the WHOLE volume — "+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

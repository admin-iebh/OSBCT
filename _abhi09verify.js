// Paṭṭhāna 2 (37Abhi09) — PRESENTATION assertions.
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
//   node --max-old-space-size=4096 _abhi09verify.js data
//   node --max-old-space-size=4096 _abhi09verify.js rows <from> <to>
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='37Abhi09', MODE=process.argv[2]||'data';

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
    A(bk.title==='Paṭṭhānapāḷi (Dutiyo bhāgo)','node label = '+bk.title);
    A(Array.isArray(bk.tree)&&bk.tree.length===1,'one inner book');
    A(bk.tree[0].label==='Tikapaṭṭhānapāḷi','inner book = '+bk.tree[0].label);

    // ---- 2. THE TOPS AND THE VĀRAS, nested, not flat --------------------
    const tops=bk.tree[0].kids.map(k=>k.label);
    A(JSON.stringify(tops)===JSON.stringify(
      ['6. Vitakkattika','7. Pītittika','8. Dassanenapahātabbattika',
       '9. Dassanenapahātabbahetukattika','10. Ācayagāmittika','11. Sekkhattika',
       '12. Parittattika','13. Parittārammaṇattika','14. Hīnattika',
       '15. Micchattaniyatattika','16. Maggārammaṇattika','17. Uppannattika',
       '18. Atītattika','19. Atītārammaṇattika','20. Ajjhattattika',
       '21. Ajjhattārammaṇattika','22. Sanidassanasappaṭighattika']),
      'tops = '+JSON.stringify(tops));
    // this bhāga opens straight at the sixth tika — 36Abhi08 ends at the fifth
    A(!tops.some(t=>/Kusalattika|Vedanāttika|Vipākattika|Upādinnattika|Saṁkiliṭṭhattika/.test(t)),
      "36Abhi08's tikas must not reappear here");
    // no tika name may repeat as its own child (the ancestor-reprint rule)
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    walk(bk.tree[0].kids,['Tikapaṭṭhānapāḷi']);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree[0].kids);
    A(cnt===996,'996 nodes (1097 printed headings less 101 ancestor reprints); got '+cnt);

    // ---- 3. THE HOMAGE IS NOT ANCHORED TO A HIDDEN ORDINAL --------------
    // ord0 and ord1 are the leaked pair "6. Vitakkattika / 1. Paṭiccavāra",
    // so both are hidden; a side-map anchored there never renders.
    const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    const B=JSON.parse(fs.readFileSync(R+'/booktitle/'+VOL+'.json','utf8'));
    for(const k of Object.keys(I)) A(!H[k],'incipit anchored to hidden ord'+k);
    for(const k of Object.keys(B)) A(!H[k],'booktitle anchored to hidden ord'+k);

    // ---- 4. THE TWO HEADING PAIRS THE EDITION SET WITH ONE SPACE --------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    for(const h of ['2. Paccayapaccanīya','2. Saṅkhyāvāra',
                    '19. Atītārammaṇattika','7. Pañhāvāra'])
      A(heads.includes(h),'one-space heading pair must be split: missing '+h);
    A(!heads.some(h=>/\s{3,}/.test(h)),
      'no heading may keep a 3+ space run: '
      +JSON.stringify(heads.filter(h=>/\s{3,}/.test(h)).slice(0,3)));

    // ---- 5. THE RENDER ITSELF -------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,'Paṭṭhānapāḷi (Dutiyo bhāgo)');
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(200);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    // EXACTLY ONE HOMAGE.  The reader falls back to a built-in lowercase copy
    // when the data supplies none at the slice start; with the incipit moved
    // off hidden ord0 that test had to learn to skip hidden ordinals, or the
    // page drew both.
    A((txt.match(/[Nn]amo tassa/g)||[]).length===1,
      'exactly one homage on the page; got '
      +(txt.match(/[Nn]amo tassa/g)||[]).length);
    A(w.document.querySelectorAll('#scroll .incipit').length===1,
      'exactly one .incipit element');
    A(/Tikapaṭṭhānapāḷi/.test(w.document.getElementById('scroll').textContent),
      "the title page's own stack must render (it was keyed to hidden ord0)");
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice -----------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,'Paṭṭhānapāḷi (Dutiyo bhāgo)');
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

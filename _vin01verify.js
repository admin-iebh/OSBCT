// 01Vin01 (Pārājikapāḷi) — NAV assertions and the row sweep.
//
// The Vinaya navs carried the old font-heuristic tree from build_nav.py and
// had never been checked against a mātikā or a colophon.  What no content gate
// on this volume can see, and what this file is for:
//
//   * a heading that is in the body and NOT in the tree.  01Vin01 prints
//     'Idaṁ sabbamūlakaṁ' four times and 'Idaṁ dasamūlakaṁ' eight; declared as
//     a `levels` entry each repeat is read as an ANCESTOR REPRINT and eleven of
//     the twelve rows disappear, with every word of the text still in place.
//   * a row that opens nothing, or opens its parent's whole text — a SPAN bug.
//     Three shapes of that have shipped.
//   * the tree's SHAPE.  The old tree merged '1. Paṭhamapārājika' with
//     'Sudinnabhāṇavāra' onto one row, invented labels the edition does not
//     print ('Vinītavatthu (1)'), and keyed four rows to the wrong ordinal.
//
//   node --max-old-space-size=4096 _vin01verify.js data
//   node --max-old-space-size=4096 _vin01verify.js rows [from] [to]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='01Vin01', LABEL='Pārājikapāḷi', MODE=process.argv[2]||'data';

const TOPS=['Verañjakaṇḍa','1. Pārājikakaṇḍa','2. Saṁghādisesakaṇḍa',
            '3. Aniyatakaṇḍa','4. Nissaggiyakaṇḍa'];
const PARAJIKA=/^\d+\.\s+\S*pārājika$/;
const SIKKHA=/^\d+\.\s+\S*sikkhāpada$/;
const VAGGA=/^\d+\.\s+\S*vagga$/;

// EVERY PRINTED HEADING, from the same two side-maps the builder reads.
function printedHeads(){
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const ks=[...new Set([...Object.keys(S),...Object.keys(U)])].sort((a,b)=>a-b);
  const out=[];
  for(const k of ks){
    for(const e of (S[k]||[])) if(e.k!=='gatha'&&e.k!=='booktitle') out.push([e.l,+k]);
    for(const b of (U[k]||[])) if(b.head) out.push([b.head,+k]);
  }
  return out;
}

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const vin=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Vinayapiṭaka');
  const all=vin.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ---- 1. ONE NODE, ONE BOOK ------------------------------------------
    A(all.length===1,VOL+' must have exactly one nav node; got '+all.length);
    const bk=all[0];
    A(bk.title===LABEL,'node label = '+bk.title);
    A(bk.first===VOL+'#0','node opens at ord0; got '+bk.first);
    A(!bk.suttas&&!bk.pdftoc,'the old font-heuristic keys must be gone');
    A(Array.isArray(bk.tree),'the node must carry a tree');

    // ---- 2. THE FIVE KAṆḌAS, IN THE EDITION'S ORDER ----------------------
    A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(TOPS),
      'tops = '+JSON.stringify(bk.tree.map(t=>t.label)));
    const top=Object.fromEntries(bk.tree.map(t=>[t.label,t]));

    // ---- 3. THE COUNTS THE EDITION ITSELF STATES -------------------------
    // four pārājikas, thirteen saṁghādisesas, two aniyatas, thirty
    // nissaggiyas in three vaggas of ten — the Pātimokkha's own numbers.
    const par=top['1. Pārājikakaṇḍa'].kids;
    A(par.length===4,'four pārājikas; got '+par.length);
    A(par.every(k=>PARAJIKA.test(k.label)),'every child of the Pārājikakaṇḍa is a pārājika');
    const sg=top['2. Saṁghādisesakaṇḍa'].kids;
    A(sg.length===13,'thirteen saṁghādisesa sikkhāpadas; got '+sg.length);
    A(sg.every(k=>SIKKHA.test(k.label)),'every child of the Saṁghādisesakaṇḍa is a sikkhāpada');
    const an=top['3. Aniyatakaṇḍa'].kids;
    A(an.length===2,'two aniyatas; got '+an.length);
    const ni=top['4. Nissaggiyakaṇḍa'].kids;
    A(ni.length===3,'three nissaggiya vaggas; got '+ni.length);
    A(ni.every(k=>VAGGA.test(k.label)),'every child of the Nissaggiyakaṇḍa is a vagga');
    A(ni.every(k=>k.kids.length===10),'ten sikkhāpadas per vagga; got '
      +JSON.stringify(ni.map(k=>k.kids.length)));
    A(ni.every(k=>k.kids.every(x=>SIKKHA.test(x.label))),
      'every child of a nissaggiya vagga is a sikkhāpada');
    // and the numbering inside each vagga runs 1..10 as printed
    for(const v of ni)
      A(JSON.stringify(v.kids.map(k=>+k.label.split('.')[0]))
        ===JSON.stringify([1,2,3,4,5,6,7,8,9,10]),
        v.label+' numbers its sikkhāpadas '+JSON.stringify(v.kids.map(k=>k.label.split('.')[0])));

    // ---- 4. EVERY PRINTED HEADING IS IN THE TREE, ONCE -------------------
    // The one thing that separates a right tree from a plausible one.  The
    // heads stream minus the edition's ANCESTOR REPRINTS (the vagga name
    // reprinted over each of its ten sikkhāpadas, 27 of them) must equal the
    // tree's rows exactly, label AND ordinal.
    const heads=printedHeads();
    A(heads.length===117,'117 printed headings; got '+heads.length);
    const flat=[]; (function walk(ns){for(const n of ns){flat.push([n.label,+n.key.split('#')[1]]);walk(n.kids||[]);}})(bk.tree);
    A(flat.length===90,'90 tree rows; got '+flat.length);
    const key=x=>x[0]+'#'+x[1];
    const seen=new Set(), reprints=[], want=[];
    const stack=[];
    for(const [l,o] of heads){
      // a reprint is a label already open above it in the printed hierarchy
      if(stack.includes(l)){reprints.push(l);continue;}
      want.push([l,o]);
      // ONLY A STRUCTURAL HEADING OPENS A LEVEL.  A vatthu, a bhāṇavāra or an
      // 'Idaṁ …mūlakaṁ' is a LEAF: it never becomes an ancestor, which is
      // exactly why the edition may print it twice in a row and both rows must
      // stand.  (Modelled the other way round, this check "found" 36 reprints
      // and called nine printed headings duplicates.)
      const d=TOPS.includes(l)?0:(PARAJIKA.test(l)||VAGGA.test(l))?1:SIKKHA.test(l)?2:null;
      if(d===null) continue;
      stack.length=Math.min(d,stack.length); stack.push(l);
    }
    A(reprints.length===27,'27 ancestor reprints skipped; got '+reprints.length);
    A(JSON.stringify(want.map(key))===JSON.stringify(flat.map(key)),
      'the tree must be exactly the printed heads minus the reprints; first '
      +'difference at '+(want.map(key).findIndex((x,i)=>x!==flat.map(key)[i])));

    // ---- 5. THE EDITION'S OWN ADJACENT REPEATS, KEPT ---------------------
    const lab=flat.map(x=>x[0]);
    A(lab.filter(x=>x==='Idaṁ sabbamūlakaṁ').length===4,
      'four printed "Idaṁ sabbamūlakaṁ" rows; got '+lab.filter(x=>x==='Idaṁ sabbamūlakaṁ').length);
    A(lab.filter(x=>x==='Idaṁ dasamūlakaṁ').length===8,
      'eight printed "Idaṁ dasamūlakaṁ" rows; got '+lab.filter(x=>x==='Idaṁ dasamūlakaṁ').length);

    // ---- 6. ORDINALS RUN FORWARD IN PRE-ORDER ---------------------------
    let prev=-1,back=[];
    for(const [l,o] of flat){ if(o<prev) back.push(l+'@'+o); prev=o; }
    A(back.length===0,'ordinals must not run backwards: '+JSON.stringify(back.slice(0,5)));
    const npara=JSON.parse(fs.readFileSync('site/'+VOL+'.json','utf8')).paragraphs.length;
    A(flat.every(([l,o])=>o>=0&&o<npara),'every key inside 0..'+npara);

    // ---- 7. THE RENDER --------------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Vinayapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL);
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===1,
      'one homage; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    A(txt.includes('Verañjakaṇḍa'),'the first kaṇḍa must render');
    A(txt.includes('Pārājikapāḷi niṭṭhitā'),
      "the volume's closing colophon must render");
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice ------------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Vinayapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,LABEL);
  b.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const slice=rows.slice(from,Math.min(to,rows.length));
  let empty=[],whole_open=[],checked=0;
  for(const r of slice){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    else if(n>=whole&&whole>50) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open the WHOLE volume — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

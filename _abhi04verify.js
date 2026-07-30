// Kathāvatthu (32Abhi04) — NAV row sweep + the assertions the mātikā check
// cannot make.  A row that opens nothing, or opens the whole book, is a SPAN
// bug and no content gate can see it.
//   node --max-old-space-size=4096 _abhi04verify.js [data|rows] [from] [to]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='32Abhi04', LABEL='Kathāvatthupāḷi', MODE=process.argv[2]||'data';

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const mine=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    A(mine.length===1,'one nav node; got '+mine.length);
    const bk=mine[0];
    A(bk.title===LABEL,'THE BOOK IS Kathāvatthupāḷi, off its own title page; got '+bk.title);
    A(bk.tree.length===32,'32 top rows: the first vagga\'s ten kathās, then the '
      +'twenty-two NAMED vaggas; got '+bk.tree.length);
    // THE FIRST VAGGA HAS NO PRINTED HEADING and none is invented — the first
    // ten tops are its kathās, and the vagga level begins at the second.
    A(bk.tree.slice(0,10).every(t=>/kathā$/.test(t.label)),
      'the first ten tops are kathās: '+JSON.stringify(bk.tree.slice(0,10).map(t=>t.label)));
    A(bk.tree.slice(10).every(t=>/^\d+\.\s+\S+vagga$/.test(t.label)),
      'the remaining twenty-two tops are named vaggas');
    A(bk.tree[10].label==='2. Dutiyavagga',
      'the vagga level begins at the SECOND, as the edition prints it; got '+bk.tree[10].label);
    A(!bk.tree.some(t=>/Mahāvagga/.test(t.label)),
      'no row may be labelled Mahāvagga — it is a BOOK title elsewhere in this canon');
    // the vagga name is reprinted at the head of every kathā under it; those
    // reprints are not nodes
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    for(const t of bk.tree) walk(t.kids,[t.label]);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree);
    A(cnt===293,'293 nodes; got '+cnt);
    // the edition's longest heading, centred at indent 7 and NAMED in headfix
    const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    A(heads.includes('(175) 10. Navattabbaṁbuddhassadinnaṁmahapphalantikathā'),
      "the body's longest heading sits at indent 7 and must still be a heading");
    A(heads.filter(h=>/kathā$/.test(h)).length>=226,
      'the book\'s kathā headings; got '+heads.filter(h=>/kathā$/.test(h)).length);
    // 35 display blocks are quoted gāthā; the two that are the book's own
    // dialogue must NOT be verse
    const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
    const blocks=[].concat(...Object.values(V).map(e=>(e.after||[])
      .filter(x=>x&&typeof x==='object'&&x.gatha).map(x=>x.gatha)));
    // 35 -> 44 on 2026-07-26af.  NOT a regression: 45 of the pādas of the
    // gāthā this book quotes were being classified as COLOPHONS and drawn as
    // centred closing lines, which also CUT the blocks they belonged to in
    // two.  `pada_runon` returns them, and nine blocks that a false colophon
    // had split are now whole.  The old 35 encoded the defect.
    A(blocks.length===44,'44 gāthā blocks; got '+blocks.length);
    A(!blocks.some(b=>/^Attheva suttantoti/.test(b[0])),
      'the "Attheva suttantoti, āmantā." dialogue must not be drawn as verse');
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL); A(!!b,'no sidebar row for '+LABEL);
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===1,'one homage');
    A(txt.includes('Kathāvatthupakaraṇaṁ niṭṭhitaṁ.')||txt.includes('Mahāvaggo.'),
      'the book must render its closing material');
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,LABEL); b.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  let empty=[],whole_open=[],checked=0;
  for(const r of rows.slice(from,Math.min(to,rows.length))){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    else if(n>=whole&&whole>50) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open the WHOLE book — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

// Yamaka III (35Abhi07) — the LAST volume of the Abhidhammapiṭaka.
// NAV row sweep + the assertions no content gate makes.
//   node --max-old-space-size=4096 _abhi07verify.js [data|rows] [from] [to]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='35Abhi07', LABEL='Yamakapāḷi (Tatiyo bhāgo)', MODE=process.argv[2]||'data';
const BOOKS=['Dhammayamakapāḷi','Indriyayamakapāḷi'];

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const mine=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    A(mine.length===1,'one nav node for this volume; got '+mine.length);
    const bk=mine[0];
    A(bk.title===LABEL,'labelled as its title page labels it; got '+bk.title);
    A(bk.work==='Abhidhamma: Yamaka','work: got '+bk.work);
    A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(BOOKS),
      'two yamakas in printed order; got '+JSON.stringify(bk.tree.map(t=>t.label)));
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree); A(cnt===248,'248 nodes; got '+cnt);
    const kid=(n,l)=>(n.kids||[]).find(x=>x.label===l);
    const dh=bk.tree[0], ind=bk.tree[1];
    // THE DHAMMAYAMAKA closes with a BHĀVANĀVĀRA where the others close with a
    // Pariññāvāra, and the edition sets it as one section with nothing under it.
    A(JSON.stringify(dh.kids.map(k=>k.label))===JSON.stringify(
      ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa','2. Pavatti','3. Bhāvanāvāra']),
      'Dhamma: four divisions, the last a Bhāvanāvāra; got '+JSON.stringify(dh.kids.map(k=>k.label)));
    A(kid(dh,'3. Bhāvanāvāra').kids.length===0,'Dhamma: the Bhāvanāvāra has nothing under it');
    A(kid(dh,'2. Pavatti').kids.length===3,'Dhamma: Pavatti holds three vāras');
    A(kid(kid(dh,'2. Pavatti'),'1. Uppādavāra').kids.length===6,'Dhamma: Uppādavāra holds six');
    // THE INDRIYAYAMAKA'S PAVATTI HOLDS ONLY THE UPPĀDAVĀRA — the edition
    // prints no Nirodhavāra and no Uppādanirodhavāra for it, and its own
    // mātikā goes straight on to the Pariññāvāra.  The short branch is the
    // page's, not a drop.
    A(JSON.stringify(ind.kids.map(k=>k.label))===JSON.stringify(
      ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa','2. Pavatti','3. Pariññāvāra']),
      'Indriya: four divisions; got '+JSON.stringify(ind.kids.map(k=>k.label)));
    const pv=kid(ind,'2. Pavatti');
    A(pv.kids.length===1&&pv.kids[0].label==='1. Uppādavāra',
      'Indriya: Pavatti holds ONLY the Uppādavāra; got '+JSON.stringify(pv.kids.map(k=>k.label)));
    A(pv.kids[0].kids.length===6,'Indriya: that Uppādavāra holds six vāras');
    A(pv.kids[0].kids[0].kids.length===6,
      'Indriya: and each of those six holds the six puggala/okāsa sections');
    // ...and its Pariññāvāra has NO middle rung — six vāras directly under it,
    // each with an Anuloma and a Paccanīka.  That pairing is what `level_memo`
    // and the separate Anuloma level are for.
    const pa=kid(ind,'3. Pariññāvāra');
    A(pa.kids.length===6,'Indriya: Pariññāvāra holds six vāras directly; got '+pa.kids.length);
    A(pa.kids.every(k=>JSON.stringify(k.kids.map(x=>x.label))===JSON.stringify(['Anuloma','Paccanīka'])),
      'Indriya: each Pariññāvāra vāra holds an Anuloma and a Paccanīka, not as its siblings');
    // THE EDITION'S OWN MISPRINT, preserved verbatim
    A(pa.kids[3].label==='4. Paccuppannātītivāra',
      'p328 heads the fourth vāra "4. Paccuppannātītivāra" and it is kept as printed; got '
      +pa.kids[3].label);
    // THE SIDE-MAPS
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    A(JSON.stringify(Object.keys(H).map(Number).sort((a,b)=>a-b))===JSON.stringify([32,99,164,416]),
      'four leaked heading pairs hidden; got '+JSON.stringify(Object.keys(H)));
    for(const m of ['verse','sections','uddana','incipit','booktitle']){
      const K=JSON.parse(fs.readFileSync(R+'/'+m+'/'+VOL+'.json','utf8'));
      A(!Object.keys(K).some(k=>H[k]),m+'/ has a key that is hidden');
    }
    A(Object.keys(JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'))).length===2,
      'two homages, one per yamaka');
    // NO GĀTHĀ — 280 display lines, not one with a comma.  Nine blocks of the
    // Indriyayamaka's catechism were drawn as verse before `no_verse`.
    const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
    let blocks=0;for(const e of Object.values(V))for(const f of ['before','after','groups'])
      for(const x of (e[f]||[]))if(x&&typeof x==='object'&&x.gatha)blocks++;
    A(blocks===0,'no gāthā blocks in this volume; got '+blocks);
    // A WRAPPED DISPLAY LINE IS NOT A COLOPHON.  p83 wraps two catechetical
    // statements, and their one-word remainders were rendering as centred
    // closing lines in the middle of a vāra.
    const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
    const colo=[].concat(...Object.values(U).map(b=>[].concat(...b.map(x=>x.lines||[]))));
    A(!colo.some(l=>/^(so|do)manassaṁ\.$/.test(l.trim())),
      'the wrapped remainders "somanassaṁ." / "domanassaṁ." must not be colophons');
    A(colo.length===14,'fourteen printed closing lines; got '+colo.length);
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL); A(!!b,'no sidebar row for '+LABEL);
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===2,
      'two homages render; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    for(const t of BOOKS) A(txt.includes(t+' niṭṭhitā.'),'must render "'+t+' niṭṭhitā."');
    // the closing line of the WHOLE sixth book of the piṭaka
    A(txt.includes('Yamakapakaraṇaṁ niṭṭhitaṁ.'),
      'the last page closes the whole Yamaka, and that line must render');
    A(txt.includes('Na somanassaṁ na somanassindriyaṁ. . Na somanassindriyaṁ na somanassaṁ.'),
      'the wrapped catechetical line must render as ONE line');
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
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open the WHOLE volume — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

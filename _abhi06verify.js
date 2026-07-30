// Yamaka II (34Abhi06) — NAV row sweep + the assertions no content gate makes.
//   node --max-old-space-size=4096 _abhi06verify.js [data|rows] [from] [to]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='34Abhi06', LABEL='Yamakapāḷi (Dutiyo bhāgo)', MODE=process.argv[2]||'data';
const BOOKS=['Saṅkhārayamakapāḷi','Anusayayamakapāḷi','Cittayamakapāḷi'];

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
      'three yamakas in printed order; got '+JSON.stringify(bk.tree.map(t=>t.label)));
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree); A(cnt===262,'262 nodes; got '+cnt);
    const kid=(n,l)=>(n.kids||[]).find(x=>x.label===l);
    // THE SAṄKHĀRAYAMAKA — 33Abhi05's shape, with THREE paṇṇatti vāras not four
    // (the edition prints no Suddhasaṅkhāramūlacakkavāra) and a Pariññāvāra
    // that is one closing section with nothing under it.
    const sk=bk.tree[0];
    A(JSON.stringify(sk.kids.map(k=>k.label))===JSON.stringify(
      ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa','2. Pavatti','3. Pariññāvāra']),
      'Saṅkhāra: four divisions; got '+JSON.stringify(sk.kids.map(k=>k.label)));
    for(const d of ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa']){
      const ls=kid(sk,d).kids.map(k=>k.label);
      A(ls.length===3&&ls[2]==='3. Suddhasaṅkhāravāra',
        'Saṅkhāra '+d+': THREE vāras, the third Suddhasaṅkhāravāra; got '+JSON.stringify(ls));
    }
    A(kid(sk,'2. Pavatti').kids.length===3,'Saṅkhāra: Pavatti holds three vāras');
    A(kid(sk,'3. Pariññāvāra').kids.length===0,
      'Saṅkhāra: the Pariññāvāra has no vāras under it, as its mātikā sets it');
    // THE ANUSAYAYAMAKA — each vāra is printed TWICE, over its anuloma half and
    // its paṭiloma half, and the COLOPHONS say it is one vāra ("Anusayavāre
    // anulomaṁ." / "Anusayavāre paṭilomaṁ." / "Anusayavāro.").  ONE node, six
    // children — and splitting it would put two adjacent siblings of the same
    // name in the tree, which _navdup.js refuses.
    const an=bk.tree[1];
    A(JSON.stringify(an.kids.map(k=>k.label))===JSON.stringify(
      ['1. Uppattiṭṭhānavāra','2. Mahāvāra']),
      'Anusaya: two divisions; got '+JSON.stringify(an.kids.map(k=>k.label)));
    const mv=kid(an,'2. Mahāvāra');
    A(mv.kids.length===8,'Anusaya: the Mahāvāra holds eight vāras; got '+mv.kids.length);
    for(const v of ['1. Anusayavāra','2. Sānusayavāra','3. Pajahanavāra',
                    '4. Pariññāvāra','5. Pahīnavāra']){
      const ls=kid(mv,v).kids.map(k=>k.label);
      A(JSON.stringify(ls)===JSON.stringify(['Anulomapuggala','Anuloma-okāsa',
        'Anulomapuggalokāsa','Paṭilomapuggala','Paṭiloma-okāsa','Paṭilomapuggalokāsa']),
        'Anusaya '+v+': one node, anuloma then paṭiloma; got '+JSON.stringify(ls));
    }
    A(mv.kids.filter(k=>/^7\./.test(k.label)).length===2,
      'the edition numbers BOTH Dhātupucchāvāra and Dhātuvisajjanāvāra "7."');
    // THE CITTAYAMAKA — an Uddesa and a Niddesa of the same structure.  The
    // Niddesa's third vāra stops at the fifth, as its own mātikā (p11) sets it.
    const ct=bk.tree[2];
    A(JSON.stringify(ct.kids.map(k=>k.label))===JSON.stringify(['Uddesa','Niddesa']),
      'Citta: Uddesa and Niddesa; got '+JSON.stringify(ct.kids.map(k=>k.label)));
    for(const half of ['Uddesa','Niddesa']){
      const h=kid(ct,half);
      A(JSON.stringify(h.kids.map(k=>k.label))===JSON.stringify(
        ['1. Suddhacittasāmañña','2. Suttantacittamissakavisesa',
         '3. Abhidhammacittamissakavisesa']),
        'Citta '+half+': got '+JSON.stringify(h.kids.map(k=>k.label)));
      const sc=kid(h,'1. Suddhacittasāmañña');
      A(JSON.stringify(sc.kids.map(k=>k.label))===JSON.stringify(
        ['1. Puggalavāra','2. Dhammavāra','3. Puggaladhammavāra']),
        'Citta '+half+': three vāras under the Suddhacittasāmañña');
      A(kid(sc,'1. Puggalavāra').kids.length===14,
        'Citta '+half+' Puggalavāra: fourteen vāras; got '+kid(sc,'1. Puggalavāra').kids.length);
    }
    A(kid(kid(kid(ct,'Niddesa'),'1. Suddhacittasāmañña'),'3. Puggaladhammavāra').kids.length===5,
      "the Niddesa's Puggaladhammavāra stops at the fifth vāra, as the page sets it");
    // THE SIDE-MAPS
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    A(JSON.stringify(Object.keys(H).map(Number).sort((a,b)=>a-b))===JSON.stringify([18,79,129,164]),
      'four leaked heading pairs hidden; got '+JSON.stringify(Object.keys(H)));
    for(const m of ['verse','sections','uddana','incipit','booktitle']){
      const K=JSON.parse(fs.readFileSync(R+'/'+m+'/'+VOL+'.json','utf8'));
      A(!Object.keys(K).some(k=>H[k]),m+'/ has a key that is hidden');
    }
    A(Object.keys(JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'))).length===3,
      'three homages, one per yamaka');
    // THIS VOLUME PRINTS NO GĀTHĀ AT ALL — measured: not one display line
    // carries a comma.  Four blocks of its catechism were drawn as verse before.
    const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
    let blocks=0;for(const e of Object.values(V))for(const f of ['before','after','groups'])
      for(const x of (e[f]||[]))if(x&&typeof x==='object'&&x.gatha)blocks++;
    A(blocks===0,'no gāthā blocks in this volume; got '+blocks);
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL); A(!!b,'no sidebar row for '+LABEL);
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===3,
      'three homages render; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    for(const t of BOOKS) A(txt.includes(t+' niṭṭhitā.'),'must render "'+t+' niṭṭhitā."');
    // THE PIṬAKA'S SECOND EMBEDDED UNIT NUMBER — printed p78 sets "24.Yattha…"
    // with no space, so the corpus spliced unit 24 into ord185.  It must still
    // begin where the edition begins it, NUMBER AND ALL.
    // the reader draws a unit's number in its own `.pn` span, so textContent
    // joins it to the words with no space — that is the shape asserted here
    A(txt.includes('24.Yattha kāmarāgānusayo ca paṭighānusayo ca mānānusayo ca'),
      'the spliced unit 24 must render with its number and its WHOLE first line');
    // the edition's own misprint, preserved verbatim
    A(txt.includes('277.Yo yato kāmarāgānusayañca'),
      'the edition prints 277 for 227 and it is kept as printed');
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

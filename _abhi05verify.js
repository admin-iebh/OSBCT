// Yamaka I (33Abhi05) — NAV row sweep + the assertions no content gate makes.
// A row that opens nothing, or opens the whole volume, is a SPAN bug and the
// body gate reads 0/0/0/0 either way.
//   node --max-old-space-size=4096 _abhi05verify.js [data|rows] [from] [to]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='33Abhi05', LABEL='Yamakapāḷi (Paṭhamo bhāgo)', MODE=process.argv[2]||'data';
const BOOKS=['Mūlayamakapāḷi','Khandhayamakapāḷi','Āyatanayamakapāḷi',
             'Dhātuyamakapāḷi','Saccayamakapāḷi'];

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const mine=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ONE NODE, because the Yamaka is ONE of the piṭaka's seven books and this
    // volume is its first BHĀGA — the label is off its own title page.
    A(mine.length===1,'one nav node for this volume; got '+mine.length);
    const bk=mine[0];
    A(bk.title===LABEL,'the volume is labelled as its title page labels it; got '+bk.title);
    A(bk.work==='Abhidhamma: Yamaka','work: got '+bk.work);
    A(bk.tree.length===5,'five inner books; got '+bk.tree.length);
    A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(BOOKS),
      'the five yamakas in printed order; got '+JSON.stringify(bk.tree.map(t=>t.label)));
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree); A(cnt===492,'492 nodes; got '+cnt);
    const kid=(n,l)=>(n.kids||[]).find(x=>x.label===l);
    // THE FOUR LATER YAMAKAS SHARE ONE SHAPE, read off their own mātikās.
    for(const t of BOOKS.slice(1)){
      const b=bk.tree.find(x=>x.label===t);
      A(JSON.stringify(b.kids.map(k=>k.label))===JSON.stringify(
        t==='Dhātuyamakapāḷi'
          ? ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa','2. Pavatti','3. Pariññāvāra']
          : ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa','2. Pavatti','3. Pariññāvāra']),
        t+': four divisions; got '+JSON.stringify(b.kids.map(k=>k.label)));
      // "2. Pavatti" is the LEFT half of a printed pair-line, so it stands one
      // level above its vāras — ONE node, not one per printing.
      const pv=kid(b,'2. Pavatti');
      A(pv.kids.length===(t==='Dhātuyamakapāḷi'?1:3),
        t+': Pavatti holds its vāras; got '+pv.kids.length);
      A(pv.kids.every(k=>/^\d\. (Uppāda|Nirodha|Uppādanirodha)vāra$/.test(k.label)),
        t+': '+JSON.stringify(pv.kids.map(k=>k.label)));
      // ...and the Pariññāvāra has NO middle rung: its six vāras sit directly
      // under it where Pavatti's sit two deep.  This is what `level_memo` is for.
      const pa=kid(b,'3. Pariññāvāra');
      if(t!=='Dhātuyamakapāḷi'){
        A(pa.kids.length===6,t+': Pariññāvāra has six vāras directly under it; got '+pa.kids.length);
        A(pa.kids.every(k=>!k.kids.length),t+': and none of them nests inside another');
        A(pv.kids[0].kids.length===6,t+': Uppādavāra has six vāras; got '+pv.kids[0].kids.length);
      }
    }
    // !!! THE KHANDHAYAMAKA'S THIRD PAVATTI VĀRA IS PRINTED WITHOUT ITS LEFT
    // HALF (p67 sets a bare "3. Uppādanirodhavāra"); it must still land under
    // "2. Pavatti", which is where the volume's own mātikā puts it.
    const kh=bk.tree.find(x=>x.label==='Khandhayamakapāḷi');
    A(kid(kh,'2. Pavatti').kids.map(k=>k.label).includes('3. Uppādanirodhavāra'),
      'Khandha: the bare "3. Uppādanirodhavāra" must sit under "2. Pavatti"');
    // SANDHI: Suddha + āyatana = Suddhāyatana.  A pattern spelling `Suddha`
    // misses these two and they hang under the previous section.
    const ay=bk.tree.find(x=>x.label==='Āyatanayamakapāḷi');
    for(const d of ['1. Paṇṇattivāra-uddesa','1. Paṇṇattivāraniddesa']){
      const ls=kid(ay,d).kids.map(k=>k.label);
      A(ls.length===4&&ls[2]==='3. Suddhāyatanavāra'&&ls[3]==='4. Suddhāyatanamūlacakkavāra',
        'Āyatana '+d+': four vāras including the two sandhi ones; got '+JSON.stringify(ls));
    }
    // THE SIDE-MAPS.  A side-map entry anchored to a HIDDEN ordinal never renders.
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    A(Object.keys(H).length===9,'nine leaked heading pairs hidden; got '+Object.keys(H).length);
    A(JSON.stringify(Object.keys(H).map(Number).sort((a,b)=>a-b))
      ===JSON.stringify([148,203,329,432,512,586,615,677,726]),'the nine ordinals');
    for(const m of ['verse','sections','uddana','incipit','booktitle']){
      const K=JSON.parse(fs.readFileSync(R+'/'+m+'/'+VOL+'.json','utf8'));
      A(!Object.keys(K).some(k=>H[k]),m+'/ has a key that is hidden');
    }
    A(Object.keys(JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'))).length===5,
      'five homages, one per yamaka');
    // THE VOLUME PRINTS EXACTLY ONE GĀTHĀ, twice.  Its catechism is set with a
    // gāthā's geometry and 21 blocks of it were drawn as verse before
    // `verse_indent`.
    const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
    const blocks=[];for(const e of Object.values(V))for(const f of ['before','after','groups'])
      for(const x of (e[f]||[]))if(x&&typeof x==='object'&&x.gatha)blocks.push(x.gatha);
    A(blocks.length===2,'two gāthā blocks; got '+blocks.length);
    A(blocks.every(b=>/^Mūlaṁ hetu nidānañca/.test(b[0])),
      'both are the Mūlayamaka\'s mnemonic; got '+JSON.stringify(blocks.map(b=>b[0])));
    A(!blocks.some(b=>b.some(l=>/āmantā|sotāyatanaṁ|khandho/.test(l))),
      'no catechetical line may be drawn as verse');
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL); A(!!b,'no sidebar row for '+LABEL);
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===5,
      'five homages render, one per yamaka; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    for(const t of BOOKS) A(txt.includes(t+' niṭṭhitā.'),'the volume must render "'+t+' niṭṭhitā."');
    // the two lines the edition sets with a SINGLE space between the halves
    A(txt.includes('2. Pavatti')&&txt.includes('3. Uppādanirodhavāra'),
      'the split pair-line halves must both render as headings');
    // printed p276 — the page the declared extent left out
    A(txt.includes('6. Atītānāgatavāra')&&txt.includes('Pariññāvāro.'),
      'the last printed page\'s heading and colophon must render');
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

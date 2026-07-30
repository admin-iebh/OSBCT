// Paṭṭhāna 5 (40Abhi12) — NAV / PRESENTATION assertions.
//
// This volume is the one place in the piṭaka where the tree cannot be built
// from the heading text alone.  TWENTY books — every naya x paṭṭhāna pair —
// and EIGHT of them are CROSSED: Tikatika crosses a tika with a tika, Dukaduka
// a duka with a duka, so both levels are the same kind of section and a `re:`
// pattern for the top level matches both.  The edition separates them only by
// POSITION on the printed line ("1. Kusalattika   1. Vedanāttika", the outer
// on the left), and that position is read back off the page by the nav
// builder's `pairsides` alignment — 696 printed pair-lines, all 696 found in
// the heads stream in order.
//
// What no content gate here can see:
//   * a flattened tree.  Every second-level heading opening a NEW top leaves
//     every word of the text present and in place.
//   * a row that opens nothing, or opens its parent's whole text — a SPAN bug;
//     three shapes of it have shipped.
//   * a duplicated top.  39Abhi11 shipped with "1. Hetuduka" twenty-two times
//     in its sidebar and every one of those rows opened text.
//
//   node --max-old-space-size=4096 _abhi12verify.js data
//   node --max-old-space-size=4096 _abhi12verify.js rows <from> <to>
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='40Abhi12', LABEL='Paṭṭhānapāḷi (Pañcamo bhāgo)', MODE=process.argv[2]||'data';

// the twenty books, in the order the edition's own mātikā lists them, each
// labelled with the naya its own title page names
const NAYAS=['Dhammānuloma','Dhammapaccanīya','Dhammānulomapaccanīya',
             'Dhammapaccanīyānuloma'];
const BOOKS=[['Dhammānuloma','Tikatika'],['Dhammānuloma','Dukaduka']].concat(
  [].concat(...NAYAS.slice(1).map(n=>
    ['Tika','Duka','Dukatika','Tikaduka','Tikatika','Dukaduka'].map(k=>[n,k]))));
const TIKA=/^\d+(-\d+)?\.\s+\S*tik(a(dvaya)?|ādi)$/;
const DUKA=/^\d+(-\d+)?\.\s+\S*(duk(a(dvaya)?|ādi)|gocchak(a|ādi))$/;

(async()=>{
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const all=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ---- 1. ONE NODE, TWENTY BOOKS, LABELLED AS THE PAGE LABELS THEM ----
    A(all.length===1,VOL+' must have exactly one nav node; got '+all.length);
    const bk=all[0];
    A(bk.title===LABEL,'node label = '+bk.title);
    A(Array.isArray(bk.tree)&&bk.tree.length===20,
      'twenty inner books; got '+(bk.tree||[]).length);
    const want=BOOKS.map(([n,k])=>n+' '+k+'paṭṭhānapāḷi');
    A(JSON.stringify(bk.tree.map(t=>t.label))===JSON.stringify(want),
      'inner books = '+JSON.stringify(bk.tree.map(t=>t.label)));
    // the labels must be DISTINCT: 'Tikapaṭṭhānapāḷi' alone occurs three times
    // and 'Tikatikapaṭṭhānapāḷi' four, so the naya is what tells them apart
    A(new Set(bk.tree.map(t=>t.label)).size===20,'twenty distinct book labels');
    // ordinals strictly increasing, and each book non-empty
    let prev=-1;
    for(const t of bk.tree){
      const o=+t.key.split('#')[1];
      A(o>prev,t.label+' must start after the book before it ('+o+' <= '+prev+')');
      prev=o;
      A((t.kids||[]).length>0,t.label+' has no sections');
    }

    // ---- 2. THE CROSSED BOOKS ARE NOT FLAT ------------------------------
    // A Tikatika book's tops AND their children are both tikas; if the
    // pair-line reading had failed, every inner tika would be a top instead
    // and the book would have ~2x the tops and NO grandchildren.
    for(const t of bk.tree){
      const kind=t.label.split(' ')[1].replace('paṭṭhānapāḷi','');
      const re=(kind[0]==='T')?TIKA:DUKA;
      A(t.kids.every(k=>re.test(k.label)),
        t.label+': every top must be a numbered '+(kind[0]==='T'?'tika':'duka')
        +'; offenders '+JSON.stringify(t.kids.filter(k=>!re.test(k.label))
                                         .map(k=>k.label).slice(0,3)));
      if(kind==='Tikatika'||kind==='Dukaduka'){
        const inner=[].concat(...t.kids.map(k=>k.kids||[]));
        A(inner.length>0,t.label+' is FLAT — its inner sections became tops');
        A(inner.every(k=>re.test(k.label)),
          t.label+': a crossed book\'s second level is the same kind as its '
          +'first; offenders '+JSON.stringify(inner.filter(k=>!re.test(k.label))
                                                .map(k=>k.label).slice(0,3)));
        // and the outer must never be its own child
        for(const k of t.kids)
          A(!(k.kids||[]).some(x=>x.label===k.label),
            t.label+': '+k.label+' is nested under itself');
      }
    }

    // ---- 3. NO ROW REPEATS AN ANCESTOR, NO TWO ADJACENT SIBLINGS AGREE --
    const walk=(ns,anc)=>{for(const n of ns){
      A(!anc.includes(n.label),'row '+n.label+' repeats an ancestor');
      walk(n.kids||[],anc.concat([n.label]));}};
    for(const t of bk.tree) walk(t.kids,[t.label]);
    const adj=ns=>{const L=ns.map(n=>n.label);
      for(let i=0;i+1<L.length;i++) A(L[i]!==L[i+1],'adjacent siblings share '+L[i]);
      for(const n of ns) adj(n.kids||[]);};
    for(const t of bk.tree) adj(t.kids);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree);
    A(cnt===1262,'1262 nodes (1592 printed headings less 350 ancestor reprints, '
      +'plus the twenty book nodes); got '+cnt);

    // ---- 4. TWENTY BOOKS, TWENTY HOMAGES, NONE ON A HIDDEN ORDINAL ------
    const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    const B=JSON.parse(fs.readFileSync(R+'/booktitle/'+VOL+'.json','utf8'));
    A(Object.keys(I).length===20,'twenty homages, one per book; got '+Object.keys(I).length);
    A(Object.keys(B).length===20,'twenty title stacks; got '+Object.keys(B).length);
    for(const k of Object.keys(I)) A(!H[k],'incipit anchored to hidden ord'+k);
    for(const k of Object.keys(B)) A(!H[k],'booktitle anchored to hidden ord'+k);
    // THE EDITION'S OWN MISPRINT, PRESERVED VERBATIM: the title page at
    // 0-based 176 reads "Abhidhammapiṭika" for Abhidhammapiṭaka.
    A(JSON.stringify(Object.values(B)).includes('Abhidhammapiṭika'),
      'the "Abhidhammapiṭika" misprint must be preserved in booktitle/');

    // ---- 5. HEADINGS ----------------------------------------------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    A(!heads.some(h=>/\s{3,}/.test(h)),
      'no heading may keep a 3+ space run: '
      +JSON.stringify(heads.filter(h=>/\s{3,}/.test(h)).slice(0,3)));
    for(const [k,v] of Object.entries(S)){
      const ls=v.map(x=>x.l);
      A(new Set(ls).size===ls.length,'ord'+k+' repeats a heading: '+JSON.stringify(ls));
    }

    // ---- 6. THE RENDER ITSELF -------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL);
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===20,
      'twenty homages on the page, one per book; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    A(txt.includes('Abhidhammapiṭika'),'the misprint must render as printed');
    for(const n of NAYAS) A(txt.indexOf(n)>=0,'the naya must render: '+n);
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice -----------------------------
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,LABEL);
  b.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  // NO EXPANSION PASS — opening the volume puts its whole tree in the DOM.
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const books=new Set(BOOKS.map(([n,k])=>n+' '+k+'paṭṭhānapāḷi'));
  const slice=rows.slice(from,Math.min(to,rows.length));
  let empty=[],whole_open=[],checked=0;
  for(const r of slice){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    else if(n>=whole&&whole>50&&!books.has(lbl(r))) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+" rows open the WHOLE volume — "+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

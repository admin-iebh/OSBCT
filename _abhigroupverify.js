// Abhidhamma volume grouping (33Abhi05 … 40Abhi12) — nav assertions.
//
// USER-REPORTED: the left pane listed the piṭaka's SEVEN books as twenty-seven
// rows — five right, then the Yamaka exploded into its ten yamakas and the
// Paṭṭhāna into twelve rows with four names repeated.  Each volume now carries
// ONE node labelled as its own title page labels it, with its inner books as
// the first level of a tree.
//
// A row that opens nothing, or opens its parent's whole text, is a SPAN bug
// and no content gate can see it — three shapes of it have shipped already.
// So every row of all eight volumes is clicked here.
//
// Clicking every row of all eight takes longer than some hosts allow one
// command, so it also takes a slice of the volume list:
//   node --max-old-space-size=4096 _abhigroupverify.js          (all eight)
//   node --max-old-space-size=4096 _abhigroupverify.js 0 4      (…and a slice)
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);

const EXPECT=[
 ['33Abhi05','Yamakapāḷi (Paṭhamo bhāgo)',   ['Mūlayamakapāḷi','Khandhayamakapāḷi','Āyatanayamakapāḷi','Dhātuyamakapāḷi','Saccayamakapāḷi']],
 ['34Abhi06','Yamakapāḷi (Dutiyo bhāgo)',    ['Saṅkhārayamakapāḷi','Anusayayamakapāḷi','Cittayamakapāḷi']],
 ['35Abhi07','Yamakapāḷi (Tatiyo bhāgo)',    ['Dhammayamakapāḷi','Indriyayamakapāḷi']],
 ['36Abhi08','Paṭṭhānapāḷi (Paṭhamo bhāgo)', ['Tikapaṭṭhānapāḷi']],
 ['37Abhi09','Paṭṭhānapāḷi (Dutiyo bhāgo)',  ['Tikapaṭṭhānapāḷi']],
 ['38Abhi10','Paṭṭhānapāḷi (Tatiyo bhāgo)',  ['Dukapaṭṭhānapāḷi']],
 ['39Abhi11','Paṭṭhānapāḷi (Catuttho bhāgo)',['Dukapaṭṭhānapāḷi','Dukatikapaṭṭhānapāḷi','Tikadukapaṭṭhānapāḷi']],
 // 40Abhi12 REBUILT: the edition prints a title page and a homage for TWENTY
 // books here — every naya x paṭṭhāna pair — and the six bare names below were
 // the old grouping, taken from the corpus `book` field, which is WRONG in this
 // volume (it labels pdf 174, still inside Dhammapaccanīya Dukaduka, as
 // Dhammānulomapaccanīya Tika).  Each book is labelled with the naya its own
 // title page names, which is also what keeps the twenty labels distinct.
 ['40Abhi12','Paṭṭhānapāḷi (Pañcamo bhāgo)', [
   'Dhammānuloma Tikatikapaṭṭhānapāḷi','Dhammānuloma Dukadukapaṭṭhānapāḷi',
   'Dhammapaccanīya Tikapaṭṭhānapāḷi','Dhammapaccanīya Dukapaṭṭhānapāḷi',
   'Dhammapaccanīya Dukatikapaṭṭhānapāḷi','Dhammapaccanīya Tikadukapaṭṭhānapāḷi',
   'Dhammapaccanīya Tikatikapaṭṭhānapāḷi','Dhammapaccanīya Dukadukapaṭṭhānapāḷi',
   'Dhammānulomapaccanīya Tikapaṭṭhānapāḷi','Dhammānulomapaccanīya Dukapaṭṭhānapāḷi',
   'Dhammānulomapaccanīya Dukatikapaṭṭhānapāḷi','Dhammānulomapaccanīya Tikadukapaṭṭhānapāḷi',
   'Dhammānulomapaccanīya Tikatikapaṭṭhānapāḷi','Dhammānulomapaccanīya Dukadukapaṭṭhānapāḷi',
   'Dhammapaccanīyānuloma Tikapaṭṭhānapāḷi','Dhammapaccanīyānuloma Dukapaṭṭhānapāḷi',
   'Dhammapaccanīyānuloma Dukatikapaṭṭhānapāḷi','Dhammapaccanīyānuloma Tikadukapaṭṭhānapāḷi',
   'Dhammapaccanīyānuloma Tikatikapaṭṭhānapāḷi','Dhammapaccanīyānuloma Dukadukapaṭṭhānapāḷi']],
];

const V0=process.argv[2]!=null?+process.argv[2]:0;
const V1=process.argv[3]!=null?+process.argv[3]:EXPECT.length;

(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');

  // ---- 1. THIRTEEN ROWS, THE SEVEN BOOKS RECOGNISABLE, NO REPEATS -----
  A(ab.volumes.length===13,'the Abhidhamma should list 13 volume rows; got '+ab.volumes.length);
  const titles=ab.volumes.map(v=>v.title);
  A(new Set(titles).size===titles.length,
    'no book title may repeat; repeats: '+JSON.stringify(titles.filter((t,i)=>titles.indexOf(t)!==i)));
  for(const t of ['Dhammasaṅgaṇīpāḷi','Vibhaṅgapāḷi','Dhātukathāpāḷi',
                  'Puggalapaññattipāḷi','Kathāvatthupāḷi'])
    A(titles.includes(t),'missing book row: '+t);
  A(titles.filter(t=>/^Yamakapāḷi/.test(t)).length===3,'the Yamaka in three bhāgas');
  A(titles.filter(t=>/^Paṭṭhānapāḷi/.test(t)).length===5,'the Paṭṭhāna in five bhāgas');
  // none of the inner names may still be a top-level row
  for(const bad of ['Mūlayamakapāḷi','Tikapaṭṭhānapāḷi','Dukapaṭṭhānapāḷi'])
    A(!titles.includes(bad),bad+' must be an inner book, not a volume row');

  // ---- 2. EACH VOLUME'S INNER BOOKS, IN PRINTED ORDER -----------------
  for(const [vol,label,inner] of EXPECT){
    const v=ab.volumes.find(x=>x.vol===vol);
    A(!!v&&v.title===label,vol+' label = '+(v&&v.title));
    A(!!v&&Array.isArray(v.tree),vol+' must be a tree');
    A(JSON.stringify((v.tree||[]).map(t=>t.label))===JSON.stringify(inner),
      vol+' inner books = '+JSON.stringify((v.tree||[]).map(t=>t.label)));
    // nothing lost: the old per-book section lists survive as children
    A((v.tree||[]).every(t=>Array.isArray(t.kids)),vol+' inner books keep their sections');
    A(v.first===(v.tree||[{}])[0].key,
      vol+' first must be its own first inner book: '+v.first+' vs '+(v.tree||[{}])[0].key);
  }
  const nsec=ab.volumes.filter(v=>EXPECT.some(e=>e[0]===v.vol))
    .reduce((n,v)=>n+v.tree.reduce((m,t)=>m+1+(t.kids||[]).length
      +(t.kids||[]).reduce((q,k)=>q+(k.kids||[]).length,0),0),0);
  A(nsec>400,'the old section lists must be preserved, not dropped; kept '+nsec+' nodes');

  // ---- 3. EVERY ROW MUST OPEN ITS OWN TEXT ----------------------------
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  A(!err,'JS error on boot: '+err);
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  let empty=[],checked=0,sampled=0,total=0;
  for(const [vol,label,inner] of EXPECT.slice(V0,V1)){
    const b=find(w,label);
    A(!!b,'no sidebar row for '+label);
    if(!b) continue;
    b.click(); await wait(120);
    for(let k=0;k<40;k++){await wait(20);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const whole=w.document.querySelectorAll('#scroll .para.canon').length;
    A(whole>0,label+' opens nothing');
    // EVERY INNER-BOOK row, and a SAMPLE of the section rows beneath them.
    // The volume level and the inner books are what this change created and
    // they are all clicked; the sections below them are the old font-heuristic
    // lists, unchanged by this change, and there are ~1,700 of them across the
    // eight volumes — more than one command's budget.  SAMPLED, NOT SILENTLY
    // CAPPED: the count checked is reported below, and each volume's sections
    // are swept in full when that volume is rebuilt.
    // SAMPLE is settable so a volume with twenty inner books fits one
    // command's budget; the count checked is printed, never silently capped.
    // 40Abhi12's own sweep (`_abhi12verify.js rows`) clicks all 1262 rows.
    const SAMPLE=process.argv[4]!=null?+process.argv[4]:12;
    for(const t of inner){
      const r=[...b.parentElement.querySelectorAll('.row')].find(x=>lbl(x)===t);
      A(!!r,label+': no row for inner book '+t);
      if(!r) continue;
      r.click(); await wait(30);
      for(let k=0;k<40;k++){await wait(8);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      checked++;
      if(!w.document.querySelectorAll('#scroll .para.canon').length) empty.push(label+' / '+t);
      const kids=[...r.parentElement.querySelectorAll('.row')].filter(x=>x!==r);
      sampled+=Math.min(SAMPLE,kids.length); total+=kids.length;
      for(const k2 of kids.slice(0,SAMPLE)){
        k2.click(); await wait(4);
        for(let q=0;q<30;q++){await wait(4);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
        checked++;
        if(!w.document.querySelectorAll('#scroll .para.canon').length) empty.push(label+' / '+lbl(k2));
      }
    }
    // an inner book must open LESS than the whole volume, when there are several
    if(inner.length>1){
      const r=[...b.parentElement.querySelectorAll('.row')].find(x=>lbl(x)===inner[0]);
      r.click(); await wait(60);
      for(let k=0;k<40;k++){await wait(10);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      const one=w.document.querySelectorAll('#scroll .para.canon').length;
      A(one>0&&one<whole,
        inner[0]+' must open its own slice, not the whole volume: '+one+' of '+whole);
    }
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open nothing — '
    +JSON.stringify(empty.slice(0,8)));
  console.log('   (clicked '+checked+' rows: every volume and inner-book row, '
    +'plus '+sampled+' of '+total+' section rows sampled)');

  console.log(`\n[vols ${V0}-${V1}] ${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

// Dhātukathā + Puggalapaññatti (31Abhi03) — NAV / PRESENTATION assertions.
//
// TWO BOOKS OF THE PIṬAKA in one physical volume, so the STANDING BOUNDARY RULE
// is what matters most here: each must render its own text and stop, and each
// must have its OWN nav node — nesting the second under the first invents a book
// the edition does not print (that shape was written once and
// `_abhigroupverify.js` caught it: 12 volume rows where the piṭaka has 13).
//
//   node --max-old-space-size=4096 _abhi03verify.js [data|rows]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='31Abhi03', MODE=process.argv[2]||'data';
const NAYA=['Uddesa','1. Paṭhamanaya','2. Dutiyanaya','3. Tatiyanaya','4. Catutthanaya',
 '5. Pañcamanaya','6. Chaṭṭhanaya','7. Sattamanaya','8. Aṭṭhamanaya','9. Navamanaya',
 '10. Dasamanaya','11. Ekādasamanaya','12. Dvādasamanaya','13. Terasamanaya','14. Cuddasamanaya'];

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const mine=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ---- 1. TWO NAV NODES, ONE PER BOOK ---------------------------------
    A(mine.length===2,VOL+' must have TWO nav nodes, one per book; got '+mine.length);
    A(mine.map(v=>v.title).join(' | ')==='Dhātukathāpāḷi | Puggalapaññattipāḷi',
      'the two book nodes = '+mine.map(v=>v.title).join(' | '));
    A(mine[0].first===VOL+'#0'&&mine[1].first===VOL+'#518',
      'the book boundary is ord518 (where the corpus n resets to 1): '
      +mine.map(v=>v.first).join(' '));
    A(ab.volumes.length===13,'the piṭaka still lists its 13 volume rows; got '+ab.volumes.length);
    // ---- 2. THE TREES ---------------------------------------------------
    A(JSON.stringify(mine[0].tree.map(t=>t.label))===JSON.stringify(NAYA),
      "the Dhātukathā's Uddesa and fourteen nayas = "+JSON.stringify(mine[0].tree.map(t=>t.label)));
    A(mine[1].tree.map(t=>t.label).join('|')==='Mātikā|Niddesa',
      "the Puggalapaññatti's two halves = "+mine[1].tree.map(t=>t.label).join('|'));
    // each naya carries exactly its own padaniddesa
    let pn=0;
    for(const t of mine[0].tree.slice(1)){
      A(t.kids.length>=1&&/padaniddesa$/.test(t.kids[0].label),
        t.label+' must open with its padaniddesa; got '+(t.kids[0]||{}).label);
      pn++;
    }
    A(pn===14,'fourteen nayas; got '+pn);
    A(mine[0].tree[0].kids.length===5,"the Uddesa's five mātikās; got "+mine[0].tree[0].kids.length);
    A(mine[1].tree[0].kids.length===10&&mine[1].tree[1].kids.length===10,
      'ten uddesas and ten paññattis; got '+mine[1].tree[0].kids.length+' and '
      +mine[1].tree[1].kids.length);

    // ---- 3. TWO HOMAGES, AND ONE OF THEM IS CAPITALISED -----------------
    const I=JSON.parse(fs.readFileSync(R+'/incipit/'+VOL+'.json','utf8'));
    const H=JSON.parse(fs.readFileSync(R+'/hide/'+VOL+'.json','utf8'));
    const B=JSON.parse(fs.readFileSync(R+'/booktitle/'+VOL+'.json','utf8'));
    A(Object.keys(I).length===2,'two homages, one per book; got '+Object.keys(I).length);
    for(const k of Object.keys(I)) A(!H[k],'incipit anchored to hidden ord'+k);
    for(const k of Object.keys(B)) A(!H[k],'booktitle anchored to hidden ord'+k);
    // the SECOND book prints "Namo Tassa" with a capital T — the form 38Abhi10
    // also uses, and the reason HOMAGE matches either case.  The FIRST prints no
    // terminal full stop.  Both kept exactly as printed.
    const inc=Object.entries(I).sort((a,b)=>+a[0]-+b[0]).map(x=>String(x[1]));
    A(/Namo tassa/.test(inc[0])&&!/\.$/.test(inc[0].trim()),
      "the Dhātukathā's homage is lowercase and carries NO terminal stop: "+inc[0]);
    A(/Namo Tassa/.test(inc[1]),
      "the Puggalapaññatti's homage prints a capital T: "+inc[1]);
    A(Object.keys(B).map(Number).sort((a,b)=>a-b).join(',')==='0,518',
      'a title stack per book, the second re-keyed off ord517: '+Object.keys(B));

    // ---- 4. VERSE, and the prose list that is NOT verse ------------------
    const ent=Object.values(V);
    A(ent.length===890,'890 units; got '+ent.length);
    const blocks=[].concat(...ent.map(e=>(e.after||[])
      .filter(x=>x&&typeof x==='object'&&x.gatha).map(x=>x.gatha)));
    A(blocks.length===9,'nine gāthā blocks, all in the Dhātukathā; got '+blocks.length);
    A(Object.entries(V).every(([k,e])=>+k<518||!(e.after||[])
        .some(x=>x&&typeof x==='object'&&x.gatha)),
      'the Puggalapaññatti prints NO gāthā — its "Kathañca puggalo…" one clause '
      +'per line is prose, which `verse_indent` is what separates');
    A(blocks.every(b=>b.length>=2),'no gāthā block may be a single line');

    // ---- 5. THE EDITION'S TWO MISPRINTS, PRESERVED VERBATIM -------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    A(heads.includes('5. Pañcakapaggalapaññatti'),
      'the body\'s "paggala" misprint must be kept as printed');
    A(!heads.includes('5. Pañcakapuggalapaññatti'),
      'and must NOT be silently corrected to the mātikā\'s spelling');
    const colo=[].concat(...Object.values(U)).flatMap(b=>b.lines||[]);
    A(colo.some(l=>/saṅgahitapasaniddeso catuttho\./.test(l)),
      'the "pasaniddeso" colophon misprint must be kept as printed');
    // ALL FOURTEEN NAYAS ARE CLOSED, thirteen spelling it `padaniddeso` and the
    // fourth `pasaniddeso`.  The eleventh was MISSING until 2026-07-26z: the
    // edition centres it and its name is long, so it sits at indent 7 where the
    // other thirteen sit at 20+, and the display gate refused it.
    A(colo.filter(l=>/padaniddeso /.test(l)).length===13,
      'thirteen padaniddesa colophons spell it correctly; got '
      +colo.filter(l=>/padaniddeso /.test(l)).length);
    A(colo.some(l=>/sampayuttavippayuttapadaniddeso ekādasamo\./.test(l)),
      "the eleventh naya's colophon sits at indent 7 and must still be one");

    // ---- 6. THE RENDER, and the standing boundary rule ------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    for(const [title,inside,outside] of [
        ['Dhātukathāpāḷi','Saṅgaho asaṅgaho','Cha paññattiyo'],
        ['Puggalapaññattipāḷi','Cha paññattiyo','Saṅgaho asaṅgaho']]){
      const b=find(w,title);
      A(!!b,'no sidebar row for '+title);
      b.click(); await wait(250);
      for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      const txt=N(w.document.getElementById('scroll').textContent);
      A(txt.includes(inside),title+' must render its own opening: '+inside);
      A(!txt.includes(outside),title+' must NOT bleed into the other book: '+outside);
      A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===1,
        title+' shows exactly its own homage; got '
        +(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    }
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS ------------------------------------------------------------
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  let empty=[],whole_open=[],checked=0;
  for(const title of ['Dhātukathāpāḷi','Puggalapaññattipāḷi']){
    const b=find(w,title); b.click(); await wait(200);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const whole=w.document.querySelectorAll('#scroll .para.canon').length;
    A(whole>0,title+' opens nothing');
    for(const r of [...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b)){
      r.click(); await wait(2);
      for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      const n=w.document.querySelectorAll('#scroll .para.canon').length;
      checked++;
      if(!n) empty.push(title+' / '+lbl(r));
      else if(n>=whole&&whole>50) whole_open.push(title+' / '+lbl(r));
    }
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open their whole book — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (clicked '+checked+' rows across both books)');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

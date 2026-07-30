// Vibhaṅga (30Abhi02) — NAV / PRESENTATION assertions.
//
// The volume is one book with a clean 1:1 pairing, so what needs asserting here
// is its SHAPE and its ROLES, which no content gate can see:
//   * 42 prose LISTS that have a gāthā's geometry ("Duvidhena vedanākkhandho–
//     atthi sahetuko, atthi ahetuko." one item per printed line).  The edition
//     prints THREE gāthā in the whole volume and the build drew 45 before
//     `verse_indent` — every word present, contiguous and unique either way.
//   * a numbered unit that IS a gāthā (printed p441, unit 1029).
//   * 18 vibhaṅgas nested three deep, and every row opening its own slice.
//
//   node --max-old-space-size=4096 _abhi02verify.js [data|rows]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>String(s).normalize('NFC').replace(/\s+/g,' ').trim();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL='30Abhi02', LABEL='Vibhaṅgapāḷi', MODE=process.argv[2]||'data';
const VIB=['1. Khandhavibhaṅga','2. Āyatanavibhaṅga','3. Dhātuvibhaṅga',
 '4. Saccavibhaṅga','5. Indriyavibhaṅga','6. Paṭiccasamuppādavibhaṅga',
 '7. Satipaṭṭhānavibhaṅga','8. Sammappadhānavibhaṅga','9. Iddhipādavibhaṅga',
 '10. Bojjhaṅgavibhaṅga','11. Maggaṅgavibhaṅga','12. Jhānavibhaṅga',
 '13. Appamaññāvibhaṅga','14. Sikkhāpadavibhaṅga','15. Paṭisambhidāvibhaṅga',
 '16. Ñāṇavibhaṅga','17. Khuddakavatthuvibhaṅga','18. Dhammahadayavibhaṅga'];

(async()=>{
  const V=JSON.parse(fs.readFileSync(R+'/verse/'+VOL+'.json','utf8'));
  const S=JSON.parse(fs.readFileSync(R+'/sections/'+VOL+'.json','utf8'));
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const ab=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Abhidhammapiṭaka');
  const all=ab.volumes.filter(v=>v.vol===VOL);

  if(MODE==='data'){
    // ---- 1. ONE NODE, EIGHTEEN VIBHAṄGAS IN PRINTED ORDER ---------------
    A(all.length===1,VOL+' must have exactly one nav node; got '+all.length);
    const bk=all[0];
    A(bk.title===LABEL,'node label = '+bk.title);
    // ONE BOOK IN THE VOLUME, so the eighteen vibhaṅgas are the FIRST tree
    // level directly — the 29Abhi01 shape, not the multi-book wrapper that
    // 39Abhi11 and 40Abhi12 need.
    A(Array.isArray(bk.tree)&&bk.tree.length===18,
      'eighteen top nodes; got '+(bk.tree||[]).length);
    const inner={kids:bk.tree};
    A(JSON.stringify(inner.kids.map(k=>k.label))===JSON.stringify(VIB),
      'the eighteen vibhaṅgas in printed order = '+JSON.stringify(inner.kids.map(k=>k.label)));
    // ---- 2. NESTED, NOT FLAT -------------------------------------------
    // thirteen vibhaṅgas divide into bhājanīyas + a Pañhāpucchaka; the
    // Indriyavibhaṅga prints NO Suttantabhājanīya, so its own two divisions are
    // numbered 1 and 2 — the numbering must not be normalised.
    const B=Object.fromEntries(inner.kids.map(k=>[k.label,k]));
    A(B['5. Indriyavibhaṅga'].kids.map(k=>k.label).join(' | ')
      ==='1. Abhidhammabhājanīya | 2. Pañhāpucchaka',
      'the Indriyavibhaṅga numbers its two divisions 1 and 2: '
      +B['5. Indriyavibhaṅga'].kids.map(k=>k.label).join(' | '));
    // a Pañhāpucchaka carries the Tika and the Duka BENEATH it, three deep
    let three=0;
    for(const v of inner.kids)
      for(const d of v.kids)
        if(/Pañhāpucchaka$/.test(d.label)){
          A(d.kids.map(k=>k.label).join('|')==='1. Tika|2. Duka',
            v.label+' / '+d.label+' kids = '+d.kids.map(k=>k.label).join('|'));
          three++;
        }
    // FOURTEEN, not twelve: the label is numbered "3. Pañhāpucchaka" in twelve
    // vibhaṅgas and "2. Pañhāpucchaka" in the two that print no
    // Suttantabhājanīya, and the edition's numbering is kept as printed.
    A(three===14,'fourteen Pañhāpucchakas carry a Tika and a Duka; got '+three);
    A(B['18. Dhammahadayavibhaṅga'].kids.length===10,
      "the Dhammahadaya's ten vāras; got "+B['18. Dhammahadayavibhaṅga'].kids.length);
    let cnt=0; const count=ns=>{for(const n of ns){cnt++;count(n.kids||[]);}};
    count(bk.tree);
    A(cnt===222,'222 nodes (18 vibhaṅgas + 204 sections); got '+cnt);

    // ---- 3. THREE GĀTHĀ IN THE WHOLE VOLUME, AND 42 PROSE LISTS ---------
    const ent=Object.values(V);
    A(ent.length===1044,'1044 units; got '+ent.length);
    const vs=Object.entries(V).filter(([k,e])=>e.groups&&e.groups.length);
    const blocks=[].concat(...ent.map(e=>(e.after||[])
      .filter(x=>x&&typeof x==='object'&&x.gatha).map(x=>x.gatha)));
    A(vs.length===1&&vs[0][0]==='1028',
      'exactly ONE numbered unit is a gāthā (printed p441, unit 1029 = ord1028); got '
      +JSON.stringify(vs.map(x=>x[0])));
    A(vs.length&&vs[0][1].groups[0].length===8,
      "unit 1029's gāthā keeps all eight pādas; got "
      +(vs.length?vs[0][1].groups[0].length:0));
    A(blocks.length===2,'exactly TWO gāthā blocks (printed p439 and p453); got '+blocks.length);
    A(blocks.every(b=>b.length>=2),'no gāthā block may be a single line');
    // and the prose lists must NOT be verse: no gāthā line may open with the
    // Vibhaṅga's own enumeration formula
    const LIST=/^(?:Ekavidhena|Duvidhena|Tividhena|Catubbidhena|Pañcavidhena|Chabbidhena|Sattavidhena|Aṭṭhavidhena|Navavidhena|Dasavidhena|Bahuvidhena)\b/;
    const bad=[].concat(...blocks,...vs.map(x=>x[1].groups[0])).filter(l=>LIST.test(l));
    A(bad.length===0,'a prose enumeration is drawn as verse: '+JSON.stringify(bad.slice(0,3)));

    // ---- 4. HEADINGS, and the edition's own misprint --------------------
    const heads=[].concat(...Object.values(S)).map(x=>x.l);
    A(heads.filter(h=>/vibhaṅga$/.test(h)).length===18,'eighteen vibhaṅga headings');
    A(!heads.some(h=>/\s{3,}/.test(h)),'no heading may keep a 3+ space run');
    for(const [k,v2] of Object.entries(S)){
      const ls=v2.map(x=>x.l);
      A(new Set(ls).size===ls.length,'ord'+k+' repeats a heading: '+JSON.stringify(ls));
    }
    // ERRATUM, PRESERVED VERBATIM: the last vibhaṅga closes "niṭṭhoto."
    const U=JSON.parse(fs.readFileSync(R+'/uddana/'+VOL+'.json','utf8'));
    const colo=[].concat(...Object.values(U)).flatMap(b=>b.lines||[]);
    A(colo.some(l=>/Dhammahadayavibhaṅgo niṭṭhoto\./.test(l)),
      'the "niṭṭhoto" misprint must be preserved as printed');
    // \d? — THE EDITION ABUTS A FOOTNOTE MARKER TO THE WORD IT MARKS, and the
    // sixth vibhaṅga's colophon carries one: "Paṭiccasamuppādavibhaṅgo1
    // niṭṭhito."  Without it this assertion reads 17 and looks like a dropped
    // colophon.
    A(colo.filter(l=>/vibhaṅgo\d? niṭṭh(?:ito|oto)\./.test(l)).length===18,
      'eighteen vibhaṅga colophons, seventeen niṭṭhito and one niṭṭhoto; got '
      +colo.filter(l=>/vibhaṅgo\d? niṭṭh(?:ito|oto)\./.test(l)).length);

    // ---- 5. THE RENDER --------------------------------------------------
    const w=boot(); let err=null; w.addEventListener('error',ev=>err=ev.message);
    if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
    A(!err,'JS error on boot: '+err);
    const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
    const b=find(w,LABEL);
    A(!!b,'no sidebar row for the volume');
    b.click(); await wait(250);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const txt=N(w.document.getElementById('scroll').textContent);
    A((txt.match(/[Nn]amo [Tt]assa/g)||[]).length===1,
      'one homage; got '+(txt.match(/[Nn]amo [Tt]assa/g)||[]).length);
    A(txt.includes('Dhammahadayavibhaṅgo niṭṭhoto.'),'the misprint must render as printed');
    A(txt.includes('Vibhaṅgapakaraṇaṁ niṭṭhitaṁ.'),'the book-end colophon must render');
    A(txt.includes('Cha ete'),'the p439 gāthā must render');
    console.log(`\n${pass} passed, ${fail} failed`);
    process.exit(fail?1:0);
  }

  // ---- ROWS: every row opens its own slice ----------------------------
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,'Abhidhammapiṭaka'); if(pit){pit.click(); await wait(80);}
  const b=find(w,LABEL);
  b.click(); await wait(200);
  for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
  const whole=w.document.querySelectorAll('#scroll .para.canon').length;
  A(whole>0,'the volume opens nothing');
  const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
  const from=+(process.argv[3]||0), to=+(process.argv[4]||1e9);
  const slice=rows.slice(from,Math.min(to,rows.length));
  let empty=[],whole_open=[],checked=0;
  for(const r of slice){
    r.click(); await wait(2);
    for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const n=w.document.querySelectorAll('#scroll .para.canon').length;
    checked++;
    if(!n) empty.push(lbl(r));
    else if(n>=whole&&whole>50&&lbl(r)!==LABEL) whole_open.push(lbl(r));
  }
  A(empty.length===0,empty.length+' of '+checked+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+checked+' rows open the WHOLE volume — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   (rows '+from+'-'+Math.min(to,rows.length)+' of '+rows.length+', clicked '+checked+')');
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

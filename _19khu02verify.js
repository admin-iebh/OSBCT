// 19Khu02 PRESENTATION assertions — the layer the content harness is blind to.
// verify_render_vs_pdf.py can report 0/0/0/0 while a heading renders as body
// text, a verse renders as prose, or a book bleeds into the next; those are only
// visible once the real reader has rendered the real data. Add a rule here the
// moment one is agreed — anything not asserted regresses silently.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>s.normalize('NFC').replace(/\s+/g,' ').toLowerCase();
// jsdom boot time varies; wait for the nav tree instead of guessing a delay.
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>100) return true; }
  return false; }
const BOOKS=[
 {t:'Vimānavatthupāḷi', open:'Pīṭhaṁ te sovaṇṇamayaṁ uḷāraṁ',           end:'Akkhāmi te bhikkhu mahānubhāva', paras:1031},
 {t:'Petavatthupāḷi',   open:'Khettūpamā arahanto, dāyakā kassakūpamā', end:'Dhammena te kāpurisa',          paras:814},
 {t:'Theragāthāpāḷi',   open:'Channā me kuṭikā sukhā nivātā',           end:'Taṁ Devadevaṁ vandāmi',         paras:1288},
 {t:'Therīgāthāpāḷi',   open:'Sukhaṁ supāhi therike',                   end:'Evaṁ karonti ye sadda',         paras:524},
];
let pass=0, fail=0;
const A=(ok,msg)=>{ if(ok){pass++;} else {fail++; console.log('   FAIL: '+msg);} };

async function openBook(w,title,leafPath){
  const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
  const find=t=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
  let r=find('Pāḷi'); if(r) r.click(); await wait(60);
  r=find('Khuddakanikāya'); if(r) r.click(); await wait(60);
  let row=find(title); if(!row) return null; row.click(); await wait(80);
  for(const step of (leafPath||[])){
    const host=row.parentElement.querySelector('.kids');
    const next=[...host.querySelectorAll('.row')].find(x=>lbl(x)===step);
    if(!next) return null; next.click(); await wait(80); row=next;
  }
  for(let k=0;k<70;k++){ await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>1500) break; }
  return w.document;
}

(async()=>{
  // ---- 1. book spans: no bleed, correct paragraph counts -------------------
  for(const b of BOOKS){
    const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
    if(!await ready(w)){ A(false,`${b.t}: nav never rendered`); continue; }
    const doc=await openBook(w,b.t);
    if(!doc){ A(false,`${b.t}: no nav row`); continue; }
    const txt=N(doc.querySelector('#scroll').textContent);
    const np=doc.querySelectorAll('#scroll .para.canon').length;
    A(!err, `${b.t}: JS error ${err}`);
    A(txt.includes(N(b.open)), `${b.t}: own opening verse missing`);
    A(txt.includes(N(b.end)),  `${b.t}: own closing verse missing`);
    A(np===b.paras, `${b.t}: ${np} paragraphs rendered, expected ${b.paras}`);
    for(const o of BOOKS) if(o!==b)
      A(!txt.includes(N(o.open)), `${b.t}: BLEEDS ${o.t} (its opening verse is rendered here)`);
    A(doc.querySelectorAll('#scroll .incipit').length===1,
      `${b.t}: expected exactly one printed homage as .incipit, got ${doc.querySelectorAll('#scroll .incipit').length}`);
    // the homage must never be ordinary body text at a book head
    A(![...doc.querySelectorAll('#scroll .para.canon')].some(p=>/Namo tassa/.test(p.textContent)),
      `${b.t}: homage rendered as body text`);
    // verses render as verse, and their number hangs inside the first .gatha
    const g=doc.querySelectorAll('#scroll .gatha').length;
    A(g>=b.paras*0.9, `${b.t}: only ${g} gāthā blocks for ${b.paras} verse paragraphs`);
    let stacked=0;
    for(const p of doc.querySelectorAll('#scroll .para.canon')){
      if(!p.querySelector('.gatha')) continue;
      const f=p.querySelector('.pn'); if(f&&!f.closest('.gatha')) stacked++;
    }
    A(stacked===0, `${b.t}: ${stacked} verse number(s) on a line of their own`);
  }

  // ---- 2. the four-level Vimānavatthu tree --------------------------------
  {
    const w=boot(); await ready(w);
    const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
    const find=t=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
    for(const t of ['Pāḷi','Khuddakanikāya']){ const r=find(t); if(r){ r.click(); await wait(60); } }
    const book=find('Vimānavatthupāḷi'); book.click(); await wait(80);
    const kids=book.parentElement.querySelector('.kids');
    const divs=[...kids.children].map(c=>c.querySelector(':scope > .row')).filter(Boolean).map(lbl);
    A(divs.length===2 && divs[0]==='1. Itthivimāna' && divs[1]==='2. Purisavimāna',
      `Vimānavatthu divisions = ${JSON.stringify(divs)}`);
    const vagLabels=[];
    for(const dw of [...kids.children]){
      const drow=dw.querySelector(':scope > .row'); if(!drow) continue;
      drow.click(); await wait(60);
      const dk=dw.querySelector('.kids');
      for(const vw of [...dk.children]){
        const vr=vw.querySelector(':scope > .row')||vw; vagLabels.push(lbl(vr));
      }
    }
    A(vagLabels.length===7, `Vimānavatthu vaggas = ${vagLabels.length}, expected 7`);
    // THE EDITION NUMBERS THE VAGGAS CONTINUOUSLY 1-7 ACROSS THE TWO DIVISIONS
    const nums=vagLabels.map(l=>parseInt(l,10));
    A(JSON.stringify(nums)===JSON.stringify([1,2,3,4,5,6,7]),
      `vagga numbering must run 1-7 continuously across divisions, got ${JSON.stringify(nums)}`);
    // leaves: the edition has 85 vimānas
    let leaves=0;
    for(const dw of [...kids.children]){
      const dk=dw.querySelector('.kids'); if(!dk) continue;
      for(const vw of [...dk.children]){
        const vrow=vw.querySelector(':scope > .row'); if(!vrow) continue;
        vrow.click(); await wait(40);
        const lk=vw.querySelector('.kids');
        if(lk) leaves+=[...lk.children].filter(c=>c.classList.contains('row')||c.querySelector(':scope > .row')).length;
      }
    }
    A(leaves===85, `Vimānavatthu vimāna leaves = ${leaves}, the edition has 85`);
  }

  // ---- 3. Theragāthā's Nidānagāthā, which the corpus does not hold ---------
  {
    const w=boot(); await ready(w);
    const doc=await openBook(w,'Theragāthāpāḷi');
    const html=doc.querySelector('#scroll').innerHTML;
    const txt=N(doc.querySelector('#scroll').textContent);
    A(txt.includes(N('Sīhānaṁva nadantānaṁ, dāṭhīnaṁ girigabbhare')),
      'Theragāthā: Nidānagāthā missing from the render');
    const iInc=html.indexOf('incipit'), iNid=html.indexOf('Sīhānaṁva'), iV1=html.indexOf('Channā me kuṭikā');
    A(iInc>=0 && iInc<iNid && iNid<iV1,
      'Theragāthā: printed order must be homage -> Nidānagāthā -> verse 1');
  }

  // ---- 4. leaked section headings are not rendered as paragraphs -----------
  {
    const w=boot(); await ready(w);
    const doc=await openBook(w,'Vimānavatthupāḷi');
    const bodies=[...doc.querySelectorAll('#scroll .para.canon')].map(p=>N(p.textContent));
    for(const s of ['valliphaladā yikāvimānavatthu','phārusakadā yikāvimānavatthu','uttara (pāyāsi) vimānavatthu'])
      A(!bodies.some(b=>b.trim().startsWith(N(s).replace(/^\d+\.\s*/,'')) || b.includes(N(s))&&b.length<90),
        `leaked heading still rendered as a paragraph: ${s}`);
  }

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

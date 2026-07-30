// 19Khu02 BOOK-SPAN BLEED CHECK (the standing rule at the top of HANDOFF.md).
// Boots the real reader, opens each of the four books in turn, and asserts that
// the render contains that book's own opening AND end, and NONE of the other
// three books' opening verses.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
// --bad reinstates the ORIGINAL, WRONG book boundaries (Theragāthā 1849,
// Therīgāthā 3140) in memory, so this checker's sensitivity stays reproducible
// without depending on a backup file that each nav build overwrites.
// Expected with --bad: 3 of 4 books FAIL — Petavatthu renders Theragāthā's first
// verse, Theragāthā renders Therīgāthā's first four, Therīgāthā loses its own.
const BAD=process.argv.includes('--bad');
const WRONG={'19Khu02#1848':1849,'19Khu02#3136':3140};
function spoil(t){ const n=JSON.parse(t);
  for(const L of n.layers) for(const nk of (L.nikayas||[])) for(const v of (nk.volumes||[]))
    if(WRONG[v.first]!==undefined) v.first=v.vol+'#'+WRONG[v.first];
  return JSON.stringify(n); }
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}if(t!=null&&BAD&&/nav\.json$/.test(f))t=spoil(t);return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>s.normalize('NFC').replace(/\s+/g,' ').toLowerCase();
const BOOKS=[
 {t:'Vimānavatthupāḷi', key:'19Khu02#0',    open:'Pīṭhaṁ te sovaṇṇamayaṁ uḷāraṁ',      end:'Akkhāmi te bhikkhu mahānubhāva'},
 {t:'Petavatthupāḷi',   key:'19Khu02#1034', open:'Khettūpamā arahanto, dāyakā kassakūpamā', end:'Dhammena te kāpurisa'},
 {t:'Theragāthāpāḷi',   key:'19Khu02#1848', open:'Channā me kuṭikā sukhā nivātā',     end:'Taṁ Devadevaṁ vandāmi'},
 {t:'Therīgāthāpāḷi',   key:'19Khu02#3136', open:'Sukhaṁ supāhi therike',              end:'Evaṁ karonti ye sadda'},
];
(async()=>{
  let fails=0;
  for(const b of BOOKS){
    const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
    await wait(800);
    // Drive the REAL nav: expand Khuddakanikāya, expand the book row, then click
    // its first vagga leaf. For a `nipata` node that leaf sets
    // state.curbook = the book's `first` key, so BOOKSPAN slices to this book —
    // which is exactly the code path a user exercises.
    const lbl=r=>(r.querySelector('.lbl')||{}).textContent||'';
    const findRow=t=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r).trim()===t);
    let r=findRow('Pāḷi'); if(r) r.click(); await wait(60);
    r=findRow('Khuddakanikāya'); if(r) r.click(); await wait(60);
    const br=findRow(b.t);
    if(!br) console.log('  no nav row for',b.t); else br.click();
    for(let k=0;k<80;k++){ await wait(90); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>2000) break; }
    const txt=N(w.document.querySelector('#scroll').textContent);
    const paras=w.document.querySelectorAll('#scroll .para.canon').length;
    const has=s=>txt.includes(N(s));
    const own = has(b.open) && has(b.end);
    const bleed = BOOKS.filter(o=>o!==b && has(o.open)).map(o=>o.t);
    const ok = own && bleed.length===0 && !err;
    if(!ok) fails++;
    console.log(`${ok?'PASS':'FAIL'}  ${b.t.padEnd(18)} ¶=${String(paras).padStart(5)}  own-open=${has(b.open)} own-end=${has(b.end)}  bleed=[${bleed.join(',')}]${err?'  JS-ERROR: '+err:''}`);
  }
  console.log(fails? `\n${fails} book(s) FAILED the bleed check` : '\nALL FOUR BOOKS: no bleed, each renders its own opening and end.');
  process.exit(fails?1:0);
})();

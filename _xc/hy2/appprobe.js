// PROBE: does the reader render the apparatus in the A / Ṭ bands?
// Reader, 2026-08-08: "the footnotes are missing" when a commentary is opened
// from the left pane.  This asks the rendered DOM, not the source.
//
// !!! THE BAND KINDS ARE 'canon' | 'A' | 'T' (reader2.html:947), NOT the layer
// names.  A first version passed 'comm'/'tika', which fell through to the canon
// branch, drew the CANON volume as spine with both bands off, and reported
// "paragraph not drawn" -- a fact about the probe reported as a fact about the
// reader.  And `state`/`cache` are top-level `const`, so they are lexical
// globals, not properties of `window`: read them with eval, never `w.cache`.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

const CASES=[
  ['31KhuA12', 210, 'A'],   // the reader's own case: Gotamī, p. 146
  ['32KhuA13', 100, 'A'],
  ['33KhuA14', 566, 'A'],
  ['09DiT02',  200, 'T'],
  ['20Khu03',   10, 'canon'],   // canon control
  ['19Khu02', 3294, 'canon'],   // canon control, the linked paragraph
];

(async()=>{
  const w=boot();
  if(!await ready(w)){ console.log('nav never built'); process.exit(1); }
  for(const [vol,ord,kind] of CASES){
    let err='';
    try{ await w.eval('openKey')(vol+'#'+ord, kind); }catch(e){ err=String(e&&e.message||e); }
    for(let k=0;k<60;k++){ await wait(80);
      const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
    const d=w.document;
    const c=(w.eval('cache')||{})[vol]||{};
    const appMap=c.app||{};
    const nHere=(appMap[String(ord)]||[]).length;
    const el=d.getElementById('p-'+vol+'-'+ord);
    const inPara=el?el.querySelectorAll('.appx').length:-1;
    const supHere=el?el.querySelectorAll('sup.fnm').length:-1;
    // over every DRAWN paragraph of this volume: data vs page
    let drawn=0, wantApp=0, gotApp=0;
    d.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
      drawn++; const o=x.id.slice(('p-'+vol+'-').length);
      const want=(appMap[o]||[]).length>0, got=x.querySelectorAll('.appx').length>0;
      if(want) wantApp++; if(got) gotApp++;
    });
    console.log(`${vol}#${ord} ${kind}  state=${JSON.stringify(w.eval('state').active)}`
      +`\n    appk keys=${Object.keys(appMap).length}  notes@ord=${nHere}`
      +`  para drawn=${el?'yes':'NO'}  .appx-in-para=${inPara}  sup.fnm-in-para=${supHere}`
      +`\n    drawn=${drawn}  paras whose DATA has apparatus=${wantApp}  paras that DREW it=${gotApp}`
      +(err?'  ERR='+err:''));
  }
  process.exit(0);
})();

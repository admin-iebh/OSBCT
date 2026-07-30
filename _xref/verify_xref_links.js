// Does a printed cross-reference actually RENDER as a live `->` link now?
//
// `check_layout.js` says 0 layout issues either way: it grades roles, not
// apparatus links, and a citation rendered as dead text is not a layout fault.
// So it was blind to the whole defect (2026-07-30f).  This boots the REAL reader
// over the REAL data, exactly as check_layout does, opens each named volume and
// counts `a.xref` anchors in the rendered apparatus.
//
//   node _xref/verify_xref_links.js 09DiT02 07ViT07 ...
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){
  const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
function layerOf(vol){
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  for(const L of (nav.layers||[])) for(const n of (L.nikayas||[])) for(const v of (n.volumes||[])) if(v.vol===vol) return L.layer;
  return 'canon';
}
const KIND={canon:'canon',commentary:'A',subcommentary:'T'};
(async()=>{
  // RESUMABLE + BUDGETED: the device shell is capped at 45s and background jobs
  // do not survive between calls, so drive the 81 volumes in foreground chunks.
  const LOG='_xref/render_results.txt';
  let vols=process.argv.slice(2);
  if(!vols.length) vols=fs.readFileSync('_xref/changed.txt','utf8').split('\n').map(s=>s.trim()).filter(Boolean);
  const done=fs.existsSync(LOG)?new Set(fs.readFileSync(LOG,'utf8').split('\n').map(l=>l.trim().split(/\s+/)[1]).filter(Boolean)):new Set();
  vols=vols.filter(v=>!done.has(v));
  const t0=Date.now(), BUDGET=32000;
  let totLink=0,totDead=0,bad=0;
  for(const vol of vols){
    if(Date.now()-t0>BUDGET){ console.log('-- budget reached --'); break; }
    const w=boot(); await wait(600);
    // the appk map is the ONLY place the reader can get xrefs from
    const appk=JSON.parse(fs.readFileSync(R+'/apparatus/'+vol+'.appk.json','utf8'));
    const withX=Object.keys(appk).filter(o=>appk[o].some(n=>(n.xrefs||[]).length));
    if(!withX.length){ const l='  --   '+vol+'  no xrefs in appk'; console.log(l); fs.appendFileSync(LOG,l+'\n'); continue; }
    try{ w.openKey(vol+'#'+withX[0], KIND[layerOf(vol)]); }catch(e){}
    await wait(900);
    const live=w.document.querySelectorAll('a.xref').length;
    const dead=[...w.document.querySelectorAll('span.xref')].length;
    totLink+=live; totDead+=dead;
    const ok=live>0;
    if(!ok) bad++;
    const line='  '+(ok?'ok  ':'FAIL')+' '+vol.padEnd(11)+' a.xref '+String(live).padStart(4)
                +'   span.xref(unresolved) '+String(dead).padStart(3)
                +'   appk ords carrying xrefs '+withX.length;
    console.log(line); fs.appendFileSync(LOG,line+'\n');
    w.close();
  }
  console.log('\n'+vols.length+' volume(s): '+totLink+' live -> links rendered, '+totDead
              +' unresolved, '+bad+' with NO live link');
  process.exit(bad?1:0);
})();

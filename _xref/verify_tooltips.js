// Are the tooltips Spanish when the interface is Spanish?
// Boots the real reader twice — once with osbct-lang=en, once with =es — and
// compares the tooltip of every toolbar control AND of the tooltips the reader
// builds in JS (copy buttons, page badges, xref links, jump buttons).
// A tooltip identical in both languages is only reported, not failed: some are
// Pāḷi and must not change.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(lang){
  const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.localStorage.setItem('osbct-lang',lang);
    // JSDOM does not fetch <script src>, so i18n.js would never load and every
    // tooltip would read English in both runs — a PASSING-LOOKING test that
    // proves nothing.  Inject it the way the browser would.
    if(!process.env.OSBCT_NO_I18N) w.eval(fs.readFileSync('site/i18n.js','utf8'));
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
    w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
const IDS=['sidetog','themebtn','tocbtn','readtog','fdec','finc'];
(async()=>{
  const out={};
  for(const lang of ['en','es']){
    const w=boot(lang); await wait(700);
    try{ w.openKey('09DiT02#'+Object.keys(JSON.parse(fs.readFileSync(R+'/apparatus/09DiT02.appk.json','utf8')))[0],'T'); }catch(e){}
    await wait(900);
    const d=w.document, g={};
    for(const id of IDS){ const e=d.getElementById(id); g['#'+id]=e?(e.getAttribute('data-tip')||e.getAttribute('title')):'(absent)'; }
    d.querySelectorAll('.lbtn').forEach(b=>{ g['.lbtn['+b.getAttribute('data-k')+']']=b.getAttribute('data-tip')||b.getAttribute('title'); });
    // tooltips built in JS live inside #scroll and were moved to data-tip by tipify()
    const pick=(sel)=>{const e=d.querySelector(sel);return e?(e.getAttribute('data-tip')||e.getAttribute('title')||''):'(none)';};
    g['copy-text']  = pick('#scroll button.icn[data-txt]');
    g['copy-cite']  = pick('#scroll button.icn[data-cite]');
    g['page-badge'] = pick('#scroll a.pgmk');
    g['xref-link']  = pick('#scroll a.xref');
    g['sigla-abbr'] = pick('#scroll .appx abbr');
    out[lang]=g; w.close();
  }
  const keys=Object.keys(out.en);
  let same=0,diff=0;
  const pad=(x,n)=>String(x==null?'':x).slice(0,n).padEnd(n);
  console.log(pad('control',18)+' '+pad('EN',46)+' ES');
  for(const k of keys){
    const a=out.en[k],b=out.es[k];
    if(a===b) same++; else diff++;
    console.log((a===b?'= ':'\u2713 ')+pad(k,18)+' '+pad(a,46)+' '+(b||''));
  }
  console.log('\n'+diff+' tooltip(s) change with the language, '+same+' identical');
})();

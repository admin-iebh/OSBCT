// Does the reader actually PUT THE BOLD ON THE PAGE?  jsdom over the shipped
// reader2.html and the shipped data -- not a Python model of it.
//
// `block()` has three branches and only the third calls `fmtBold`:
//     if(asSpine && vmap && vmap.groups){...}  else if(asSpine){...}
//     else body = fmtBold(pr.text, spans);
// `asSpine = kind==='canon' || !!(opts&&opts.spine)`, and the standalone-work
// view (`_work`) calls block(wk,key,{spine:true}).  If that reading is right,
// a commentary volume opened from the tree draws NO <b class="lemma"> at all,
// while the same volume drawn as a BAND under its canon volume draws them.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(f){
  const src=process.env.OSBCT_READER_PATH||(R+'/'+f);
  const dom=new JSDOM(fs.readFileSync(src,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f2=resolve(u);let t=null;try{t=fs.readFileSync(f2,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
(async()=>{
  const READER=process.env.OSBCT_READER||'reader2.html';
  const vol=process.argv[2]||'20KhuA01', key=process.argv[3]||(vol+'#377');
  const w=boot(READER);
  for(let k=0;k<80&&!w.openKey;k++) await wait(80);
  // --- 1. the volume opened as ITS OWN SPINE (what the tree gives a reader)
  try{ await w.openKey(key,'A'); }catch(e){ console.log('openKey err',e.message); }
  const scroll=()=>w.document.querySelector('#scroll');
  for(let k=0;k<40;k++){ await wait(80);
    if(scroll()&&scroll().querySelectorAll('.para').length>3) break; }
  try{ w.eval('render();'); }catch(e){}
  for(let k=0;k<40;k++){ await wait(80);
    if(scroll()&&scroll().querySelectorAll('.para').length>3) break; }
  let isWork=false; try{ isWork=!!w.eval('state.filter && !state.active.canon'); }catch(e){}
  const spineB=scroll()?scroll().querySelectorAll('b.lemma').length:-1;
  const spineP=scroll()?scroll().querySelectorAll('.para').length:-1;
  console.log('%s  SPINE view  (state.filter set: %s)  paragraphs=%d  <b class="lemma">=%d',
              vol, isWork, spineP, spineB);
  // --- 1b. the FILTERED WORK route: the work reached from the tree, drawn as
  // its own stream under a canon volume with the canon band off.  This is the
  // `_work` branch, and the one 690cfff8 changed.
  try{ w.eval('state.filter="'+vol+'";state.active={canon:false,A:true,T:false};render();'); }catch(e){console.log('work err',e.message);}
  for(let k=0;k<50;k++){ await wait(90); if(scroll()&&scroll().querySelectorAll('.para').length>3) break; }
  console.log('%s  WORK view (state.filter set)     paragraphs=%d  <b class="lemma">=%d',
              vol, scroll()?scroll().querySelectorAll('.para').length:-1,
              scroll()?scroll().querySelectorAll('b.lemma').length:-1);
  // --- 2. the same commentary under its CANON volume, with the A band on.
  // Opening the commentary directly makes it `state.canonVol` -- it IS the
  // spine -- so the band view has to be reached from the canon side.
  const canon=process.argv[4]||'18Khu01';
  try{ w.eval('state.filter=null;state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(canon+'#0','canon'); }catch(e){ console.log('canon open err',e.message); }
  for(let k=0;k<60;k++){ await wait(90);
    if(scroll()&&scroll().querySelectorAll('.para').length>3) break; }
  try{ w.eval('state.active={canon:true,A:true,T:false};render();'); }catch(e){console.log('band err',e.message);}
  for(let k=0;k<60;k++){ await wait(90);
    if(scroll()&&scroll().querySelectorAll('.para.l-A').length>0) break; }
  const bandB=scroll()?scroll().querySelectorAll('.para.l-A b.lemma').length:-1;
  const bandP=scroll()?scroll().querySelectorAll('.para.l-A').length:-1;
  console.log('%s under %s  BAND view   .para.l-A=%d  <b class="lemma"> inside them=%d',
              vol, canon, bandP, bandB);
  const s=scroll()?scroll().textContent:'';
  console.log('   sample bold drawn in band view:',
              [...(scroll()?scroll().querySelectorAll('b.lemma'):[])].slice(0,8).map(e=>e.textContent).join(' | '));
  process.exit(0);
})();

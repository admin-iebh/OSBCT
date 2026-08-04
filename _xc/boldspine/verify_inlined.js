// Bold drawn in BOTH views, over the SHIPPED reader with `i18n.js` and
// `panel.js` INLINED.  jsdom does not fetch `<script src>`; the fetch shim the
// other harnesses install covers `fetch()` only, so both files were silently
// absent and every claim made through them was made about a reader missing
// 122 KB of its own code.  Inlining is ASSERTED, not assumed: the run aborts if
// either tag is not replaced, if i18n did not run, or if panel.js did not run.
//
//   node _xc/boldspine/verify_inlined.js <READER.html> <VOL> <CANONHOST>
//
// Three routes are counted, because "the spine view" is two different code
// paths and only one of them is what 690cfff8 changed:
//   WORK  — the work reached from the tree: canon host open, canon band off,
//           state.filter set.  render()'s `_work` branch, block(...,{spine:true}).
//   SELF  — a volume opened as its own canon stream (kind==='canon'): the route
//           a volume with no canon counterpart takes.  block('canon',...).
//   BAND  — the same volume under its canon host with the A band on: the one
//           path that always drew bold, and the one that must not move.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlined(readerPath){
  let h=fs.readFileSync(readerPath,'utf8');
  const i18n=fs.readFileSync('site/i18n.js','utf8'), panel=fs.readFileSync(R+'/panel.js','utf8');
  let n=0;
  h=h.replace(/<script src="\.\.\/i18n\.js[^"]*"><\/script>/,()=>{n++;return '<script>'+i18n+'</script>';});
  h=h.replace(/<script src="panel\.js[^"]*"[^>]*><\/script>/,()=>{n++;return '<script>'+panel+'</script>';});
  if(n!==2) throw new Error('INLINING FAILED: replaced '+n+' of 2 <script src> tags');
  return h;
}
function boot(readerPath){
  const dom=new JSDOM(inlined(readerPath),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',
    beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
        // CONTROLS.  A check that cannot be made to fail on real input is not a
        // check.  Each of these disturbs the data the fix reads, on the wire, and
        // the run reports how many drawn bold runs moved.
        const C=process.env.CONTROL||'';
        if(C && t!=null && /\/bold\/[^/]+\.bold\.json$/.test(f)){
          let m=JSON.parse(t);
          if(C==='nobold') m={};
          else if(C==='shiftspans'){ for(const k in m) m[k]=m[k].map(a=>[a[0]+5,a[1]+5]); }
          else if(C==='halfspans'){ for(const k in m) m[k]=m[k].filter((_,i)=>i%2===0); }
          else if(C==='widenspans'){ for(const k in m) m[k]=m[k].map(a=>[a[0],a[1]+6]); }
          t=JSON.stringify(m);
        }
        if(C==='noverse' && t!=null && /\/verse\/[^/]+\.json$/.test(f)) t='{}';
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
const S=()=>0;
(async()=>{
  const readerPath=process.argv[2]||(R+'/reader2.html');
  const vol=process.argv[3]||'20KhuA01', canon=process.argv[4]||'18Khu01';
  const w=boot(readerPath);
  for(let k=0;k<80&&!w.openKey;k++) await wait(80);
  if(!w.openKey){ console.log('BOOT FAILED'); process.exit(2); }
  const haveI18n=(typeof w.t==='function')||(typeof w.T!=='undefined')||(typeof w.I18N!=='undefined');
  const havePanel=(typeof w.WL!=='undefined');
  console.log('INLINE  i18n ran='+haveI18n+'  panel ran='+havePanel);
  if(!haveI18n||!havePanel){ console.log('ASSERT FAILED: an inlined script did not run'); process.exit(3); }
  // Count over the DOCUMENT, not over `#scroll`.  With panel.js present the
  // rendered stream is not always inside the `#scroll` this harness first
  // grabbed -- a query against it returned 0 while the document held 1,871
  // paragraphs, which would have read as "nothing is drawn" and is exactly the
  // kind of false zero this file exists to avoid.
  const scroll=()=>w.document;
  const tally=(sel)=>{const s=scroll(); if(!s) return [-1,-1,-1];
    const ps=s.querySelectorAll(sel), bs=s.querySelectorAll(sel+' b.lemma');
    return [ps.length,bs.length,[...bs].reduce((a,e)=>a+e.textContent.length,0)];};
  const settle=async(sel,n)=>{for(let k=0;k<70;k++){await wait(90); if(scroll()&&scroll().querySelectorAll(sel).length>=n) return;}};
  // ---- ORDER MATTERS, and getting it wrong reads as "nothing is drawn".
  // The A band only renders once the commentary volume's cache and reverse map
  // are loaded, and that load is driven by `openKey`, not by `render()`.  With
  // the canon volume opened first the band came back EMPTY -- a false zero.
  try{ await w.openKey(vol+'#'+(process.argv[5]||'9'),'A'); }catch(e){ console.log('warm err',e.message); }
  await settle('.para',1);
  try{ w.eval('state.filter=null;state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(canon+'#0','canon'); }catch(e){ console.log('canon open err',e.message); }
  await settle('.para',4);
  // BAND — the path that always drew bold, and the one that must not move
  try{ w.eval('state.active={canon:true,A:true,T:false};render();'); }catch(e){console.log('band err',e.message);}
  await settle('.para.l-A',1);
  let b=tally('.para.l-A');
  console.log(vol+'  BAND under '+canon+'   paras='+b[0]+'  b.lemma='+b[1]+'  boldletters='+b[2]);
  console.log('   sample band bold: '+[...w.document.querySelectorAll('.para.l-A b.lemma')].slice(0,6).map(e=>e.textContent).join(' | '));
  // WORK — the standalone-work stream 690cfff8 added: block(wk,key,{spine:true})
  try{ w.eval('state.filter="'+vol+'";state.active={canon:false,A:true,T:false};render();'); }catch(e){console.log('work err',e.message);}
  await settle('.para',4);
  let a=tally('.para');
  const isWork=(()=>{try{return w.eval('!state.active.canon && !!state.filter && state.filter!==state.canonVol');}catch(e){return null;}})();
  console.log(vol+'  WORK-spine (_work branch='+isWork+')   paras='+a[0]+'  b.lemma='+a[1]+'  boldletters='+a[2]);
  console.log('   sample work bold: '+[...w.document.querySelectorAll('b.lemma')].slice(0,6).map(e=>e.textContent).join(' | '));
  // SELF — the volume drawn as its own canon stream (kind==='canon')
  try{ w.eval('state.filter=null;state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(vol+'#0','canon'); }catch(e){ console.log('self open err',e.message); }
  try{ w.eval('state.active={canon:true,A:false,T:false};render();'); }catch(e){console.log('self err',e.message);}
  await settle('.para',4);
  let c=tally('.para');
  console.log(vol+'  SELF-spine (own canon stream)   paras='+c[0]+'  b.lemma='+c[1]+'  boldletters='+c[2]);
  console.log('   sample self bold: '+[...w.document.querySelectorAll('b.lemma')].slice(0,6).map(e=>e.textContent).join(' | '));
  process.exit(0);
})();

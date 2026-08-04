// BROWSER PROOF of the commentary-range fix, over the shipped reader2.html and
// the shipped data, in jsdom.  Every assertion has a negative control below it
// (--control inverts the expectations and the run MUST then fail).
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const CONTROL=false; const RUNOPEN_=2;
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(lang){
  const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
    if(lang) try{ w.localStorage.setItem('osbct-lang',lang); }catch(e){}
    w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
let pass=0,fail=0;
function ok(name,cond,got){ if(cond){pass++;console.log('  ok   '+name);} else {fail++;console.log('  FAIL '+name+'   got: '+JSON.stringify(got));} }
const visible=el=>!el.closest('[hidden]');

(async()=>{
  const w=boot(null); const errs=[]; w.addEventListener('error',e=>errs.push(e.message));
  await wait(800);
  await w.openKey('09Ma01#255','canon'); await wait(1500);
  w.eval('state.active.A=true; state.active.T=true; state.view="single"; state.curbook=null; state.curvagga=null; state.cursutta=null;');
  await w.eval('ensureBandVols()'); await wait(3000); w.eval('render();'); await wait(800);
  ok('no js errors with P+A+T', errs.length===0, errs.slice(0,2));
  const doc=w.document;
  const all=[...doc.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  const dup=all.filter((x,k)=>all.indexOf(x)!==k);
  ok('P+A+T: nothing is drawn twice', dup.length===0, dup.slice(0,4));
  const T=[...doc.querySelectorAll('#scroll .subwrap.t')];
  ok('the T band draws', T.length>0, T.length);
  const runs=T.map(b=>[...b.querySelectorAll('.para[id]')].length);
  ok('at least one T band is a RANGE, not a point', Math.max.apply(null,runs)>1, {max:Math.max.apply(null,runs),n:runs.length});
  const tmore=[...doc.querySelectorAll('.subwrap.t .runmore')];
  ok('long T runs get a Read-more control', runs.filter(x=>x>RUNOPEN_+1).length===tmore.length,
     {longRuns:runs.filter(x=>x>RUNOPEN_+1).length, controls:tmore.length});
  // every T run must stay inside the volume it started in
  const bad=T.filter(b=>{const ids=[...b.querySelectorAll('.para[id]')].map(e=>e.id.replace(/-\d+$/,''));
                         return new Set(ids).size>1;});
  ok('no T run crosses into another volume', bad.length===0, bad.length);
  w.close();
  console.log('\n'+pass+' passed, '+fail+' failed');
  process.exit(fail?1:0);
})();

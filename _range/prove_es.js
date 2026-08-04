// BROWSER PROOF of the commentary-range fix, over the shipped reader2.html and
// the shipped data, in jsdom.  Every assertion has a negative control below it
// (--control inverts the expectations and the run MUST then fail).
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const CONTROL=process.argv.includes('--control');
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
  // ---------- Spanish ----------
  // jsdom does not fetch <script src>, so i18n.js — which the page really does
  // load (reader2.html:270) — is injected here.  Without it TIP() answers from
  // its English fallback and the Spanish string is never exercised at all: an
  // assertion satisfied by absence.
  const w3=boot(null); await wait(800);
  w3.eval(fs.readFileSync('site/i18n.js','utf8'));
  ok('i18n.js carries both strings', !!(w3.I18N.run_more&&w3.I18N.run_more.es&&w3.I18N.run_less&&w3.I18N.run_less.es),
     w3.I18N.run_more);
  await w3.openKey('18Khu01#0','canon'); await wait(1200);
  w3.eval('state.active.A=true; state.view="single"; state.curbook=null; state.curvagga=null;');
  await w3.eval('ensureBandVols()'); await wait(2500); w3.eval('render();'); await wait(600);
  const bEN=w3.document.getElementById('p-18Khu01-0').parentElement.querySelector('.subwrap.a button.runmore');
  ok('en: the control comes from i18n.js, not the fallback',
     !!bEN && bEN.textContent===w3.I18N.run_more.en.replace('%s','17'), bEN&&bEN.textContent);
  w3.localStorage.setItem('osbct-lang','es');
  ok('the page now reports Spanish', w3.osbctLang()==='es', w3.eval('osbctLang()'));
  w3.eval('render();'); await wait(600);
  const b3=w3.document.getElementById('p-18Khu01-0').parentElement.querySelector('.subwrap.a button.runmore');
  ok('es: the control is Spanish', !!b3 && /^Leer más — 17 párrafos más/.test(b3.textContent), b3&&b3.textContent);
  b3.dispatchEvent(new w3.Event('click',{bubbles:true})); await wait(120);
  ok('es: expanding relabels in Spanish', b3.textContent==='Mostrar menos', b3.textContent);
  w3.close();

  console.log('\n'+pass+' passed, '+fail+' failed'+(CONTROL?'   [CONTROL RUN]':''));
  process.exit(fail?1:0);
})();

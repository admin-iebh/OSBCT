const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){
  const dom=new JSDOM(fs.readFileSync(R+'/'+(process.env.OSBCT_READER||'reader2.html'),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
(async()=>{
  const w=boot(); let err=[]; w.addEventListener('error',e=>err.push(e.message));
  await wait(800);
  try{ await w.openKey('18Khu01#0','canon'); }catch(e){ console.log('openKey err',e.message); }
  await wait(1500);
  try{ w.eval('state.active.A=true; state.view="single"; state.curbook=null; state.curvagga=null;'); }catch(e){ console.log('eval err',e.message); }
  try{ await w.eval('ensureBandVols()'); }catch(e){ console.log('ebv err',e.message); }
  await wait(2500);
  try{ w.eval('render();'); }catch(e){ console.log('render err',e.message); }
  await wait(800);
  const doc=w.document;
  const seq=[...doc.querySelectorAll('#scroll .para')].map(p=>p.id);
  console.log('JSERR', JSON.stringify(err.slice(0,3)));
  console.log('total .para drawn:', seq.length);
  console.log('first 40 of stream:', JSON.stringify(seq.slice(0,40)));
  const tf=w.eval('JSON.stringify([0,1,2,6,11,12,24,35,52,63,79,88].map(i=>[i,targetsFor(i,"A").map(t=>t.key)]))');
  console.log('targetsFor:', tf);
  w.close();
})();

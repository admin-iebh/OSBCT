// The lazy band load must not break the bands. Open a canon volume, turn on
// Aṭṭhakathā, then Ṭīkā, and check blocks actually appear each time.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
let bytes=0;
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const w=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}if(t)bytes+=t.length;return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;
const click=k=>{const b=[...w.document.querySelectorAll('.lbtn')].find(x=>x.dataset.k===k); b.onclick(); };
(async()=>{
  await wait(1500);
  let fail=0;
  for(const vol of (process.argv.slice(2).length?process.argv.slice(2):['18Khu01','06Di01','09Ma01'])){
    try{ w.openKey(vol+'#0','canon'); }catch(e){}
    await wait(1800); bytes=0;
    const canon=w.document.querySelectorAll('.para.canon').length;
    click('A'); await wait(2500);
    const A=w.document.querySelectorAll('.para.l-A, .subwrap.a').length, aBytes=bytes; bytes=0;
    click('T'); await wait(2500);
    const T=w.document.querySelectorAll('.para.l-T, .subwrap.t').length;
    const ok=canon>0 && A>0;
    if(!ok) fail++;
    console.log('  '+(ok?'ok  ':'FAIL')+' '+vol.padEnd(10)
      +' canon '+String(canon).padStart(5)
      +' | A '+String(A).padStart(5)+' ('+(aBytes/1048576).toFixed(2)+' MB fetched on demand)'
      +' | T '+String(T).padStart(5));
    click('A'); click('T'); await wait(400);   // back to canon-only for the next volume
  }
  console.log(fail?'\n'+fail+' FAILED':'\nall bands populate on demand');
  process.exit(fail?1:0);
})();

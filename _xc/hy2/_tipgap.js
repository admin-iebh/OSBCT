const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
(async()=>{const w=boot();
 for(let k=0;k<80;k++){await wait(100); if(w.document.querySelectorAll('.row').length>3) break;}
 for(const vol of ['21Khu04','19Khu02','31KhuA12','32KhuA13','29KhuA10','09DiT02','25VsmT01']){
  await w.eval('openKey')(vol+'#0','canon');
  for(let k=0;k<60;k++){await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break;}
  const c=(w.eval('cache')||{})[vol]||{};
  w.document.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
    const o=+x.id.slice(('p-'+vol+'-').length);
    const app=(c.app||{})[String(o)]||[]; if(!app.length) return;
    const notes=new Set(app.map(n=>String(n&&n.n)));
    x.querySelectorAll('sup.fnm').forEach(s=>{ if(s.closest('.appx')) return;
      if(!notes.has(s.textContent)) return;
      if(s.getAttribute('title')||s.getAttribute('data-tip')) return;
      const same=app.filter(n=>String(n.n)===s.textContent);
      console.log(`${vol} ord ${o} digit ${s.textContent}: ${same.length} note(s) with that n; bodies=`+JSON.stringify(same.map(n=>(n.variants||[]).length?'variants':(n.text||'(empty)'))));
    });
  });
 }
 process.exit(0);})();

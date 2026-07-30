const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
(async()=>{await new Promise(r=>setTimeout(r,1000));const rows=()=>[...w.document.querySelectorAll('.row')];
rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,180));
const sn=rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi');sn.click();await new Promise(r=>setTimeout(r,180));
[...sn.parentElement.querySelectorAll('.row')].find(r=>r.textContent.trim()==='3. Mahāvagga')?.click();
await new Promise(r=>setTimeout(r,500));
console.log('JS error:',err||'none');
const p=w.document.querySelector('#p-18Khu01-1435');
if(p){const af=p.querySelector('.gatha-after');
console.log('v738 verse has NO false count:',p.querySelectorAll('.gatha-count').length===0);
console.log('v738 prose present & starts "(5)":',af?/^\(5\)/.test(af.textContent.trim()):'no prose');
console.log('v738 prose renders as prose not verse:',af&&!p.querySelector('.gatha').textContent.includes('bhikkhave'));}
})();

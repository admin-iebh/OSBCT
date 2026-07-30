const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
(async()=>{await new Promise(r=>setTimeout(r,900));const rows=()=>[...w.document.querySelectorAll('.row')];
console.log('JS error:',err||'none');
rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,150));
const it=rows().find(r=>r.textContent.trim()==='Itivuttakapāḷi');it?.click();await new Promise(r=>setTimeout(r,120));
// nipata rows should now be visible under Itivuttaka
const kids=it.parentElement.querySelectorAll(':scope > .kids > .wrap > .row, :scope > .kids > .row');
const nipRows=[...it.parentElement.querySelectorAll('.row')].map(r=>r.textContent.trim()).filter(t=>/nipāta/.test(t));
console.log('nipāta rows under Itivuttaka:',nipRows);
// expand Ekakanipāta, check its vaggas
const eka=[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim()==='1. Ekakanipāta');
eka?.click();await new Promise(r=>setTimeout(r,120));
const ekaVaggas=[...eka.parentElement.querySelectorAll('.row')].map(r=>r.textContent.trim()).filter(t=>/vagga/.test(t));
console.log('Ekaka vaggas:',ekaVaggas);
// click Dutiyavagga of Ekaka (ord603) -> should open Itivuttaka slice at that vagga
const dv=[...eka.parentElement.querySelectorAll('.row')].find(r=>r.textContent.trim()==='2. Dutiyavagga');
dv?.click();
for(let k=0;k<70;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>800)break;await new Promise(r=>setTimeout(r,100));}
const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
console.log('opened & Itivuttaka only (Dhammapada excluded):',!txt.includes('Manopubbaṅgamā'),'| Udāna excluded:',!txt.includes('Yadā have pātubhavanti'));
console.log('title shows vagga:',((w.document.querySelector('#doctitle')||{}).textContent||'').slice(0,26));
// Catukka is a leaf (no expand chev children)
const cat=[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim()==='4. Catukkanipāta');
console.log('Catukka is leaf row present:',!!cat);
})();

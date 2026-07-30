const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
(async()=>{await new Promise(r=>setTimeout(r,900));const rows=()=>[...w.document.querySelectorAll('.row')];
rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,150));
const sn=rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi');sn?.click();await new Promise(r=>setTimeout(r,130));
[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim()==='1. Uragavagga')?.click();await new Promise(r=>setTimeout(r,120));
[...w.document.querySelectorAll('.row')].find(r=>/4\. Kasibhāradvājasutta/.test(r.textContent))?.click();
for(let k=0;k<80;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>800)break;await new Promise(r=>setTimeout(r,100));}
const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
console.log('JS error:',err||'none');
console.log('Kasi intro prose present (Ekanāḷāyaṁ):',txt.includes('Ekanāḷāyaṁ brāhmaṇagāme'));
console.log('intro before verse 76 (Kassako paṭijānāsi):',txt.indexOf('Ekanāḷāyaṁ')<txt.indexOf('Kassako paṭijānāsi'));
console.log('mixed split: prose blocks (.gatha-after):',[...w.document.querySelectorAll('#scroll .gatha-after')].length);
console.log('closing prose (Atha kho Kasibhāradvājo) in a gatha-after:',[...w.document.querySelectorAll('#scroll .gatha-after')].some(e=>/Atha kho Kasibhāradvājo/.test(e.textContent)));
console.log('verse-count (5) still shows:',[...w.document.querySelectorAll('#scroll .gatha-count')].some(e=>e.textContent==='(5)'));
console.log('sutta-end Kasibhāradvājasuttaṁ catutthaṁ.:',txt.includes('Kasibhāradvājasuttaṁ catutthaṁ.'));
})();

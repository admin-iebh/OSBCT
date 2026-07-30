const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;
(async()=>{await new Promise(r=>setTimeout(r,900));const rows=()=>[...w.document.querySelectorAll('.row')];
rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,150));
rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi')?.click();await new Promise(r=>setTimeout(r,130));
[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim()==='4. Aṭṭhakavagga')?.click();
for(let k=0;k<80;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>800)break;await new Promise(r=>setTimeout(r,100));}
const p=w.document.querySelector('#p-18Khu01-1662');
if(p){const g=p.querySelectorAll('.gatha');
console.log('Sāriputta ord1662 verse blocks:',g.length,'| counts:',[...p.querySelectorAll('.gatha-count')].map(x=>x.textContent.trim()));
console.log('  2nd verse is verse not prose (Pañcanaṁ dhīro in a .gatha):',[...g].some(x=>/Pañcanaṁ dhīro/.test(x.textContent)));}
})();

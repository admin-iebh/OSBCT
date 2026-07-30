const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.getComputedStyle=()=>({});w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
(async()=>{await new Promise(r=>setTimeout(r,900));const rows=()=>[...w.document.querySelectorAll('.row')];
rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,150));
rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi')?.click();await new Promise(r=>setTimeout(r,130));
[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim()==='3. Mahāvagga')?.click();
for(let k=0;k<80;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>800)break;await new Promise(r=>setTimeout(r,100));}
console.log('JS error:',err||'none');
const heads=[...w.document.querySelectorAll('#scroll .head.section')].map(h=>h.textContent);
console.log('Mahā sutta heads:',heads.length,'(expect 12)');
console.log('  4. Pūraḷāsa (Sundarikabhāradvāja) sutta present:',heads.some(h=>/Pūraḷāsa/.test(h)));
// Sundarika heading at v457 (ord for 457); check it precedes multiple verses before v490
const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
const iSund=txt.indexOf('Pūraḷāsa');const iV490=txt.indexOf('Buddho bhavaṁ arahati pūraḷāsaṁ');
console.log('  Sundarika heading BEFORE its v490 verse (spans many verses):', iSund>0&&iSund<iV490);
console.log('  Subhāsitasuttaṁ tatiyaṁ colophon present (ends Subhāsita correctly):',txt.includes('Subhāsitasuttaṁ tatiyaṁ.'));
console.log('  Subhāsita colophon comes BEFORE Sundarika heading:',txt.indexOf('Subhāsitasuttaṁ tatiyaṁ.')<iSund);
// italic number check: .gatha .pn font-style
const st=[...w.document.querySelectorAll('#scroll .gatha .pn')];
console.log('numbers inside .gatha (styled non-italic via css):',st.length,'e.g.',st[0]?st[0].textContent:'none');
// Cūḷa 14 + Kapila
})();

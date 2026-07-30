const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const R='site/reader';
const resolve=(u)=>{u=String(u).split('?')[0];
  if(u.startsWith('../'))return path.join('site',u.slice(3));
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}
  return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',
  beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
    w.fetch=(u)=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
      return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
(async()=>{ await new Promise(r=>setTimeout(r,900));
  const rows=()=>[...w.document.querySelectorAll('.row')];
  rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click();await new Promise(r=>setTimeout(r,140));
  const ud=rows().find(r=>r.textContent.trim().startsWith('Udānapāḷi'));ud?.click();await new Promise(r=>setTimeout(r,140));
  const vr=[...(ud.parentElement.querySelectorAll('.row'))].find(r=>/Bodhivagga/.test(r.textContent));
  console.log('Bodhivagga row in tree:',!!vr); vr?.click();
  for(let k=0;k<70;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>600)break;await new Promise(r=>setTimeout(r,100));}
  const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
  const heads=[...w.document.querySelectorAll('#scroll .head')].map(h=>h.textContent);
  console.log('JS error:',err||'none');
  console.log('title:',((w.document.querySelector('#doctitle')||{}).textContent||'').slice(0,34));
  console.log('vagga heads:',heads.filter(h=>/vagga$/.test(h)).length,'/8 |',heads.filter(h=>/vagga$/.test(h)));
  console.log('1. Bodhivagga:',heads.includes('1. Bodhivagga'),'| 1. Paṭhamabodhisutta:',heads.includes('1. Paṭhamabodhisutta'),'| 10. Bāhiyasutta:',heads.includes('10. Bāhiyasutta'));
  console.log('colophons:',['Bodhivaggo paṭhamo.','Soṇavaggo pañcamo.','Pāṭaligāmiyavaggo aṭṭhamo.'].filter(c=>txt.includes(c)).length,'/3');
  console.log('Tassuddānaṁ labels:',[...w.document.querySelectorAll("#scroll .udd-label")].filter(x=>/Tassuddān/.test(x.textContent)).length);
  console.log('Udāne vaggānamuddānaṁ:',txt.includes('Vaggamidaṁ paṭhamaṁ varabodhi'),'| ends Udānapāḷi niṭṭhitā.:',txt.includes('Udānapāḷi niṭṭhitā.'));
  console.log('Dhammapada excluded:',!txt.includes('Manopubbaṅgamā'),'| Itivuttaka excluded:',!txt.includes('vuttañhetaṁ')&&!txt.includes('Vuttañhetaṁ'));
})();

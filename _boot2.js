const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const R='site/reader';
const resolve=(u)=>{ u=String(u).split('?')[0];
  if(u.startsWith('../')) return path.join('site',u.slice(3));
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}
  return path.join(R,u); };
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',
  beforeParse(w){ w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
    w.fetch=(u)=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
      return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;
(async()=>{ await new Promise(r=>setTimeout(r,800));
  const clk=t=>{const el=[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim().startsWith(t));if(el)el.click();};
  clk('Khuddakanikāya');await new Promise(r=>setTimeout(r,120));clk('Khuddakapāṭhapāḷi');await new Promise(r=>setTimeout(r,120));
  const c=[...w.document.querySelectorAll('.row .lbl')].find(e=>/Saraṇattaya/.test(e.textContent)); if(c)c.closest('.row').click();
  for(let k=0;k<50;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>300)break;await new Promise(r=>setTimeout(r,100));}
  const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
  const need=['Saraṇattayaṁ','Dasasikkhāpadaṁ','Dvattiṁsākāraṁ','Maṅgalasuttaṁ','Ratanasuttaṁ','Tirokuṭṭasuttaṁ','Nidhikaṇḍasuttaṁ','Mettasuttaṁ'];
  console.log('build ok · colophons',need.filter(n=>txt.includes(n)).length+'/8','· v8',txt.includes('Yathā vārivahā pūrā'),'· v12',txt.includes('Kiñcāpi so kamma'),'· Dhp excluded',!txt.includes('Manopubbaṅgamā'),'· ends with niṭṭhitā',txt.trimEnd().endsWith('niṭṭhitā.'));
})();

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
const w=dom.window;
(async()=>{ await new Promise(r=>setTimeout(r,900));
  const clk=t=>{const el=[...w.document.querySelectorAll('.row')].find(r=>r.textContent.trim().startsWith(t));if(el)el.click();};
  clk('Khuddakanikāya');await new Promise(r=>setTimeout(r,140));clk('Dhammapadapāḷi');await new Promise(r=>setTimeout(r,140));
  const c=[...w.document.querySelectorAll('.row .lbl')].find(e=>/Yamakavagga/.test(e.textContent)); if(c)c.closest('.row').click();
  else { // no vagga in tree? click a chapter row under Dhammapada
    const any=[...w.document.querySelectorAll('.row .lbl')].find(e=>/vagga/i.test(e.textContent)); if(any)any.closest('.row').click(); }
  for(let k=0;k<60;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>500)break;await new Promise(r=>setTimeout(r,100));}
  const s=w.document.querySelector('#scroll');const txt=s?s.textContent:'';
  const heads=[...w.document.querySelectorAll('#scroll .head')].map(h=>h.textContent);
  const vaggaHeads=heads.filter(h=>/vagga$/.test(h.replace(/\d+\.\s*/,'')));
  console.log('vagga headings shown:',vaggaHeads.length,'| first/last:',vaggaHeads[0],'/',vaggaHeads[vaggaHeads.length-1]);
  console.log('vatthu "1. Cakkhupālattheravatthu":',heads.includes('1. Cakkhupālattheravatthu'));
  console.log('vatthu "2. Maṭṭhakuṇḍalīvatthu":',heads.includes('2. Maṭṭhakuṇḍalīvatthu'));
  console.log('verse 24 restored:',txt.includes('Uṭṭhānavato satīmato'),'| its vatthu head:',heads.includes('2. Kumbhaghosakaseṭṭhivatthu'));
  console.log('verse 52 restored:',txt.includes('vaṇṇavantaṁ sagandhakaṁ'));
  const colo=['Yamakavaggo paṭhamo.','Appamādavaggo dutiyo.','Brāhmaṇavaggo chabbīsatimo.','Dhammapadapāḷi niṭṭhitā.'];
  console.log('colophons:',colo.filter(x=>txt.includes(x)).length+'/'+colo.length, colo.filter(x=>!txt.includes(x)).length?'MISSING '+colo.filter(x=>!txt.includes(x)):'✓');
  console.log('leaked hidden (no standalone "Visākhāya sahāyikānaṁ vatthu" para):', !heads.some(h=>/^1\. Visākhāya/.test(h))? 'as-heading-only':'check', '| Visākhāya as heading:',heads.includes('1. Visākhāya sahāyikānaṁ vatthu'));
  console.log('Khuddakapāṭha excluded:',!txt.includes('Buddhaṁ saraṇaṁ gacchāmi'),'| Udāna excluded:',!txt.includes('Bodhivagga'));
  console.log('title:',((w.document.querySelector('#doctitle')||{}).textContent||'').slice(0,40));
})();

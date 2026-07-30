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
const w=dom.window; let jserr=null; w.addEventListener('error',e=>jserr=e.message);
(async()=>{ await new Promise(r=>setTimeout(r,900));
  // expand Khuddakanikāya, then Dhammapadapāḷi, then click its Yamakavagga child
  const rows=()=>[...w.document.querySelectorAll('.row')];
  rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click(); await new Promise(r=>setTimeout(r,120));
  const dhpRow=rows().find(r=>r.textContent.trim().startsWith('Dhammapadapāḷi'));
  dhpRow?.click(); await new Promise(r=>setTimeout(r,120));
  // vagga rows are siblings inside dhp wrap
  const wrap=dhpRow?.parentElement;
  const vaggaRow=[...(wrap?wrap.querySelectorAll('.row'):[])].find(r=>/Yamakavagga/.test(r.textContent));
  vaggaRow?.click();
  for(let k=0;k<60;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>600)break;await new Promise(r=>setTimeout(r,100));}
  const s=w.document.querySelector('#scroll');const txt=s?s.textContent:'';
  const heads=[...w.document.querySelectorAll('#scroll .head')].map(h=>h.textContent);
  console.log('JS error:',jserr||'none');
  console.log('title:',((w.document.querySelector('#doctitle')||{}).textContent||'').slice(0,40));
  console.log('vagga heads in DOM:',heads.filter(h=>/vagga$/.test(h)).length);
  console.log('1. Yamakavagga:',heads.includes('1. Yamakavagga'),'| 1. Cakkhupālattheravatthu:',heads.includes('1. Cakkhupālattheravatthu'));
  console.log('verse24:',txt.includes('Uṭṭhānavato satīmato'),'| Kumbhaghosaka head:',heads.includes('2. Kumbhaghosakaseṭṭhivatthu'),'| verse52:',txt.includes('vaṇṇavantaṁ sagandhakaṁ'));
  console.log('Yamakavaggo paṭhamo.:',txt.includes('Yamakavaggo paṭhamo.'),'| book-end niṭṭhitā:',txt.includes('Dhammapadapāḷi niṭṭhitā.'));
  console.log('leaked Visākhāya as heading:',heads.includes('1. Visākhāya sahāyikānaṁ vatthu'),'| Khuddakapāṭha excluded:',!txt.includes('Buddhaṁ saraṇaṁ gacchāmi'));
})();

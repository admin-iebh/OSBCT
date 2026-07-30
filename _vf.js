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
  // open Mucalindavagga (contains Upāsakasutta ord527 & Ekaputtakasutta ord529)
  const ud=rows().find(r=>r.textContent.trim().startsWith('Udānapāḷi'));ud?.click();await new Promise(r=>setTimeout(r,140));
  [...(ud.parentElement.querySelectorAll('.row'))].find(r=>/Mucalindavagga/.test(r.textContent))?.click();
  for(let k=0;k<70;k++){const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>600)break;await new Promise(r=>setTimeout(r,100));}
  console.log('JS error:',err||'none');
  const txt=(w.document.querySelector('#scroll')||{}).textContent||'';
  console.log('ord527 dropped line now present (Saṅkhātadhammassa):',txt.includes('Saṅkhātadhammassa bahussutassa'));
  // ord529 two gatha blocks
  const gd=[...w.document.querySelectorAll('#scroll .gatha')];
  console.log('gatha blocks in Mucalindavagga:',gd.length);
  // find the para with Ekaputta verse -> should have 2 .gatha siblings
  const eka=[...w.document.querySelectorAll('#scroll .para.canon')].find(p=>/Piyarūpassādagadhitāse/.test(p.textContent));
  console.log('Ekaputtaka has 2 gatha blocks:', eka? eka.querySelectorAll('.gatha').length : 'not found');
})();

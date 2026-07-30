// Does the title actually RENDER, for one volume of each nav shape?
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
let pass=0,fail=0;const A=(o,m)=>{o?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<80;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
// pdftoc / nested / nipata / tree — one of each
const CASES=[['Pārājikapāḷi','Pārājikapāḷi','Vinayapiṭaka'],
             ['Sīlakkhandhavaggapāḷi','Sīlakkhandhavaggapāḷi','Dīghanikāya'],
             ['Mūlapaṇṇāsapāḷi','Mūlapaṇṇāsapāḷi','Majjhimanikāya'],
             ['Ekakanipātapāḷi','Ekakanipātapāḷi','Aṅguttaranikāya'],
             ['Sagāthāvaggasaṁyuttapāḷi','Sagāthāvaggasaṁyuttapāḷi','Saṁyuttanikāya'],
             ['Dhammasaṅgaṇīpāḷi','Dhammasaṅgaṇīpāḷi','Abhidhammapiṭaka']];
(async()=>{
  const w=boot(); await ready(w);
  for(const r of [...w.document.querySelectorAll('.row')]) if(['Pāḷi','Vinayapiṭaka','Dīghanikāya','Majjhimanikāya','Saṁyuttanikāya','Aṅguttaranikāya','Abhidhammapiṭaka'].includes(lbl(r))) { r.click(); await wait(40); }
  for(const [row,title,series] of CASES){
    const r=find(w,row); A(!!r,'no nav row for '+row); if(!r) continue;
    r.click();
    for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1200)break;}
    const bt=w.document.querySelector('#scroll .head.booktitle');
    A(!!bt && bt.textContent.trim()===title, row+': title not rendered, got '+(bt?bt.textContent.trim():'none'));
    const sr=w.document.querySelector('#scroll .head.bookseries');
    A(!!sr && sr.textContent.trim()===series, row+': expected series line "'+series+'", got '+(sr?sr.textContent.trim():'none'));
  }
  console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail?1:0);
})();

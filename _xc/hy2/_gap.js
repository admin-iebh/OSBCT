const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const MARK=/[a-zāīūṁṅñṭḍṇḷ](\d{1,2})(?!\d)/g;
(async()=>{const w=boot();
 for(let k=0;k<80;k++){await wait(100); if(w.document.querySelectorAll('.row').length>3) break;}
 for(const vol of ['19Khu02','09DiT02']){
  await w.eval('openKey')(vol+'#0','canon');
  for(let k=0;k<60;k++){await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break;}
  const c=(w.eval('cache')||{})[vol]||{}; const P=c.paras||[]; const V=c.verse||{};
  let rows=[];
  w.document.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
    const o=+x.id.slice(('p-'+vol+'-').length); const p=P[o]; if(!p) return;
    const t=String(p.text||'').replace(/^\s*\d+(-\d+)?\.\s*/,'');
    MARK.lastIndex=0; const exp=(t.match(MARK)||[]).length;
    let sup=0; x.querySelectorAll('sup.fnm').forEach(s=>{ if(!s.closest('.appx')) sup++; });
    if(sup!==exp) rows.push({o,exp,sup,pg:p.printed,verse:!!V[String(o)],bold:((c.bold||{})[String(o)]||[]).length});
  });
  console.log(vol+': '+rows.length+' paragraphs disagree');
  rows.slice(0,15).forEach(r=>console.log(`   ord ${r.o} p.${r.pg} verse=${r.verse} boldspans=${r.bold}  text ${r.exp}, page ${r.sup}`));
 }
 process.exit(0);})();

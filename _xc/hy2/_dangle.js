const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
(async()=>{const w=boot();
 for(let k=0;k<80;k++){await wait(100); if(w.document.querySelectorAll('.row').length>3) break;}
 let bad=0,seen=0;
 for(const vol of process.argv.slice(2)){
  await w.eval('openKey')(vol+'#0','canon');
  for(let k=0;k<60;k++){await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break;}
  w.document.querySelectorAll('#scroll .pgrule').forEach(r=>{
    // the text immediately above this rule
    let n=r.previousSibling, t='';
    while(n && t.length<8){ t=(n.textContent||'')+t; n=n.previousSibling; }
    t=t.replace(/\s+$/,''); if(!t) return; seen++;
    if('“‘(«'.indexOf(t[t.length-1])>=0){ bad++; if(bad<6) console.log('   '+vol+': page closes on '+JSON.stringify(t.slice(-24))); }
  });
 }
 console.log(`${seen} page rules examined, ${bad} closing on a dangling opening mark`);
 process.exit(bad?1:0);})();

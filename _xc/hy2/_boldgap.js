const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
(async()=>{const w=boot();
 for(let k=0;k<80;k++){await wait(100); if(w.document.querySelectorAll('.row').length>3) break;}
 for(const vol of (process.argv.slice(2).length?process.argv.slice(2):['31KhuA12','32KhuA13','09DiT02','25VsmT01','29KhuA10'])){
  await w.eval('openKey')(vol+'#0','canon');
  for(let k=0;k<60;k++){await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break;}
  const c=(w.eval('cache')||{})[vol]||{}; const P=c.paras||[]; const Bd=c.bold||{}; const V=c.verse||{};
  let want=0,got=0, wantV=0,gotV=0, ex=[];
  w.document.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
    const o=+x.id.slice(('p-'+vol+'-').length); const p=P[o]; if(!p) return;
    const n=(Bd[String(o)]||[]).length; if(!n) return;
    const drew=x.querySelectorAll('b.lemma').length;
    const isV=!!V[String(o)];
    want+=n; got+=drew; if(isV){wantV+=n; gotV+=drew;}
    if(drew<n && ex.length<6) ex.push(`ord ${o} p.${p.printed} verse=${isV}: data ${n}, drawn ${drew}`);
  });
  console.log(`${vol}: bold spans in data ${want}, <b class="lemma"> drawn ${got}  (${(100*got/Math.max(1,want)).toFixed(1)}%)`);
  console.log(`   on ordinals with a verse map: data ${wantV}, drawn ${gotV}  (${(100*gotV/Math.max(1,wantV)).toFixed(1)}%)`);
  ex.forEach(e=>console.log('      '+e));
 }
 process.exit(0);})();

// Does the section name written into 27KhuA08 reach what a READER sees?
// The `sutta` field feeds the citation and the title bar; the ☰ Contents is
// built from `site/reader/sections/`, which is a SEPARATE artefact.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(h){return h.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{let t=null;try{t=fs.readFileSync(resolve(u),'utf8');}catch(e){}return t==null?m:'<script>'+t+'</script>';});}
const dom=new JSDOM(inlineScripts(fs.readFileSync(R+'/reader2.html','utf8')),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;
(async()=>{
  await wait(1500);
  try{ await w.openKey('27KhuA08#244','A'); }catch(e){ console.log('open:',e.message); }
  for(let k=0;k<80;k++){ await wait(90); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
  const el=w.document.querySelector('#p-27KhuA08-244');
  console.log('paragraph 244 rendered:', !!el);
  if(el){ const b=[...el.querySelectorAll('[data-cite]')].map(x=>x.getAttribute('data-cite'));
    console.log('citation offered:', JSON.stringify(b)); }
  const el2=w.document.querySelector('#p-27KhuA08-362');
  if(el2){ console.log('¶362 citation:', JSON.stringify([...el2.querySelectorAll('[data-cite]')].map(x=>x.getAttribute('data-cite')))); }
  process.exit(0);
})();

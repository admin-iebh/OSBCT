// The branch test, run on the SHIPPED reader with the SHIPPED data: call
// `block()` on the same paragraph twice, once as a band block and once with
// {spine:true}, and count the <b class="lemma"> each returns.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const src=process.env.OSBCT_READER_PATH||(R+'/reader2.html');
  return new JSDOM(fs.readFileSync(src,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;}
const N=h=>(String(h).match(/<b class="lemma">/g)||[]).length;
(async()=>{
  const canon=process.argv[2]||'18Khu01', key=process.argv[3]||'20KhuA01#377';
  const w=boot(); for(let k=0;k<80&&!w.openKey;k++) await wait(80);
  try{ await w.openKey(canon+'#0','canon'); }catch(e){}
  for(let k=0;k<60;k++){ await wait(90); const s=w.document.querySelector('#scroll'); if(s&&s.querySelectorAll('.para').length>3) break; }
  try{ w.eval('state.active={canon:true,A:true,T:false};render();'); }catch(e){}
  for(let k=0;k<60;k++){ await wait(90); const s=w.document.querySelector('#scroll'); if(s&&s.querySelectorAll('.para.l-A').length>0) break; }
  const q=e=>{try{return w.eval(e);}catch(x){return 'ERR '+x.message;}};
  const band=q("block('A','"+key+"')");
  const spine=q("block('A','"+key+"',{spine:true})");
  console.log('  block(A,%s)              lemma tags = %s', key, typeof band==='string'?N(band):band);
  console.log('  block(A,%s,{spine:true}) lemma tags = %s', key, typeof spine==='string'?N(spine):spine);
  process.exit(0);
})();

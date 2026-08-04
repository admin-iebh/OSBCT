// The same volume, the same data, two views of the shipped reader:
//   (a) hanging under its canon volume as an A band
//   (b) opened directly, so it is `state.canonVol` and therefore `asSpine`
// Counting <b class="lemma"> in each.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const src=process.env.OSBCT_READER_PATH||(R+'/reader2.html');
  return new JSDOM(fs.readFileSync(src,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;}
(async()=>{
  const canon=process.argv[2]||'18Khu01', vol=process.argv[3]||'20KhuA01';
  const w=boot(); for(let k=0;k<80&&!w.openKey;k++) await wait(80);
  const S=()=>w.document.querySelector('#scroll');
  const cnt=()=>[S()?S().querySelectorAll('.para').length:-1, S()?S().querySelectorAll('b.lemma').length:-1];
  try{ await w.openKey(canon+'#0','canon'); }catch(e){}
  for(let k=0;k<60;k++){ await wait(90); if(S()&&S().querySelectorAll('.para').length>3) break; }
  try{ w.eval('state.active={canon:true,A:true,T:false};render();'); }catch(e){}
  for(let k=0;k<60;k++){ await wait(90); if(S()&&S().querySelectorAll('.para.l-A').length>0) break; }
  let c=cnt(); console.log('  BAND   %s under %s : paras=%d  b.lemma=%d  (l-A paras %d)',
      vol,canon,c[0],S().querySelectorAll('.para.l-A b.lemma').length? c[0]:c[0], S().querySelectorAll('.para.l-A').length);
  console.log('         b.lemma inside .para.l-A = %d', S().querySelectorAll('.para.l-A b.lemma').length);
  try{ w.eval('state.canonVol="'+vol+'";state.filter=null;state.curbook=null;state.curvagga=null;state.cursutta=null;state.active={canon:true,A:true,T:false};render();'); }catch(e){console.log('  err',e.message);}
  for(let k=0;k<60;k++){ await wait(90); if(S()&&S().querySelectorAll('.para').length>3) break; }
  c=cnt(); console.log('  SPINE  %s opened directly     : paras=%d  b.lemma=%d', vol, c[0], c[1]);
  process.exit(0);
})();

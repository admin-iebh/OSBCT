// THE FIX MUST ADD MARKUP AND NEVER MOVE A LETTER.  Renders the WORK spine
// under both readers and compares the rendered TEXT, character for character.
// A drift here would mean the located-substring rule dropped or duplicated
// text -- the one way this change could damage the page silently.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlined(p){let h=fs.readFileSync(p,'utf8');let n=0;
  h=h.replace(/<script src="\.\.\/i18n\.js[^"]*"><\/script>/,()=>{n++;return '<script>'+fs.readFileSync('site/i18n.js','utf8')+'</script>';});
  h=h.replace(/<script src="panel\.js[^"]*"[^>]*><\/script>/,()=>{n++;return '<script>'+fs.readFileSync(R+'/panel.js','utf8')+'</script>';});
  if(n!==2) throw new Error('INLINING FAILED '+n); return h;}
function boot(p){const dom=new JSDOM(inlined(p),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function spineText(p,vol,canon){
  const w=boot(p); for(let k=0;k<80&&!w.openKey;k++) await wait(80);
  const D=()=>w.document;
  const settle=async(sel,n)=>{for(let k=0;k<70;k++){await wait(90); if(D().querySelectorAll(sel).length>=n) return;}};
  try{ await w.openKey(vol+'#9','A'); }catch(e){}
  await settle('.para',1);
  try{ w.eval('state.filter=null;state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(canon+'#0','canon'); }catch(e){}
  await settle('.para',4);
  try{ w.eval('state.active={canon:true,A:true,T:false};render();'); }catch(e){}
  await settle('.para.l-A',1);
  const band=[...D().querySelectorAll('.para.l-A')].map(e=>e.textContent).join('');
  try{ w.eval('state.filter="'+vol+'";state.active={canon:false,A:true,T:false};render();'); }catch(e){}
  await settle('.para',4);
  const work=[...D().querySelectorAll('.para')].map(e=>e.textContent).join('');
  return {band,work};
}
(async()=>{
  const vol=process.argv[2], canon=process.argv[3];
  const a=await spineText(R+'/reader2.html.prebold',vol,canon);
  const b=await spineText(R+'/reader2.html',vol,canon);
  for(const k of ['band','work']){
    const same=a[k]===b[k];
    let where=''; if(!same){ let i=0; while(i<a[k].length&&i<b[k].length&&a[k][i]===b[k][i]) i++;
      where=' first difference at '+i+': '+JSON.stringify(a[k].slice(i-40,i+40))+' vs '+JSON.stringify(b[k].slice(i-40,i+40)); }
    console.log(vol+'  '+k+' text identical: '+same+'  ('+a[k].length+' vs '+b[k].length+' chars)'+where);
  }
  process.exit(0);
})();

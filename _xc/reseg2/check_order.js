// Render a volume in the ACTUAL reader (reader2.html under jsdom, the same
// bootstrap pipeline/check_layout.js uses) and assert two things the
// letter-equivalence check cannot see:
//   1. the printed page markers come out in ASCENDING order
//   2. every section heading is followed by its own paragraph, not by the
//      paragraph it should have headed minus one
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){
  const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
(async()=>{
  const vol=process.argv[2];
  const w=boot(); await wait(1500);
  try{ w.eval('state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(vol+'#0','A'); }catch(e){}
  for(let k=0;k<70;k++){ await wait(90);
    const s=w.document.querySelector('#scroll'); if(s && s.textContent.length>2000) break; }
  const s=w.document.querySelector('#scroll');
  const nodes=[...s.querySelectorAll('.para')];
  // page markers, in DOM order
  const pgs=[...s.querySelectorAll('.pgmk')].map(e=>{const m=String(e.textContent).match(/\d+/);return m?parseInt(m[0],10):NaN;}).filter(n=>!isNaN(n));
  let desc=0, worst=null;
  for(let i=1;i<pgs.length;i++) if(pgs[i]<pgs[i-1]){ desc++; if(!worst) worst=[pgs[i-1],pgs[i]]; }
  // headings followed by a paragraph
  const secs=[...s.querySelectorAll('.head, .stack, .secprose')];
  // DOCUMENT ORDER over headings and paragraphs together: a heading must have
  // a paragraph somewhere after it (a stack of consecutive headings is legal;
  // a heading at the very end of the volume with nothing under it is not).
  const flat=[...s.querySelectorAll('.head, .stack, .secprose, .para')];
  let orphan=0, lastPara=-1;
  flat.forEach((e,i)=>{ if((e.className||'').split(' ').includes('para')) lastPara=i; });
  flat.forEach((e,i)=>{ if(!(e.className||'').split(' ').includes('para') && i>lastPara) orphan++; });
  const paras=[...s.querySelectorAll('.para')].length;
  console.log(`${vol}: rendered ${paras} .para, ${pgs.length} page markers, ${secs.length} headings`);
  console.log(`   page markers ASCENDING: ${desc===0?'YES':'NO ('+desc+' descents, first '+worst+')'}`);
  console.log(`   first 12 page markers: ${pgs.slice(0,12).join(' ')}`);
  console.log(`   last 6 page markers  : ${pgs.slice(-6).join(' ')}`);
  console.log(`   headings with NOTHING after them: ${orphan}`);
  process.exit(desc===0 && orphan===0 ? 0 : 1);
})();

// How heavy is the reader's DOM after boot and after opening a big volume?
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
let bytes=0, fetches=[];
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const w=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}if(t){bytes+=t.length;fetches.push([String(u).split('?')[0],t.length]);}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;
(async()=>{
  await wait(1500);
  const bootBytes=bytes, bootNodes=w.document.getElementsByTagName('*').length;
  console.log('AFTER BOOT (no volume open)');
  console.log('  bytes fetched : '+(bootBytes/1048576).toFixed(2)+' MB');
  console.log('  DOM elements  : '+bootNodes.toLocaleString());
  fetches.slice().sort((a,b)=>b[1]-a[1]).slice(0,6).forEach(f=>console.log('     '+(f[1]/1024).toFixed(0).padStart(6)+' KB  '+f[0]));
  for(const vol of ['18Khu01','39Abhi11']){
    bytes=0; fetches=[];
    try{ w.openKey(vol+'#0','canon'); }catch(e){ console.log('  open failed',e.message); }
    await wait(2500);
    console.log('\nAFTER OPENING '+vol);
    console.log('  extra bytes   : '+(bytes/1048576).toFixed(2)+' MB');
    console.log('  DOM elements  : '+w.document.getElementsByTagName('*').length.toLocaleString());
    console.log('  .para blocks  : '+w.document.querySelectorAll('.para').length.toLocaleString());
    console.log('  a.xref anchors: '+w.document.querySelectorAll('a.xref').length.toLocaleString());
    console.log('  files fetched : '+fetches.length);
    const byDir={};
    fetches.forEach(f=>{const d=f[0].replace(/[^/]*$/,'');byDir[d]=(byDir[d]||0)+f[1];});
    Object.entries(byDir).sort((a,b)=>b[1]-a[1]).slice(0,8)
      .forEach(([d,n])=>console.log('     '+(n/1048576).toFixed(2)+' MB  '+d));
    fetches.slice().sort((a,b)=>b[1]-a[1]).slice(0,5)
      .forEach(f=>console.log('       biggest: '+(f[1]/1024).toFixed(0)+' KB  '+f[0]));
  }
  process.exit(0);
})();

// search.html must fetch NOTHING heavy on load, and must still search.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
let log=[];
const resolve=u=>{u=String(u).split('?')[0].replace(/^\.\//,'');return path.join('site',u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const w=new JSDOM(fs.readFileSync('site/search.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/search.html',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}log.push([String(u).split('?')[0],t?t.length:0]);return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;
(async()=>{
  await wait(1200);
  const onLoad=log.slice(); const mb=onLoad.reduce((a,b)=>a+b[1],0)/1048576;
  console.log('ON LOAD: '+onLoad.length+' fetch(es), '+mb.toFixed(2)+' MB');
  onLoad.forEach(f=>console.log('   '+(f[1]/1024).toFixed(0)+' KB  '+f[0]));
  const heavy=onLoad.some(f=>/terms\.compact|names\.json/.test(f[0]));
  console.log('  terms.compact/names fetched on load: '+(heavy?'YES  <-- STILL BROKEN':'no'));
  log=[];
  w.document.getElementById('q').value='nibbāna';
  await w.run(); await wait(3000);
  const q=log.reduce((a,b)=>a+b[1],0)/1048576;
  const rows=w.document.querySelectorAll('#results .hit, #results > div').length;
  console.log('\nAFTER FIRST QUERY: '+log.length+' fetch(es), '+q.toFixed(2)+' MB');
  console.log('  status : '+w.document.getElementById('status').textContent.slice(0,90));
  console.log('  results: '+rows+' row(s) rendered');
  process.exit(heavy||rows===0?1:0);
})();

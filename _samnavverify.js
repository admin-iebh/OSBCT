// THE THREE SAṀYUTTA NAVS — row sweep over EVERY node of the volume.
//
//   node --max-old-space-size=4096 _samnavverify.js <VOL> [from] [to]
//
// !!! WHY NOT `_vinnavverify.js`: that file asserts ONE nav node per volume and
// sweeps `all[0]`.  12Sam01 and 13Sam02 carry TWO BOOKS and so TWO nodes, and
// sweeping only the first would report a clean pass over half the volume —
// the same shape as the false pass that file itself was fixed for on
// 2026-07-27.  This one iterates every node the volume has and says how many.
//
// The class this finds and nothing else does is the SPAN bug: a row that opens
// NOTHING, or opens its parent's whole text.  No body, apparatus or layout
// gate can see it.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
let pass=0,fail=0;const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<90;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);
const VOL=process.argv[2], FROM=+(process.argv[3]||0), TO=+(process.argv[4]||1e9);
(async()=>{
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const canon=nav.layers.find(L=>L.layer==='canon'||L.id==='canon')||nav.layers[0];
  const nik=canon.nikayas.find(n=>(n.volumes||[]).some(v=>v.vol===VOL));
  const nodes=(nik.volumes||[]).filter(v=>v.vol===VOL);
  console.log('   '+VOL+' is in '+nik.nikaya+' and has '+nodes.length+' nav node(s): '
              +JSON.stringify(nodes.map(n=>n.title)));
  const w=boot();
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  const pit=find(w,nik.nikaya); if(pit){pit.click(); await wait(120);}
  let total=0,empty=[],whole_open=[],swept=0;
  for(const nd of nodes){
    const b=find(w,nd.title);
    if(!b){A(false,'no sidebar row for '+nd.title);continue;}
    b.click(); await wait(220);
    for(let k=0;k<60;k++){await wait(30);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
    const whole=w.document.querySelectorAll('#scroll .para.canon').length;
    A(whole>0,nd.title+' opens nothing');
    const rows=[...b.parentElement.querySelectorAll('.row')].filter(r=>r!==b);
    total+=rows.length;
    for(const r of rows.slice(FROM,Math.min(TO,rows.length))){
      r.click(); await wait(2);
      for(let k=0;k<40;k++){await wait(3);if(w.document.querySelectorAll('#scroll .para.canon').length)break;}
      const n=w.document.querySelectorAll('#scroll .para.canon').length;
      swept++;
      if(!n) empty.push(nd.title+' / '+lbl(r));
      else if(n>=whole&&whole>50) whole_open.push(nd.title+' / '+lbl(r));
    }
    console.log('   '+nd.title+': '+rows.length+' rows, opens '+whole+' ¶');
  }
  A(empty.length===0,empty.length+' of '+swept+' rows open NOTHING — '+JSON.stringify(empty.slice(0,8)));
  A(whole_open.length===0,whole_open.length+' of '+swept+' rows open the WHOLE book — '+JSON.stringify(whole_open.slice(0,8)));
  console.log('   swept '+swept+' of '+total+' rows across '+nodes.length+' node(s)');
  console.log('\n'+pass+' passed, '+fail+' failed');
  process.exit(fail?1:0);
})();

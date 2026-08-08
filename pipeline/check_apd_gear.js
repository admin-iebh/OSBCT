// GATE: the APD tab's defaults and gear, as the reader decided 2026-08-06.
//
//   1. CPED opens first and PED second, and both are OPEN — the two defaults;
//   2. every other section with a hit draws CLOSED: a one-line header
//      carrying its label and count — hidden must not mean absent;
//   3. clicking that header opens the section in place WITHOUT touching the
//      persisted gear state — for this word only;
//   4. the gear popover carries the one-line §9 note (Edition, Abhidhāna and
//      DPD are not options, and the absence must read as deliberate), and
//      offers NO checkbox for CPED or PED;
//   5. ticking a checkbox persists (localStorage `osbct-apdgear`, beside
//      `osbct-wle`), reopens the popover, and the section renders OPEN;
//   6. the persisted choice holds on the NEXT word.
//
// Drives the real reader2.html + panel.js in jsdom with `?wl=1`, feeding the
// stores from the repository the way the panel's own '../../stores/' archive
// fallback expects; gzipped shards are served DECOMPRESSED, which the panel's
// two-byte sniff is explicitly built to accept.  The panel's real Chromium
// gate is `_panel/gate_reader.py`; this file exists because the sandbox has
// no Chromium, and it presses only what it added.
//
// SELFTEST: run against a build without the gear (`--selftest PATH`, e.g.
// `git show HEAD:site/reader/panel.js`) — the assertions must FAIL there.
//
// Usage:  node pipeline/check_apd_gear.js
//         node pipeline/check_apd_gear.js --selftest /tmp/panel_old.js

const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {JSDOM}=require('jsdom');
const ROOT=path.dirname(__dirname);
const R=path.join(ROOT,'site','reader');
const SELF=process.argv.includes('--selftest');
const PANEL=SELF?process.argv[process.argv.indexOf('--selftest')+1]:path.join(R,'panel.js');

const resolve=u=>{u=String(u).split('?')[0];
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}}
  while(u.startsWith('../')) u='REPO/'+u.slice(3), u=u.replace('REPO/../','REPO/'); // handled below
  return u;};
function localPath(u){
  u=String(u).split('?')[0];
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){} return path.join(R,u);}
  if(u.startsWith('../../')) return path.join(ROOT,u.slice(6));
  if(u.startsWith('../'))    return path.join(ROOT,'site',u.slice(3));
  return path.join(R,u);
}
function readMaybe(f){
  try{ return fs.readFileSync(f); }catch(e){}
  return null;
}
function boot(){
  const dom=new JSDOM(fs.readFileSync(path.join(R,'reader2.html'),'utf8'),{
    runScripts:'dangerously',pretendToBeVisual:true,
    url:'http://x/reader2.html?wl=1',
    beforeParse(w){
      w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{
        let f=localPath(u); let b=readMaybe(f);
        if(!b&&/\.gz$/.test(f)){ /* nothing */ }
        if(b&&/\.gz$/.test(f)){ try{ b=zlib.gunzipSync(b); }catch(e){} }
        if(!b&&!/\.gz$/.test(f)){ const g=readMaybe(f+'.gz'); if(g){ try{ b=zlib.gunzipSync(g); }catch(e){} } }
        const ok=b!=null;
        return Promise.resolve({ok,status:ok?200:404,
          json:()=>Promise.resolve(ok?JSON.parse(b.toString('utf8')):{}),
          text:()=>Promise.resolve(ok?b.toString('utf8'):''),
          arrayBuffer:()=>Promise.resolve(ok?b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength):new ArrayBuffer(0))});
      };
    }});
  return dom.window;
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0;
const ok=(c,label,detail)=>{ console.log((c?'  ok    ':'  FAIL  ')+label+(detail?'  ['+detail+']':'')); if(!c)fails++; };

(async()=>{
  console.log((SELF?'SELFTEST — expected to FAIL — panel: ':'checking panel: ')+PANEL);
  const w=boot();
  for(let k=0;k<100;k++){ await wait(100); if(w.document.querySelectorAll('.row').length>3) break; }
  // jsdom 29 no longer loads external <script>s: inject the panel by hand.
  // document.readyState is already 'complete', so panel.js calls start() itself.
  w.eval(fs.readFileSync(PANEL,'utf8'));
  await wait(200);
  await w.openKey('18Khu01#89','canon');
  let para=null;
  for(let k=0;k<60;k++){ await wait(100); para=w.document.querySelector('.para'); if(para) break; }
  if(!para||!w.WL){ console.log('  FAIL  panel or paragraph did not arrive (WL='+(!!w.WL)+')'); process.exit(1); }
  // `āmanteti` is the file's own recorded many-dictionary example ("the reader
  // found āmanteti showing two where dictionary.sutta.org shows ten") — an
  // overflow lemma like `dhammā` carries its APD rows on pages this press
  // does not walk, and shows PED alone.
  await w.WL.lookup('āmanteti',para);
  const el=()=>w.document.getElementById('wl');
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const dictBtn=w.document.querySelector('#wlt button[data-tab="dict"]');
  if(!dictBtn){ console.log('  FAIL  no APD tab for āmanteti'); process.exit(1); }
  dictBtn.click(); await wait(300);
  const body=()=>w.document.getElementById('wlb');

  // 1. CPED first and open, PED second and open
  const secs=[...body().querySelectorAll('.wl-sec')];
  const label=s=>{const el2=s.querySelector('.wl-sub'); const ol=s.querySelector('.wl-openline');
    return (el2?el2.textContent:ol?ol.textContent:'').trim();};
  const isOpen=s=>!s.classList.contains('wl-off');
  ok(secs.length>2 && /Concise/i.test(label(secs[0])) && isOpen(secs[0]),
     'CPED is first and open', label(secs[0])||'(none)');
  ok(secs.length>2 && /PED|P-E|Pali-English/i.test(label(secs[1])) && isOpen(secs[1]),
     'PED is second and open', label(secs[1])||'(none)');

  // 2. everything else closed, with the one-line count header
  const others=secs.slice(2);
  const closed=others.filter(s=>!isOpen(s));
  ok(others.length>0 && closed.length===others.length,
     'every other section draws closed', closed.length+' of '+others.length+' closed');
  ok(closed.every(s=>{const b=s.querySelector('.wl-openline'); return b&&/·\s*\d+/.test(b.textContent);}),
     'closed sections carry label · count', closed.length?closed[0].querySelector('.wl-openline').textContent.trim():'(none)');

  // 3. opening in place does not touch the persisted state
  const before=w.localStorage.getItem('osbct-apdgear');
  if(closed.length){ closed[0].querySelector('.wl-openline').click(); await wait(100); }
  ok(closed.length>0 && !closed[0].querySelector('div[hidden]'),
     'one-line header opens the section in place');
  ok(w.localStorage.getItem('osbct-apdgear')===before,
     'in-place open leaves the gear state alone');

  // 3b. the jump strip lists ONLY the open sections (reader, 2026-08-09) —
  //     a closed section is already its own one-line header, and the strip
  //     said everything twice
  const jump1=[...body().querySelectorAll('.wl-jump a')].map(a=>a.textContent.trim());
  ok(jump1.length===2 && /Concise/i.test(jump1[0]) && /PED|P-E/i.test(jump1[1]),
     'jump strip lists only the open sections', jump1.join(' | ')||'(no strip)');

  // 4. the gear: §9 note present; no checkbox for CPED or PED
  const gear=body().querySelector('.wl-gear');
  ok(!!gear,'the gear exists');
  if(gear){ gear.click(); await wait(100); }
  const pop=body().querySelector('.wl-gearpop');
  ok(!!pop && !pop.hidden,'the popover opens');
  ok(!!pop && /§9/.test(pop.textContent),'the popover carries the §9 line');
  const boxIds=pop?[...pop.querySelectorAll('input[data-wl-gear]')].map(i=>i.dataset.wlGear):[];
  ok(boxIds.length>0 && !boxIds.includes('C') && !boxIds.includes('_ped'),
     'CPED and PED are not options', boxIds.join(','));

  // 5. ticking NCP persists, reopens the popover, and opens the section
  const ncp=pop&&pop.querySelector('input[data-wl-gear="NCP"]');
  if(ncp){ ncp.checked=true; ncp.dispatchEvent(new w.Event('change',{bubbles:true})); await wait(300); }
  let st={}; try{ st=JSON.parse(w.localStorage.getItem('osbct-apdgear')||'{}'); }catch(e){}
  ok(!!ncp && st.NCP===1,'the choice persists in osbct-apdgear', JSON.stringify(st));
  const pop2=body().querySelector('.wl-gearpop');
  ok(!!pop2 && !pop2.hidden,'the popover stays open across the re-render');
  const ncpSec=body().querySelector('#wl-s-NCP');
  ok(!!ncpSec && !ncpSec.classList.contains('wl-off'),'the ticked section renders open');
  const jump2=[...body().querySelectorAll('.wl-jump a')].map(a=>a.textContent.trim());
  ok(jump2.length===3 && jump2.some(t=>/New Concise/i.test(t)),
     'the ticked section joins the jump strip', jump2.join(' | '));

  // 6. the choice holds on the next word
  await w.WL.lookup('bhagavā',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const db2=w.document.querySelector('#wlt button[data-tab="dict"]');
  if(db2){ db2.click(); await wait(300); }
  const ncpSec2=body().querySelector('#wl-s-NCP');
  ok(!ncpSec2 || !ncpSec2.classList.contains('wl-off'),
     'the persisted choice holds on the next word', ncpSec2?'present, open':'no NCP hit for this word');

  console.log(fails?('FAILED: '+fails+' assertion(s)'):'all green');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('  FAIL  threw: '+(e&&e.message||e)); process.exit(1); });

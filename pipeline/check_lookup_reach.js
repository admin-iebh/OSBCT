// A WORD THAT IS IN THE DICTIONARY MUST RESOLVE THROUGH THE READER'S OWN PATH.
//
// `claude/open_atappaka_not_found_in_lookup.md`, closing paragraph: "Whatever
// the cause, the fix should come with a check that would have caught it: a
// sample of known-present words asserted to resolve through the reader's own
// path, not through a script's."  This is that check.
//
// The fault: the panel entered `lookup_eval/` through the `form` set alone, and
// `form` holds only the surface forms the corpus inflects.  `atappaka` sits in
// `lem` with its Abhidhāna gloss; it is not a surface form; the panel said
// nothing.  34,821 of 52,757 lemmas (66.0%) and 57,198 of 74,146 DPD headwords
// (77.1%) were unreachable the same way.
//
// So the sample is drawn FROM THE STORE at run time — words known to be in
// `lem` but absent from `form`, exactly the class that was broken — and each is
// put through `lookup()`, the function a click and the search box both call.
// A hard-coded list would stop testing the fault the day the store is rebuilt.
//
//   node pipeline/check_lookup_reach.js [N]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
// !!! THE STORES MOVED, TWICE OVER, AND THIS RESOLVER HAD TO LEARN BOTH MOVES.
// 2026-08-07, DEPLOY_SCALE §6a: panel.js now names an ABSOLUTE origin
// (https://dict.buddha-dhamma.net/lookup/...) instead of '../lookup/', and the
// stores move from site/ to stores/.  This function is the offline stub's whole
// notion of where a URL lives, so both changes land here.
//
// It was run against the changed panel.js BEFORE being fixed, and reported
// 0 passed, 6 failed -- "No entry for atappaka in the corpus or the
// dictionaries", the exact sentence this gate exists to catch.  That is the
// negative control for the fix, and it is recorded because a resolver that has
// only ever been seen to pass proves nothing.
//
// STORE is detected, not assumed, so this file works before the relocation,
// after it, and if the two lines in panel.js are ever reverted.
const STORE=fs.existsSync('stores/lookup/index.json')?'stores':'site';
const isStore=p=>/^lookup(_eval)?\//.test(p);
const resolve=u=>{
  u=String(u).split('?')[0];
  if(u.startsWith('../')){const p=u.slice(3);return path.join(isStore(p)?STORE:'site',p);}
  if(u.startsWith('http')){
    let p=u;try{p=new URL(u).pathname.replace(/^\//,'');}catch(e){}
    return isStore(p)?path.join(STORE,p):path.join(R,p);
  }
  return path.join(R,u);
};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    return t==null?m:'<script>'+t+'</script>'; });
}
function boot(){
  const dom=new JSDOM(inlineScripts(fs.readFileSync(R+'/reader2.html','utf8')),
    {runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/?wl=1',beforeParse(w){
      w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,
          json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
// --- the sample, taken from the store itself -------------------------------
function sample(n){
  const load=d=>{const out={};for(const f of fs.readdirSync(d)){if(!f.endsWith('.json'))continue;
    let x=null;try{x=JSON.parse(fs.readFileSync(path.join(d,f),'utf8'));}catch(e){continue}
    for(const k of Object.keys(x)) out[k]=1;} return out;};
  const form=load(path.join(STORE,'lookup_eval/form')), lem=load(path.join(STORE,'lookup_eval/lem'));
  // !!! ABSENT FROM `freq` TOO, or the sample is not a sample of the fault.
  // `resolveTyped` queries `lookup/freq/` first, so a lemma that also happens
  // to occur in the corpus was always reachable and proves nothing.  Filtering
  // on both is what makes every word here an instance of what was broken.
  const freq=load(path.join(STORE,'lookup/freq'));
  const broken=Object.keys(lem)
    .filter(k=>!form[k] && !freq[k] && /^[a-zāīūṁṅñṭḍṇḷ]{5,}$/.test(k)).sort();
  const step=Math.max(1,Math.floor(broken.length/n));
  const out=[]; for(let i=0;i<broken.length&&out.length<n;i+=step) out.push(broken[i]);
  if(lem['atappaka'] && out.indexOf('atappaka')<0) out.unshift('atappaka');   // the reported word, always
  return {words:out, total:broken.length, form:Object.keys(form).length, lem:Object.keys(lem).length};
}
let pass=0, fail=0;
const ok=(w,c,g)=>{ if(c){pass++;console.log('  ok   '+w);} else {fail++;console.log('  FAIL '+w+'   got: '+JSON.stringify(g));} };

(async()=>{
  const S=sample(+(process.argv[2]||10));
  console.log('store: form %d keys, lem %d keys; %d lemmas absent from form',
              S.form, S.lem, S.total);
  console.log('sample (%d): %s\n', S.words.length, S.words.join(' '));
  const w=boot(); await wait(600);
  const doc=w.document;
  // !!! DRIVE THE REAL SEARCH BOX, NOT `lookup()`.  panel.js runs inside an
  // IIFE, so `lookup`, `EVAL` and the rest are not reachable from outside — and
  // that is fortunate, because calling `lookup` directly would have skipped
  // `resolveTyped`, which is where the reported fault actually lived: it
  // queries `lookup/freq/`, the words that OCCUR IN THE CORPUS, so a headword
  // the edition never inflects bare never reached `lookup` at all.  Typing into
  // the box is the reader's path; anything less tests a different program.
  const openBtn=doc.getElementById('wlw'); if(openBtn) openBtn.click();
  await wait(200);
  const q=doc.getElementById('wlq');
  if(!q){ console.log('  FAIL the panel has no search box (#wlq)'); process.exit(1); }
  for(const word of S.words){
    // !!! CLEAR BETWEEN WORDS.  The panel keeps the previous word's tabs and
    // body until the next render replaces them, so a poll that starts while
    // the new lookup is still in flight reads the OLD word's success and breaks
    // out immediately.  That is a false pass per word and it is invisible.
    // Emptying both and requiring one of them to come back is what makes each
    // iteration an observation of THIS word.
    doc.getElementById('wlb').innerHTML=''; doc.getElementById('wlt').innerHTML='';
    q.hidden=false; q.value=word;
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    // poll rather than sleep a fixed time: a slow shard would otherwise read as
    // "not found" and the gate would pass on a fault it caused itself
    // !!! `!/not found/i.test(body)` WAS A VACUOUS TEST AND PASSED ON THE OLD
    // CODE.  The interface runs in SPANISH, so the miss renders `wl_notfound`
    // as "no se encontró…" and an English regex never matched it; the message
    // is itself body text, so `body.length>0` was true as well.  The gate
    // reported 7/7 against the very build that has the bug.
    // The miss has a MARKER — `<p class="wl-none">` — and a hit renders TABS
    // into `#wlt` while a miss explicitly clears it.  Assert both.
    let none=true, tabs='', st='';
    for(let i=0;i<60;i++){ await wait(100);
      st=doc.getElementById('wl')?doc.getElementById('wl').dataset.state:'';
      none=!!doc.querySelector('#wlb .wl-none');
      tabs=(doc.getElementById('wlt')||{}).textContent||'';
      if(st!=='loading'&&(none||tabs)) break; }
    const body=(doc.getElementById('wlb')||{}).textContent||'';
    ok('"'+word+'" resolves through the search box', !none && tabs.trim().length>0,
       {state:st, wl_none:none, tabs:tabs.slice(0,50), body:body.slice(0,50)});
  }
  console.log('\n%d passed, %d failed', pass, fail);
  process.exit(fail?1:0);
})();

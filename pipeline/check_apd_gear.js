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
  ok(secs.length>=2 && /Concise/i.test(label(secs[0])) && isOpen(secs[0]),
     'CPED is first and open', label(secs[0])||'(none)');
  ok(secs.length>=2 && /PED|P-E|Pali-English/i.test(label(secs[1])) && isOpen(secs[1]),
     'PED is second and open', label(secs[1])||'(none)');

  // 2. NOTHING else draws as a section — the seven one-line headers were
  //    replaced by ONE summary line saying how many more dictionaries carry
  //    this word (reader, 2026-08-09, trying this before deciding on removal)
  ok(secs.length===2, 'only the open sections draw', secs.length+' sections');
  const more=body().querySelector('.wl-moredicts');
  ok(!!more && /7/.test(more.textContent),
     'one summary line carries the closed count', more?more.textContent.trim():'(none)');

  // 3. the summary line opens the GEAR, and touches no state
  const before=w.localStorage.getItem('osbct-apdgear');
  if(more){ more.click(); await wait(100); }
  const popNow=body().querySelector('.wl-gearpop');
  ok(!!more && !!popNow && !popNow.hidden, 'the summary line opens the gear');
  ok(w.localStorage.getItem('osbct-apdgear')===before,
     'the summary line leaves the gear state alone');
  if(popNow) popNow.hidden=true;

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
  const more2=body().querySelector('.wl-moredicts');
  ok(!!more2 && /6/.test(more2.textContent),
     'the summary count falls when a section opens', more2?more2.textContent.trim():'(none)');

  // 6. the choice holds on the next word
  await w.WL.lookup('bhagavā',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const db2=w.document.querySelector('#wlt button[data-tab="dict"]');
  if(db2){ db2.click(); await wait(300); }
  const ncpSec2=body().querySelector('#wl-s-NCP');
  ok(!ncpSec2 || !ncpSec2.classList.contains('wl-off'),
     'the persisted choice holds on the next word', ncpSec2?'present, open':'no NCP hit for this word');

  // 7. DPD's stub blocks are scrubbed (2026-08-09, user-reported): the
  //    archived entry carries `root family loading...` etc. as lazy-load
  //    stubs DPD's server would have filled; the chip and the stub must BOTH
  //    be gone, and the three inline blocks must keep their chips.
  await w.WL.lookup('sāvakā',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const dpdBtn=w.document.querySelector('#wlt button[data-tab="dpd"]');
  if(dpdBtn){ dpdBtn.click(); await wait(300); }
  const dpdTxt=body().textContent;
  ok(!/loading\.\.\./.test(dpdTxt),'no lazy-load stub survives in the DPD tab');
  const chips=[...body().querySelectorAll('a.dpd-button[data-target]')];
  ok(chips.length>0 && chips.every(a=>!!body().querySelector('[id="'+a.dataset.target+'"]')),
     'every surviving DPD chip has a real block', chips.length+' chips');
  ok(chips.some(a=>/grammar/i.test(a.textContent)),
     'the inline chips (grammar…) survive the scrub');

  // 8. THE FAMILIES ARE BACK WITH CONTENT (2026-08-09, the store rebuild):
  //    the root-family chip exists again, and clicking it fetches the
  //    pre-rendered family from stores/lookup_eval/family/ — for sāvaka,
  //    √su with its 111 words — with no stub and no dead promise.
  const rootChip=chips.find(a=>/root family/i.test(a.textContent));
  ok(!!rootChip,'the root family chip is back');
  if(rootChip){
    rootChip.click(); await wait(600);
    const blk=body().querySelector('[id="'+rootChip.dataset.target+'"]');
    ok(!!blk && /111.*words belong to the root family/.test(blk.textContent.replace(/\s+/g,' '))
            && /√su/.test(blk.textContent),
       'clicking it fetches the real √su family (111 words)',
       blk?blk.textContent.replace(/\s+/g,' ').slice(0,60):'(no block)');
    ok(!!blk && blk.querySelectorAll('table.family tr').length>100,
       'the family table carries its rows', blk?blk.querySelectorAll('table.family tr').length+' rows':'');
  }
  const compChip=chips.find(a=>/compound family/i.test(a.textContent));
  ok(!!compChip,'the compound family chip is back');
  const idmChip=chips.find(a=>/idiom/i.test(a.textContent));
  ok(!!idmChip,'the idioms chip is back');

  // 9. ONE BLOCK OPEN PER ENTRY (2026-08-09, user request): opening the
  //    compound family closes the root family; re-clicking closes itself.
  if(rootChip&&compChip){
    compChip.click(); await wait(600);
    const rootBlk=body().querySelector('[id="'+rootChip.dataset.target+'"]');
    const compBlk=body().querySelector('[id="'+compChip.dataset.target+'"]');
    ok(!!rootBlk&&rootBlk.classList.contains('hidden')
       &&!!compBlk&&!compBlk.classList.contains('hidden'),
       'opening one block closes the other',
       'root hidden='+(rootBlk&&rootBlk.classList.contains('hidden'))+' comp hidden='+(compBlk&&compBlk.classList.contains('hidden')));
    compChip.click(); await wait(100);
    ok(!!compBlk&&compBlk.classList.contains('hidden'),
       're-clicking the open chip closes it');
  }

  // 10. THE DICTIONARIES ARE REACHABLE BY THEIR OWN HEADWORDS (2026-08-10).
  //     `yathānisinna` is the reader's report of 2026-08-09: the panel said
  //     "no entry" while dictionary.sutta.org answered it — from PCED books B
  //     and K, both of which are in our own `_dictsrc/`.  It is a compound, so
  //     all twelve of its corpus forms are `dpd_tier: 3` and it never entered
  //     `LEMMAS`; the whole `lem` store was keyed on DPD's index, so 163,453
  //     of 210,111 headwords (77.8%) could not be reached.  See
  //     `claude/dpd_gates_the_abhidhana.md`.
  //
  //     THIS ASSERTION IS WRITTEN TO FAIL ON THE BUILD THAT HAS THE BUG, and
  //     was run red before the store existed — the dict tab does not even
  //     appear for this word today.  What it presses is what the reader sees:
  //     the two named books, drawn open, carrying their own Burmese gloss, and
  //     the Abhidhāna tab with the pm12e entry behind it.
  //
  //     B and K are ticked through localStorage rather than through the gear,
  //     because on the failing build there is no gear to click: viewDict
  //     returns `wl-none` before it draws one.
  w.localStorage.setItem('osbct-apdgear', JSON.stringify({B:1,K:1}));
  await w.WL.lookup('yathānisinna',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const db3=w.document.querySelector('#wlt button[data-tab="dict"]');
  ok(!!db3 && !db3.classList.contains('dis'),
     'yathānisinna has a dictionary tab', db3?db3.textContent.trim():'(no tab)');
  if(db3&&!db3.classList.contains('dis')){ db3.click(); await wait(300); }
  const secB=body().querySelector('#wl-s-B'), secK=body().querySelector('#wl-s-K');
  ok(!!secB,'book B (Pali Myanmar Dictionary) draws a section');
  ok(!!secK,'book K (Tipiṭaka Pāḷi-Myanmar Dictionary) draws a section');
  // the gloss itself, not merely a heading: the Burmese spelling of the word,
  // and K's definition line — the two strings `_dictsrc/pced_full.jsonl.gz`
  // actually carries for this headword.
  ok(!!secB && /ယထာနိသိန္န/.test(secB.textContent),
     'book B carries the Burmese headword', secB?secB.textContent.replace(/\s+/g,' ').slice(0,70):'');
  ok(!!secK && /ယထာနိသိန္န/.test(secK.textContent) && /နေ-ထိုင်-မြဲတိုင်းသော/.test(secK.textContent),
     'book K carries its definition', secK?secK.textContent.replace(/\s+/g,' ').slice(0,70):'');
  // and the §9 authority itself: pm12e.csv:145524 is this word, so the
  // Abhidhāna tab must not be disabled either.
  const abhiBtn=w.document.querySelector('#wlt button[data-tab="abhi"]');
  ok(!!abhiBtn && !abhiBtn.classList.contains('dis'),
     'the Abhidhāna tab is live for yathānisinna',
     abhiBtn?abhiBtn.textContent.trim():'(no tab)');
  if(abhiBtn&&!abhiBtn.classList.contains('dis')){ abhiBtn.click(); await wait(300); }
  ok(!!abhiBtn && !abhiBtn.classList.contains('dis') && /ယထာနိသိန္န/.test(body().textContent),
     'the Abhidhāna entry draws');
  // 10b. AND THE WORD THE READER TYPES NEED NOT CARRY ITS DIACRITICS.  §7 asks
  //      search to be diacritic-insensitive; the store is keyed on fold(), so
  //      the plain-ASCII spelling must reach the same two books.
  await w.WL.lookup('yathanisinna',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const db4=w.document.querySelector('#wlt button[data-tab="dict"]');
  if(db4&&!db4.classList.contains('dis')){ db4.click(); await wait(300); }
  ok(!!db4 && !db4.classList.contains('dis') && !!body().querySelector('#wl-s-K'),
     'the undiacriticked spelling reaches the same entry');

  // 11. THE MISS MESSAGE NO LONGER CLAIMS THE CORPUS IS SILENT WHEN IT IS NOT.
  //     "No entry for X in the corpus or the dictionaries" was false about its
  //     first half for any stem the edition only ever prints inflected.
  //     `yathāvuttamattha` is such a stem, measured over the shipped stores: it
  //     is in NEITHER freq, ped, lem, dpd NOR the new hw store, and the corpus
  //     carries 4 forms of it, 91 occurrences.  So the miss is genuine — and
  //     the forms must be offered above it, each one clickable.
  //
  //     Pressed through the SEARCH BOX, which is where the message lives; a
  //     direct WL.lookup() call would skip resolveTyped and test nothing.
  const qbox=w.document.getElementById('wlq');
  ok(!!qbox,'the panel has a search box');
  if(qbox){
    w.document.getElementById('wlb').innerHTML='';
    qbox.hidden=false; qbox.value='yathāvuttamattha';
    qbox.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    for(let k=0;k<80;k++){ await wait(100);
      if(w.document.querySelector('#wlb .wl-none')) break; }
    const none=w.document.querySelector('#wlb .wl-none');
    const pfx=[...w.document.querySelectorAll('#wlb .wl-pfx')];
    ok(!!none,'the typed stem is still reported as having no entry');
    ok(pfx.length>=4,'the corpus forms are offered before the message',
       pfx.map(b=>b.textContent.trim()).join(' | ').slice(0,90));
    ok(pfx.length>0 && pfx.every(b=>/^yath[aā]vuttamatth/.test(b.dataset.w||'')),
       'every form offered actually begins with the matched prefix',
       pfx.map(b=>b.dataset.w).join(' '));
    // !!! AND THE PREFIX IS THE STEM, NOT THE TYPED WORD (reader, 2026-08-10).
    //     A literal prefix drops every form whose final vowel has inflected:
    //     for `yathānisinna` that is 5 of 12 forms and 36 of 52 occurrences,
    //     including `yathānisinnova`, the commonest of the whole set.  The
    //     heading must therefore name the prefix actually matched — one
    //     character shorter than what was typed — and not claim to have
    //     matched the word.
    const sub=w.document.querySelector('#wlb .wl-sec .wl-sub');
    ok(!!sub && /yathāvuttamatth[^a]/.test(sub.textContent),
       'the heading names the matched prefix, not the typed word',
       sub?sub.textContent.replace(/\s+/g,' ').trim():'(none)');
    // the chips must be live: clicking one looks that form up
    if(pfx.length){
      const want=pfx[0].dataset.w;
      pfx[0].click();
      for(let k=0;k<80;k++){ await wait(100);
        if(el()&&el().dataset.state==='ready'
           &&w.document.getElementById('wlw').textContent===want) break; }
      ok(w.document.getElementById('wlw').textContent===want,
         'clicking a form looks it up',
         w.document.getElementById('wlw').textContent);
    }
  }

  // 12. A DICTIONARY THAT IS NEITHER THE ABHIDHĀNA NOR A PCED BOOK MUST ALSO
  //     BE REACHABLE BY ITS OWN HEADWORD.  `Akalaṅka` is a Malalasekera proper
  //     name and NOTHING else: measured over the shipped stores it is absent
  //     from freq, ped, lem and dpd, and carries no APD row and no Abhidhāna
  //     row — so it exists in the panel only if DPPN was keyed on its own
  //     headword.  Through `lem` it was reachable only where DPD happened to
  //     have a lemma for it.
  await w.WL.lookup('Akalaṅka',para);
  for(let k=0;k<120;k++){ await wait(100); if(el()&&el().dataset.state==='ready') break; }
  const db5=w.document.querySelector('#wlt button[data-tab="dict"]');
  ok(!!db5 && !db5.classList.contains('dis'),
     'a DPPN-only name has a dictionary tab', db5?db5.textContent.trim():'(no tab)');
  if(db5&&!db5.classList.contains('dis')){ db5.click(); await wait(300); }
  // and it must be DRAWN, not merely counted.  Its only section is the
  // proper-names one, which is not a default; before 2026-08-10 the tab said
  // "1" and rendered a single grey line.  Where nothing would be open, the
  // first section opens.
  const ppnSec=body().querySelector('#wl-s-_ppn');
  ok(!!ppnSec && !ppnSec.classList.contains('wl-off'),
     'the proper-names section is DRAWN, not just counted',
     body().textContent.replace(/\s+/g,' ').slice(0,80));
  ok(!!ppnSec && /Akalaṅka/.test(ppnSec.textContent),
     'and it carries the entry',
     ppnSec?ppnSec.textContent.replace(/\s+/g,' ').slice(0,70):'(none)');

  // 13. WHAT THE READER TYPED IS WHAT THE READER GETS (reader, 2026-08-10:
  //     "If I type kiriya it should not change to kiriyā").  `kiriya` occurs 4
  //     times and `kiriyā` 296; the 2026-08-05 order opened the commoner one
  //     silently.  Exact now wins, and the commoner spelling is OFFERED as a
  //     clickable line instead of being substituted.
  for (const [typed, other] of [['kiriya','kiriyā'], ['itthi','itthī']]) {
    w.document.getElementById('wlb').innerHTML='';
    qbox.hidden=false; qbox.value=typed;
    qbox.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    for(let k=0;k<80;k++){ await wait(100);
      if(el()&&el().dataset.state==='ready'
         &&w.document.getElementById('wlw').textContent===typed) break; }
    ok(w.document.getElementById('wlw').textContent===typed,
       '"'+typed+'" opens '+typed+', not '+other,
       w.document.getElementById('wlw').textContent);
    const sibs=[...w.document.querySelectorAll('#wlc .wl-sib')].map(b=>b.dataset.w);
    ok(sibs.indexOf(other)>=0,
       'and '+other+' is offered beside it', sibs.join(' ')||'(none)');
  }
  // and a query that is NOT a corpus form still reaches the commonest reading,
  // or diacritics stop being optional (§7)
  w.document.getElementById('wlb').innerHTML='';
  qbox.value='pathavikasina';
  qbox.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
  for(let k=0;k<80;k++){ await wait(100);
    if(el()&&el().dataset.state==='ready'
       &&/pathav/.test(w.document.getElementById('wlw').textContent)) break; }
  ok(/^pathavīkasiṇ/.test(w.document.getElementById('wlw').textContent),
     'an undiacriticked non-form still reaches the accented word',
     w.document.getElementById('wlw').textContent);

  console.log(fails?('FAILED: '+fails+' assertion(s)'):'all green');
  process.exit(fails?1:0);
})().catch(e=>{ console.log('  FAIL  threw: '+(e&&e.message||e)); process.exit(1); });

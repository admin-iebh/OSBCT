// GATE: every apparatus marker the edition prints must reach the page.
//
// WHY.  Reader, 2026-08-08: "the footnotes are missing" when a Commentary or
// Subcommentary is opened from the left pane.  The apparatus DATA was sound --
// 118 `<vol>.appk.json`, 73,431 notes -- and the `.appx` note block was drawn on
// every paragraph that has one.  What was lost was the MARKER in the running
// text: `fmtBold`/`_boldRange`/`gathaHTML` assembled the HTML first and then ran
// `([letter])(\d{1,2})` over it, so a bold lemma ending on the annotated letter
// -- `<b class="lemma">Apadāne</b>2` -- broke the adjacency the pattern needed.
// 3,480 of 70,598 markers (4.93%), concentrated in exactly the two layers the
// reader was reading.
//
// !!! THE PARAGRAPH'S OWN `text` IS NOT THE UNIT THE PAGE DRAWS, AND TWO
// VERSIONS OF THIS CHECK GOT THAT WRONG BEFORE IT WAS WRITTEN DOWN.
//   1.  Comparing markers in `text` against `sup.fnm` inside the paragraph
//       element reported 09DiT02 ord 14 as drawing 39 for 9 -- 30 inventions.
//       There were none: that ordinal also draws `verse/` blocks whose text
//       lives in a side map, so the check was counting them against a string
//       that does not contain them.
//   2.  Excluding `.gatha`/`.gatha-after` to compensate then reported 09DiT02 as
//       drawing 7 markers for 907 -- a near-total failure.  There was none
//       either: in a ṭīkā the RUNNING PROSE is drawn in `gatha-after` blocks, so
//       the exclusion threw away almost the whole volume.
// Both are facts about the check reported as facts about the reader, which is
// the failure this whole project exists to avoid.
//
// THE DENOMINATOR IS THE STRINGS THE PAGE ACTUALLY DRAWS.  Where `verse/<VOL>`
// carries an entry for an ordinal, the reader draws THOSE lines and not the
// paragraph's `text`; the two are a re-segmentation of each other and their
// marker counts differ slightly (19Khu02: 927 in `text`, 925 in the drawn lines;
// 09DiT02: 907 against 868).  Measured against `text` this check would show a
// permanent shortfall that no rendering fix can close, which is the shape of
// gate that gets switched off.  Measured against what is drawn, both volumes are
// exact -- and the `text`/`verse` divergence stays visible as its own number,
// reported below, because it is a real question about the verse map and not
// something this check should quietly absorb.
//
// `.appx` is excluded from the page side only because a note block draws no
// `sup.fnm` at all, so excluding it can cost nothing.
//
// Usage:  node pipeline/check_fn_markers.js [VOL ...]      (default: a sample)
//         node pipeline/check_fn_markers.js --all
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const ROOT=path.dirname(__dirname); const R=path.join('site','reader');
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(path.join(R,'reader2.html'),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

// !!! THIS CLASS MUST TRACK `FNM` IN reader2.html.  It gained `)”’»` on
// 2026-08-08 (684 markers the letter-only form could not see), and a gate whose
// pattern is narrower than the reader's would score correct markers as invented.
const MARK=/[a-zāīūṁṅñṭḍṇḷ)”’»](\d{1,2})(?!\d)/g;
const LEAD=/^\s*\d+(-\d+)?\.\s*/;
// every string inside a `verse/` entry, whatever the entry's shape
// (`groups`, `before`, `after`, and a group member may be {gatha:[...]}or {t,n})
function lines(e,out){ out=out||[];
  if(e==null) return out;
  if(typeof e==='string'){ out.push(e); return out; }
  if(Array.isArray(e)){ for(const x of e) lines(x,out); return out; }
  if(typeof e==='object'){ for(const k in e) lines(e[k],out); }
  return out; }
// One canon volume, one aṭṭhakathā, one ṭīkā, plus the three the reader met.
const SAMPLE=['21Khu04','19Khu02','31KhuA12','32KhuA13','29KhuA10','09DiT02','25VsmT01'];

// !!! THE ONLY WAY TO KNOW A GATE WORKS IS TO BREAK THE THING IT GUARDS.
// `--selftest` puts the ORIGINAL `_boldRange` back -- the one that assembled the
// markup and then ran the marker pattern over it -- re-renders, and requires the
// check to go red.  A gate that has never been seen to fail is a gate that might
// be measuring nothing; that is how `check_links.py` carried a wrong range
// pattern through 356 correct links, and how `check_concordance.py` drifted by
// 46 without a word.
// a second assertion, added with the tooltip: a marker whose paragraph carries a
// note with that number must SHOW it.  The pairing itself is only claimed where
// the counts agree, so this asserts reachability, not identification.
const OLD_BOLDRANGE = `_boldRange = function(stripped,sp,a,b,marks){
  let seg=sp.filter(x=>x[1]>a&&x[0]<b).map(x=>[Math.max(a,x[0]),Math.min(b,x[1])]);
  let html='',cur=a;
  for(const s of seg){ if(s[0]<cur) continue;
    html+=esc(stripped.slice(cur,s[0]))+'<b class="lemma">'+esc(stripped.slice(s[0],s[1]))+'</b>'; cur=s[1]; }
  html+=esc(stripped.slice(cur,b));
  return html.replace(/([a-z\\u0101\\u012b\\u016b\\u1e41\\u1e45\\u00f1\\u1e6d\\u1e0d\\u1e47\\u1e37])(\\d{1,2})(?![\\d])/g,'$1<sup class="fnm">$2</sup>');
}`;

(async()=>{
  let argv=process.argv.slice(2);
  const selftest=argv.includes('--selftest');
  let vols=argv.filter(a=>a!=='--selftest');
  if(vols[0]==='--all'){
    vols=fs.readdirSync(path.join(R,'bold')).filter(f=>f.endsWith('.bold.json'))
           .map(f=>f.slice(0,-10)).sort();
  } else if(!vols.length) vols=selftest?['31KhuA12']:SAMPLE;
  const w=boot();
  if(!await ready(w)){ console.log('FAIL: the nav never built'); process.exit(1); }
  let fail=0, totWant=0, totGot=0, tipWant=0, tipGot=0, noteWant=0, noteGot=0;
  let broke=false;
  for(const vol of vols){
    try{ await w.eval('openKey')(vol+'#0','canon'); }catch(e){ console.log('FAIL '+vol+': '+e.message); fail++; continue; }
    for(let k=0;k<60;k++){ await wait(80);
      const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
    if(selftest && !broke){ broke=true; w.eval(OLD_BOLDRANGE); w.eval('render()'); await wait(400);
      console.log('   [selftest] the pre-2026-08-08 _boldRange is back in place'); }
    const c=(w.eval('cache')||{})[vol]||{}; const P=c.paras||[]; const V=c.verse||{};
    let want=0,got=0,inText=0,bad=[];
    w.document.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
      const o=+x.id.slice(('p-'+vol+'-').length); const p=P[o]; if(!p) return;
      const e=V[String(o)];
      const src=e!=null ? lines(e) : [String(p.text||'')];
      let exp=0; for(const s of src){ MARK.lastIndex=0;
        exp+=(String(s).replace(LEAD,'').match(MARK)||[]).length; }
      MARK.lastIndex=0;
      inText+=(String(p.text||'').replace(LEAD,'').match(MARK)||[]).length;
      // !!! EVERY NOTE MUST STILL BE ON THE PAGE SOMEWHERE.  Splitting the block
      // by printed page moves notes out of the end-of-paragraph block, and a
      // note assigned to a page whose rule is never emitted would simply vanish
      // -- silently, because a missing note looks exactly like a paragraph that
      // has none.  This counts the rows drawn against the notes the data holds.
      noteWant+=((c.app||{})[String(o)]||[]).length;
      x.querySelectorAll('.appx > div').forEach(()=>noteGot++);
      let sup=0;
      const notes=new Set(((c.app||{})[String(o)]||[]).map(n=>String(n&&n.n)));
      x.querySelectorAll('sup.fnm').forEach(s=>{ if(s.closest('.appx')) return; sup++;
        if(notes.has(s.textContent)){ tipWant++;
          if(s.getAttribute('title')||s.getAttribute('data-tip')) tipGot++; } });
      want+=exp; got+=sup;
      if(sup<exp && bad.length<10)
        bad.push(`ord ${o} p.${p.printed}: drawn strings carry ${exp}, page shows ${sup}`);
    });
    totWant+=want; totGot+=got;
    const ok=got>=want;
    const d=inText-want;
    const drift=d===0 ? '' : `  (paragraph text carries ${inText}, the drawn strings ${want} — the verse map re-segments ${Math.abs(d)} ${d>0?'away':'in'})`;
    if(!ok){ fail++; console.log(`FAIL ${vol}: ${want} markers in the drawn strings, ${got} on the page${drift}`);
             bad.forEach(b=>console.log('      '+b)); }
    else console.log(`ok   ${vol}: ${want} markers, all drawn${drift}`);
  }
  const tipOk = tipGot>=tipWant;
  if(!tipOk) fail++;
  const noteOk = noteGot===noteWant;
  if(!noteOk) fail++;
  console.log(`\n${vols.length} volumes; ${totWant} markers in the drawn strings, ${totGot} drawn; ${fail} failing`);
  console.log(`${tipWant} markers whose paragraph carries a note with that number; ${tipGot} carry it in a tooltip`+(tipOk?'':'  <-- FAIL'));
  console.log(`${noteWant} notes in the data; ${noteGot} rows drawn`+(noteOk?'':'  <-- FAIL'));
  if(selftest){
    const caught=fail>0;
    console.log(caught
      ? `SELFTEST PASSES: the defect was injected and the gate caught it (${totWant-totGot} markers lost).`
      : 'SELFTEST FAILS: the defect was injected and the gate stayed green. It is measuring nothing.');
    process.exit(caught?0:1);
  }
  process.exit(fail?1:0);
})();

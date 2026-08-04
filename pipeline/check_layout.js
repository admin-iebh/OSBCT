// Per-volume PRESENTATION checker.
//
// pipeline/verify_render_vs_pdf.py compares CONTENT: is every printed line in the
// render, is every rendered block contiguous in the print, is anything rendered
// more often than printed.  It is structurally blind to whether a line is set in
// the right ROLE — a heading rendered as body text, the "Namo tassa…" homage
// folded into a paragraph, a verse number stacked above its verse instead of
// hanging beside it, a vagga opening with the previous vagga's uddāna.  Every one
// of those shipped at 0/0/0/0 and was caught by eye.
//
// This boots the real reader over the real data and asserts the layout rules.
// Add a rule here the moment one is agreed; anything not asserted regresses silently.
//
//   node check_layout.js                # every canon volume in the manifest
//   node check_layout.js 18Khu01 09Ma01 # named volumes
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));

const HOMAGE=/[Nn]amo\s+tassa\s+\S+\s+[Aa]rahato\s+Sammāsambuddhassa/;

// !!! JSDOM DOES NOT FETCH `<script src>`, so the reader this file boots was
// missing `i18n.js` and `panel.js` -- every `TIP(...)` fell through to its
// hard-coded English default and the word panel was absent.  A proof run against
// a reader missing two of its scripts is a proof of a different reader.  They are
// inlined here, from the same bytes the browser would load; `?v=` cache-busting
// query strings are stripped.
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u);
    let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    if(t==null){ console.log('  !! could not inline '+u+' ('+f+')'); return m; }
    return '<script>'+t+'</script>';
  });
}
function boot(){
  const dom=new JSDOM(inlineScripts(fs.readFileSync(R+'/'+(process.env.OSBCT_READER||'reader2.html'),'utf8')),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}

// !!! WHICH LAYER A VOLUME LIVES IN DECIDES BOTH HOW TO OPEN IT AND WHAT TO
// SELECT, and getting this wrong produced a CONFIDENT FALSE FAILURE.
// `openKey(key, layerkind)` takes a SECOND argument; called without it, a
// COMMENTARY volume resolves to `state.active={canon:true}` and the reader
// renders that volume's CANON COUNTERPART.  This file then selected
// `.para.canon` — which is exactly what was on screen — and graded those canon
// paragraphs against the COMMENTARY's verse map.  Every id missed, so every
// numbered paragraph containing a gāthā was flagged: "FAIL 02VinA02 /
// verse-number-stacked :: 127", while `check_layout.js 02Vin02` PASSED on the
// identical render.  Same pixels, opposite verdict, decided only by which verse
// map was loaded.  Found 2026-07-27n.
// Canon paragraphs carry `.para.canon`; commentary `.para.l-A`; subcommentary
// `.para.l-T`.
function layerOf(vol){
  try{
    const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
    for(const L of (nav.layers||[]))
      for(const n of (L.nikayas||[]))
        for(const v of (n.volumes||[]))
          if(v.vol===vol) return L.layer;
  }catch(e){}
  return 'canon';
}
const LAYERKIND={canon:'canon',commentary:'A',subcommentary:'T'};
const LAYERSEL ={canon:'.para.canon',commentary:'.para.l-A',subcommentary:'.para.l-T'};

// !!! A COMMENTARY VOLUME IS NOT REACHABLE THROUGH ONE OPENING.
// `openKey(k,'A')` resolves the commentary paragraph to its CANON counterpart
// and opens THAT canon volume with `state.filter` set to the commentary, so
// what renders is the slice of the commentary hanging off ONE canon volume.
// 02VinA02's 240 paragraphs hang off FOUR of them — 146 off 01Vin01, 43 off
// 02Vin02, 15 off 05Vin05, 3 off 04Vin04 — and the single opening this file
// used to do rendered 45 and called it the volume.
// So walk it once per HOST canon volume and grade the union.  Coverage is
// still reported, because 33 of those 240 paragraphs are reachable from no
// canon volume at all and no amount of opening will render them: the reverse
// map is the whole of what the reader can reach.
function hostsOf(vol, layer){
  if(layer==='canon') return [{canon:vol, key:vol+'#0', row:true}];
  let rev={}; try{ rev=JSON.parse(fs.readFileSync(`${R}/linksk/${vol}.rev.json`,'utf8')); }catch(e){}
  const first={};
  for(const [ord,e] of Object.entries(rev)){
    if(!e||!e.canon) continue;
    const cv=e.canon.split('#')[0];
    if(first[cv]==null || +ord<first[cv]) first[cv]=+ord;
  }
  return Object.keys(first).sort().map(cv=>({canon:cv, key:vol+'#'+first[cv], row:false}));
}

async function openOne(w, vol, kind, h, sel){
  if(h.row){
    // canon: drive the sidebar exactly as a reader would — this also exercises
    // the nav, which is half of what the canon run is for.
    const rows=[...w.document.querySelectorAll('.row')];
    const row=rows.find(r=>r.dataset&&r.dataset.k&&r.dataset.k.startsWith(vol+'#'))
          || rows.find(r=>(r.getAttribute('onclick')||'').includes(vol+'#'));
    if(row) row.click();
    else { try{ w.openKey ? await w.openKey(vol+'#0', kind) : null; }catch(e){} }
  } else {
    // !!! `state.curbook` SURVIVES FROM AN EARLIER CLICK and clamps render() to
    // one book's BOOKSPAN, so a second opening can silently show less than the
    // host volume holds.  Clear it before every host.  (`state` is a top-level
    // `const`, so it is a global binding and not a window property — eval is
    // the only way in from here.)
    try{ w.eval('state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
    try{ await w.openKey(h.key, kind); }catch(e){}
  }
  // Wait for OUR paragraphs, not for a word count.  The old loop waited until
  // #scroll held 2,000 characters, which a host contributing a single
  // commentary paragraph never reaches — so it burned 6.3s and then reported
  // the host as rendering nothing.
  for(let k=0;k<70;k++){
    await wait(90);
    const s=w.document.querySelector('#scroll'); if(!s) continue;
    if([...s.querySelectorAll(sel)].some(p=>(p.id||'').includes('-'+vol+'-'))) break;
    if(s.textContent.length>2000) break;
  }
  return true;
}

// stream-order rules — these depend on what follows what ON ONE PAGE, so they
// are graded per opening, not over the union.
function gradeStream(doc, txt, issues){
  // 3. nothing should open with the previous section's closing mnemonic
  if(/^\s*Tassuddāna/.test(txt.slice(0,400))) issues.push(['opens-with-uddana', txt.slice(0,60)]);
  // 4. a heading must not be duplicated immediately (the "two titles" artifact)
  // ADJACENT IN THE DOM, not merely successive among headings.  The edition
  // really does print one heading twice inside a section with paragraphs
  // between: 39Abhi11 p357-358 sets "Paccayacatukka-hetu" for the
  // Paṭiccādivāra block and again for the Pañhāvāra block, with no heading in
  // between because a parenthetical note carries the Pañhāvāra.  Comparing
  // successive .head elements ignored the body between them and reported that
  // as the "two titles" artifact.  The artifact is two heads with NOTHING
  // between; that is what is tested here.
  const flow=[...doc.querySelectorAll('#scroll .head, #scroll .para')]
    .map(el=>el.classList.contains('head') ? {h:el.textContent.trim()} : {body:true});
  for(let i=1;i<flow.length;i++)
    if(flow[i].h && flow[i-1].h && flow[i].h===flow[i-1].h)
      issues.push(['duplicate-heading', flow[i].h]);
  // 5. apparatus/footnote blocks must not leak into the reading body
  if(/_{6,}/.test(txt)) issues.push(['rule-leaked-into-body','a ______ separator is rendered']);
}

// !!! THE PAGE RULE IS DRAWN WHERE THE PAGE TURNS (2026-08-04).  A paragraph
// carries its page BREAKS now (`pbreak/<VOL>.json`), not one page, so a rule can
// sit INSIDE a paragraph's text.  Three things are asserted, and the second is
// the only one that is not circular:
//   (a) two adjacent rules never carry the same number -- that is the LASTPG
//       guarantee, and it is what a mid-paragraph rule can break by drawing a
//       page the next paragraph then draws again;
//   (b) the letters that FOLLOW a mid-paragraph rule are the letters the PRINTED
//       page opens with.  The fixture is `_xc/pagemark/expect/<VOL>.json`, built
//       from `pline` + the running header and from nothing in the corpus or in
//       `pbreak/`, so this compares the rendered DOM against the printed page;
//   (c) a rule drawn ABOVE a heading group (the `pgPre` path, offset -1) is
//       followed by a heading and not by body text.
// Rules are located by walking the paragraph's own child nodes, so a rule that
// escaped its paragraph is not silently graded as if it were inside one.
const LETT=t=>String(t||'').replace(/[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]/g,'');
const NODIG=t=>String(t||'').replace(/[0-9]/g,'');
// The letters that FOLLOW `node` inside `root`, in document order, skipping every
// `.pgrule`'s own text (its "page NN" is not corpus text and a second rule may
// legitimately stand right after the first).
function textAfter(root, node, want){
  const doc=root.ownerDocument;
  const w=doc.createTreeWalker(root, 0x04 /* TEXT */);
  let seen=false, out='';
  while(w.nextNode()){
    const t=w.currentNode;
    if(!seen){ if(node.contains(t)) seen=true; continue; }
    if(node.contains(t)) continue;
    const pe=t.parentElement;
    if(pe && pe.closest && pe.closest('.pgrule')) continue;
    out+=LETT(t.nodeValue);
    if(out.length>=want) break;
  }
  // a rule with no text nodes of its own still has to start the scan
  if(!seen){
    const w2=doc.createTreeWalker(root, 0x04);
    let after=false;
    while(w2.nextNode()){
      const t=w2.currentNode;
      if(!after){
        if(node.compareDocumentPosition(t)&doc.defaultView.Node.DOCUMENT_POSITION_FOLLOWING) after=true;
        else continue;
      }
      const pe=t.parentElement;
      if(pe && pe.closest && pe.closest('.pgrule')) continue;
      out+=LETT(t.nodeValue);
      if(out.length>=want) break;
    }
  }
  return out;
}

function gradePages(doc, vol, expect, issues){
  const stream=[...doc.querySelectorAll('#scroll .pgrule')];
  let prev=null, adj=0;
  for(const r of stream){
    const n=(r.textContent.match(/page\s+(\d+)/)||[])[1];
    if(n!=null && prev===n) adj++;
    prev=n;
  }
  if(adj) issues.push(['page-rule-repeated', adj+' adjacent rule(s) carry the page already drawn']);
  if(!expect || !Object.keys(expect).length) return;
  let mid=0, midbad=0, midend=0, midshort=0, pre=0, prebad=0;
  for(const p of doc.querySelectorAll('#scroll .para')){
    if(!(p.id||'').includes('-'+vol+'-')) continue;
    // !!! THE RULE IS NO LONGER A DIRECT CHILD OF `.para`.  The spine's verse
    // branch draws its page rules INSIDE the `.gatha` / `.gatha-after` div whose
    // string it cuts, so `:scope > .pgrule` found 14 of 40Abhi12's rules and
    // `nextSibling` found NOTHING after them: 14 of 14 reported misplaced with an
    // EMPTY `got` -- a checker failing because it was looking in the wrong place,
    // not a reader drawing in the wrong place.  Both the search and the text that
    // follows are now taken in DOCUMENT ORDER over the whole paragraph.
    for(const r of p.querySelectorAll('.pgrule')){
      const n=(r.textContent.match(/page\s+(\d+)/)||[])[1]; if(n==null) continue;
      const want=expect[n]; if(!want) continue;
      const got=textAfter(p, r, 80);
      mid++;
      // DIGIT-TOLERANT.  The rendered side carries FOOTNOTE MARKERS the printed
      // line stream does not: `21KhuA02` p.272's only miss was
      // `Piṇḍapātikassabhikkhuno` against `...bhikkhuno1`, the marker digit and
      // nothing else.  Digits are removed from BOTH sides before the compare, so
      // the letters must still agree exactly -- this tolerates a marker, not a
      // different line.
      // COMPARE OVER THE SHORTER OF THE TWO.  `want` is a whole printed LINE and
      // some are shorter than 24 letters; `got` runs on into the next line, so a
      // fixed 24-letter window failed a rule standing exactly where it should
      // (`21KhuA02` p.20: want `Athanaṁmāṇavoāha`, got the same 16 letters and
      // then the following line).  Short lines are counted apart, since a 6-letter
      // anchor discriminates much less than a 24-letter one.
      const _W=NODIG(want), _G=NODIG(got), _L=Math.min(24,_W.length);
      if(_W.length<10) midshort++;
      if(!got.length || !_L || _W.slice(0,_L)!==_G.slice(0,_L)) {
        midbad++;
        if(!got.length) midend++;
        if(midbad<=6) issues.push(['page-rule-misplaced',
          vol+' p.'+n+' want '+want.slice(0,24)+' got '+got.slice(0,24)]);
      }
    }
  }
  // (c) the above-heading rules: emitted outside any .para, immediately before a
  //     heading group.  Counted rather than failed when absent, because whether
  //     the volume has any is a property of its hide map.
  for(const r of stream){
    if(r.closest('.para')) continue;
    const nx=r.nextElementSibling;
    if(nx && /(^|\s)head(\s|$)/.test(nx.className||'')) pre++;
  }
  // A rule with NOTHING after it is the reader's bounded END-OF-PARAGRAPH FLUSH,
  // taken when the printed line could not be located among the drawn strings.  It
  // is still counted as misplaced -- it is late -- but it is reported apart, so a
  // known bounded fallback is never mistaken for a rule drawn on the wrong letters.
  // !!! ASCENDING PAGE ORDER, over THIS VOLUME's paragraphs in document order.
  // The fault this whole repair began from showed itself as `page 73` drawn
  // immediately above `page 63` in 40Abhi12: two records for one ordinal written
  // out of order by the locator's `findany` fallback.  Nothing asserted that, so
  // it shipped.  Restricted to `-vol-` paragraphs because #scroll can hold more
  // than one volume and two layers legitimately interleave their numbering.
  {
    let seq=[], back=0, first=null;
    for(const p of doc.querySelectorAll('#scroll .para')){
      if(!(p.id||'').includes('-'+vol+'-')) continue;
      for(const r of p.querySelectorAll('.pgrule')){
        const v=(r.textContent.match(/page\s+(\d+)/)||[])[1];
        if(v!=null) seq.push(+v);
      }
    }
    for(let i=1;i<seq.length;i++) if(seq[i]<seq[i-1]){ back++; if(first===null) first=seq[i-1]+' then '+seq[i]; }
    if(back) issues.push(['page-rule-out-of-order', back+' descent(s) in '+seq.length+' rules, first '+first]);
    else if(seq.length) issues.push(['#page-rules-ascending', seq.length+' rules, 0 descents']);
  }
  if(mid) issues.push(['#page-rules-inside-paragraphs',
      mid+' checked, '+midbad+' misplaced ('+midend+' flushed at end of paragraph, '
      +(midbad-midend)+' on the wrong letters; '+midshort+' anchored on a line under 10 letters)']);
  if(pre) issues.push(['#page-rules-above-a-heading', String(pre)]);
}

// paragraph rules — graded ONCE over the union of every paragraph any opening
// put on screen, so a volume spread over four hosts is judged as one book.
function gradeParas(paras, vol, vmap, issues){
  // 1. The homage must never be body text WHERE IT OPENS A BOOK. It legitimately
  //    occurs inside narrative — a character utters it ("…udānaṁ udānesi– 'Namo
  //    tassa…'") — so apply the same discriminator the builder uses.
  for(const p of paras){
    const t=p.textContent; const m=t.match(HOMAGE);
    if(!m || p.querySelector('.incipit')) continue;
    const pre=t.slice(Math.max(0,m.index-60), m.index);
    if(/udān|[“”"‘']/.test(pre)) continue;              // quoted speech, not a book head
    if(m.index>0 && !/pāḷi|niṭṭhit|samatt/.test(pre)) continue;
    issues.push(['homage-as-body', p.id||'?', t.slice(Math.max(0,m.index-30), m.index+40)]);
  }
  // 2. a verse number hangs beside its first pāda, never on a line of its own.
  //    APPLIES TO VERSE PARAGRAPHS ONLY.  When this rule was written every
  //    paragraph containing a .gatha was one.  26Khu09 is the first volume
  //    whose units are PROSE that quotes verse part-way through, and there the
  //    number belongs outside, beside the prose it actually numbers.  The verse
  //    map says which is which — a non-empty `groups` is a verse paragraph, an
  //    empty one is prose — and reading it keeps the rule sharp for the volumes
  //    it was written for: a verse paragraph whose number escaped its gāthā is
  //    still flagged even when that paragraph opens with intro prose.
  let outside=0, stacked=0;
  for(const p of paras){
    const f=p.querySelector('.pn'); if(!f) continue;
    // !!! THIS GEOMETRY IS THE CANON RENDERER'S.  Only `kind==='canon'` goes
    // through block()'s verse-map path, where the number is HANDED INTO the
    // first .gatha / .gatha-after and so must be found inside one.  A
    // commentary or Ṭīkā paragraph is built by fmtBold, which returns INLINE
    // html: the <span class="pn"> is followed directly by the paragraph's own
    // text and there is no wrapper for it to be inside.  Testing it by the
    // canon rule reported all 207 rendered paragraphs of 02VinA02 as
    // "prose-number-stacked" — every one of them correct on the page.
    // What is worth asserting there is what the rule actually means: the
    // number must be followed by INLINE content.  `reading:'outline'` swaps
    // the body for a <div class="cmt-outline">, which would strand it.
    if(!p.classList.contains('canon')){
      // !!! `nextElementSibling` SKIPS TEXT NODES, and the thing that follows
      // the number is usually TEXT.  It passed only because `fmtBold` normally
      // emits a <b class="lemma"> first; where a paragraph opens with plain
      // text instead, the next ELEMENT is the apparatus <div> and the rule
      // reported a stacked number on a line that is perfectly inline —
      // 01VinA01 ord88 and ord131, both false.  Test the next NODE.
      let nx=f.nextSibling;
      while(nx && nx.nodeType===3 && !nx.textContent.trim()) nx=nx.nextSibling;
      if(nx && nx.nodeType===1 && /^(DIV|P)$/.test(nx.tagName)) stacked++;
      continue;
    }
    const m=(p.id||'').match(/-(\d+)$/); const e=m?vmap[m[1]]:null;
    const isProse = e && Array.isArray(e.groups) && e.groups.length===0;
    if(isProse){
      // A PROSE UNIT'S number opens its first printed paragraph, INLINE with
      // it, as the page sets " 1. Sotāvadhāne paññā sutamaye ñāṇaṁ.".  It was
      // emitted as a block-level sibling of the prose <div> and so stacked on
      // its own line — a user-reported defect, and one no content gate can see,
      // since every word was present and in the right order.
      if(!f.closest('.gatha-after') && !f.closest('.gatha')) stacked++;
    } else if(p.querySelector('.gatha')){
      if(!f.closest('.gatha')) outside++;
    }
  }
  if(outside) issues.push(['verse-number-stacked', outside+' verse paragraph(s)']);
  if(stacked) issues.push(['prose-number-stacked', stacked+' prose unit(s)']);
}

async function checkVolume(vol, inc){
  let EXPECT={}; try{ EXPECT=JSON.parse(fs.readFileSync('_xc/pagemark/expect/'+vol+'.json','utf8')); }catch(e){}
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  await wait(700);
  const layer=layerOf(vol), kind=LAYERKIND[layer], sel=LAYERSEL[layer];
  const hosts=hostsOf(vol, layer);
  const issues=[]; if(err) issues.push(['js-error',err]);
  const mine=new Map();            // id -> element, the UNION across hosts
  const secSeen=new Set();         // ids of the heading groups actually drawn
  let incEls=0, renders=0, refusal=null, dead=[];
  // !!! CLOSE THE WINDOW.  Each volume boots its own JSDOM; without this the
  // whole run holds every window it ever made and node dies of heap exhaustion
  // partway through the Khuddaka, which looks exactly like a checker that found
  // nothing wrong with the volumes it never reached.
  const done=r=>{ try{ w.close(); }catch(e){} return r; };
  if(!hosts.length)
    return done({vol, skipped:`REFUSING: ${vol} is in layer ${layer} and has no reverse map — `
                        +`the reader has no route into it`, issues:[]});
  for(const h of hosts){
    await openOne(w, vol, kind, h, sel);
    const doc=w.document, scroll=doc.querySelector('#scroll');
    const txt=scroll?scroll.textContent:'';
    const paras=[...doc.querySelectorAll('#scroll '+sel)];
    // !!! THE ONE-LINE ASSERTION THAT WOULD HAVE CAUGHT THE LAYER BUG ABOVE:
    // the paragraphs on screen must BELONG to the volume we were asked about.
    // A checker that cannot reach its subject must REFUSE, not grade.
    const ours=paras.filter(p=>(p.id||'').includes('-'+vol+'-'));
    if(paras.length && !ours.length){
      refusal=refusal||`REFUSING: rendered ${paras.length} paragraph(s), none belonging to ${vol} `
                      +`(first id ${paras[0].id}) — the reader opened a different volume`;
      dead.push(h.canon); continue;
    }
    if(!paras.length){
      // A HOST THAT CONTRIBUTES ONE PARAGRAPH IS NOT AN EMPTY HOST.  The page
      // length is not the test; the presence of this volume's paragraphs is.
      refusal=refusal||(txt.length<500
        ? 'nothing rendered (nav shape not driveable headlessly)'
        : `REFUSING: nothing rendered for ${vol} in layer ${layer}`);
      dead.push(h.canon); continue;
    }
    renders++;
    for(const p of ours) if(!mine.has(p.id)) mine.set(p.id, p);
    for(const e of doc.querySelectorAll('#scroll [id^="sec-'+vol+'-"]')) secSeen.add(e.id);
    incEls=Math.max(incEls, doc.querySelectorAll('#scroll .incipit').length);
    gradeStream(doc, txt, issues);
    gradePages(doc, vol, EXPECT, issues);
  }
  if(!renders) return done({vol, skipped:refusal||'nothing rendered (nav shape not driveable headlessly)', issues:[]});
  if(dead.length) issues.push(['host-rendered-nothing', dead.join(', ')]);

  const paras=[...mine.values()];
  let vmap={}; try{ vmap=JSON.parse(fs.readFileSync(`${R}/verse/${vol}.json`,'utf8')); }catch(e){}
  gradeParas(paras, vol, vmap, issues);

  // AN INCIPIT ANCHORED ON A PARAGRAPH THAT IS NOT ON SCREEN CANNOT BE ON
  // SCREEN.  06VinSg06's homage is anchored at ord0 and NO canon paragraph
  // links to ord0, so the reader has no route to it — reporting that as a
  // layout defect blames the renderer for a hole in the link map.  Scoped the
  // same way rule 6 is: only anchors whose paragraph was actually rendered.
  const incWant=Object.keys(inc||{}).filter(o=>mine.has('p-'+vol+'-'+o));
  if(incWant.length && incEls===0)
    issues.push(['incipit-not-rendered', `${incWant.length} anchored on rendered paragraphs, 0 rendered`]);

  // 6. EVERY HEADING ANCHORED ON A PARAGRAPH THAT IS ON SCREEN MUST BE ON SCREEN.
  // The reader drew `sections/`, `booktitle/` and `incipit/` from
  // cache[state.canonVol] only — which for a commentary volume is the CANON book
  // it hangs off, not the work itself.  So all 74 headings built for 02VinA02
  // were anchored, written to disk, and never drawn: its 240 paragraphs ran
  // together with nothing between them, and no gate said a word.  Anchored-vs-
  // rendered is the assertion that closes that whole class.
  let sec={}; try{ sec=JSON.parse(fs.readFileSync(`${R}/sections/${vol}.json`,'utf8')); }catch(e){}
  const want=Object.keys(sec).filter(o=>mine.has('p-'+vol+'-'+o));
  const gone=want.filter(o=>!secSeen.has('sec-'+vol+'-'+o));
  if(gone.length) issues.push(['sections-not-rendered',
    `${gone.length} of ${want.length} anchored heading group(s) on rendered paragraphs are absent (first ord ${gone[0]})`]);

  // !!! NO SILENT PARTIAL CHECKS, AND NO CRYING WOLF EITHER.  The denominator
  // is the paragraphs the reader is SUPPOSED to draw: corpus minus the `hide`
  // map, which exists precisely to suppress leaked-heading paragraphs.  Judged
  // against the raw corpus count, five shipped Abhidhamma volumes read as 70-92%
  // "PARTIAL" when every paragraph they are meant to show was on screen —
  // 40Abhi12 hides 714 of its 2,413 by design.
  let corpusParas=0, hidden=0;
  try{ corpusParas=JSON.parse(fs.readFileSync(`site/${vol}.json`,'utf8')).paragraphs.length; }catch(e){}
  try{ hidden=Object.keys(JSON.parse(fs.readFileSync(`${R}/hide/${vol}.json`,'utf8'))).length; }catch(e){}
  const denom=Math.max(0, corpusParas-hidden);
  const coverage = denom ? Math.round(100*paras.length/denom) : null;

  return done({vol, paras:paras.length, incEls, issues, coverage, corpusParas:denom, hosts:hosts.length});
}

(async()=>{
  const man=JSON.parse(fs.readFileSync(R+'/manifest.json','utf8')).volumes;
  const argv=process.argv.slice(2);
  const vols=argv.length?argv:Object.keys(man).filter(v=>man[v].layer==='canon').sort();
  // A PARTIAL CHECK IS NOT A PASS.  Say what fraction of the volume was seen.
  const cov=r=>(r.coverage==null?'':(r.coverage<95
      ? `  [PARTIAL: ${r.paras} of ${r.corpusParas} ¶ = ${r.coverage}% examined`
        +`${r.hosts>1?`, ${r.hosts} host volumes walked`:''}]`
      : (r.hosts>1?`  [${r.hosts} host volumes walked]`:'')));
  let bad=0, skipped=0, partial=0;
  for(const v of vols){
    let inc={}; try{ inc=JSON.parse(fs.readFileSync(`${R}/incipit/${v}.json`,'utf8')); }catch(e){}
    const r=await checkVolume(v,inc);
    if(r.skipped){ skipped++; console.log(`  ~  ${v.padEnd(11)} ${r.skipped}`); continue; }
    // rows whose name opens with '#' are COUNTS, not defects: they say how much
    // the page-rule assertion actually examined, which a run that examined
    // nothing would otherwise report as a clean pass.
    const info=r.issues.filter(i=>String(i[0]).startsWith('#'));
    r.issues=r.issues.filter(i=>!String(i[0]).startsWith('#'));
    if(info.length) console.log('       '+info.map(i=>i.join(' ')).join('   '));
    if(r.issues.length){ bad++;
      console.log(`  FAIL ${v.padEnd(11)} ${r.paras} ¶, incipit x${r.incEls}${cov(r)}`);
      const seen=new Set();
      for(const i of r.issues){ const k=i[0]; if(seen.has(k)&&seen.size>0&&i[0]!=='homage-as-body') continue; seen.add(k);
        console.log('        - '+i.join(' :: ').slice(0,120)); }
    } else { if(r.coverage!=null&&r.coverage<95) partial++; console.log(`  ${r.coverage!=null&&r.coverage<95?'PART':'ok  '} ${v.padEnd(11)} ${r.paras} ¶, incipit x${r.incEls}${cov(r)}`); }
  }
  console.log(`\n${vols.length-bad-skipped-partial} clean, ${partial} PARTIAL, ${bad} with layout issues, ${skipped} not driveable headlessly`);
  process.exit(bad?1:0);
})();

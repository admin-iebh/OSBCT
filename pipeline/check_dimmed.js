// THE DIMMED CASE, ASSERTED.
//
// `claude/decision_dim_the_condemned_links.md`, "Before it ships": a gate run
// that exercises the DIMMED case, not just the undimmed one, because
// `claude/start_here_2026-08-04.md` §5 -- an assertion that exercises the
// shallowest case is not an assertion about the feature.
//
// So this does not merely load a page and find no error.  It picks a paragraph
// from EACH condemned family, boots the real reader over the real data, and
// requires FIVE things that can each fail on their own:
//
//   1. a `.jbtn.dim` button exists on that paragraph
//   2. it is NOT disabled -- dimmed means "the evidence is against it", never
//      "there is nothing here", and `.jbtn.none` is the other statement
//   3. its tooltip carries that family's OWN evidence: for `ordinal`, the check
//      by name and both numbers; for `concordance`, the volume the link reaches
//      and the volumes the edition does pair this one with
//   4. the two families' tooltips are NOT THE SAME TEXT, and neither has fallen
//      through to `dim_generic`
//   5. a control paragraph with an UNCONDEMNED link has a jump button and it is
//      NOT dimmed
//
// (4) AND (5) ARE THE TWO THAT MATTER, and they fail in opposite directions.
// Without (5) the whole file passes on a build that dims every link, or none,
// or crashes before drawing any -- the vacuous pass this project has now
// shipped eight times.  Without (4) it passes on a build where both families
// say the same generic sentence, which is a real regression with no visible
// symptom: a generic tooltip is still a tooltip, still sits on a dimmed button,
// and still tells the reader the link opens.  It just stops telling him WHICH
// check fired, which is the entire content of the decision.
//
//   node pipeline/check_dimmed.js
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    if(t==null){ console.log('  !! could not inline '+u); return m; } return '<script>'+t+'</script>';
  });
}
function boot(){
  const dom=new JSDOM(inlineScripts(fs.readFileSync(R+'/reader2.html','utf8')),
    {runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
      w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,
          json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}

// --- pick the fixture from the DATA, never hard-code an ordinal ------------
// A hard-coded paragraph number silently stops testing the feature the moment
// the links are rebuilt and that ordinal is no longer condemned.
//
// EXTENDED 2026-08-07 for the second condemned family.  `why:'concordance'`
// (1,162 visible chips) joins `why:'ordinal'` (316), and the requirement the
// handoff states is that they are dimmed WITH WORDING DISTINCT FROM THE 320.
// "Distinct" is not a property of one tooltip, so it cannot be asserted by
// looking at one: the gate must hold both at once and compare them.  Hence a
// fixture per family rather than the first dim it meets.
//
// Volumes are searched independently per family, because nothing guarantees
// one volume carries both -- requiring that would make the gate skip silently
// on a build where it should run, which is the vacuous pass this file was
// written against.
function fixture(){
  const D='site/reader/linksk';
  const want={ordinal:null,concordance:null};
  let clean=null, cleanVol=null;
  for(const f of fs.readdirSync(D).sort()){
    if(!f.endsWith('.links.json')) continue;
    const vol=f.slice(0,-'.links.json'.length);
    const d=JSON.parse(fs.readFileSync(path.join(D,f),'utf8'));
    for(const si of Object.keys(d).sort((a,b)=>a-b)){
      for(const layer of ['commentary','subcommentary']){
        // Only the FIRST direct entry becomes a chip -- `dimOf` reads r[0].dim.
        // Picking any other would give the gate a fixture the reader never
        // draws, and it would then assert against a button that is not there.
        const ents=(d[si][layer]||[]).filter(e=>e.state==='direct');
        if(!ents.length) continue;
        const e=ents[0], tg = layer==='commentary'?'A':'T';
        if(e.dim){ if(!want[e.dim.why]) want[e.dim.why]={vol,ord:si,tg,d:e.dim}; }
        else if(!clean){ clean={vol,ord:si,tg}; cleanVol=vol; }
      }
    }
    if(want.ordinal&&want.concordance&&clean) break;
  }
  return {ordinal:want.ordinal,concordance:want.concordance,clean,cleanVol};
}

(async()=>{
  const fx=fixture();
  const fails=[];
  for(const fam of ['ordinal','concordance'])
    if(!fx[fam]) fails.push('no `'+fam+'` fixture in any volume -- that family is not being tested at all, '
      +'which is the vacuous pass this file exists to prevent. Run pipeline/mark_condemned.py --write.');
  if(!fx.clean) fails.push('no uncondemned link anywhere -- the discrimination control cannot run');
  if(fails.length){ fails.forEach(f=>console.log('  FAIL '+f)); console.log('\ncheck_dimmed: FAIL'); process.exit(1); }

  for(const fam of ['ordinal','concordance'])
    console.log('fixture '+fam.padEnd(12)+' '+fx[fam].vol+' ¶'+fx[fam].ord+' '+fx[fam].tg+'  '+JSON.stringify(fx[fam].d));
  console.log('fixture '+'control'.padEnd(12)+' '+fx.clean.vol+' ¶'+fx.clean.ord+' '+fx.clean.tg);

  const w=boot();
  await wait(400);
  const btnsOf=(vol,ord)=>{
    const el=w.document.getElementById('p-'+vol+'-'+ord);
    return el?Array.from(el.querySelectorAll('.jbtn')):null;
  };
  const tips={};

  // --- 1-3, ONCE PER FAMILY ------------------------------------------------
  for(const fam of ['ordinal','concordance']){
    const F=fx[fam];
    await w.openKey(F.vol+'#'+F.ord,'canon');
    await wait(700);
    const D=btnsOf(F.vol,F.ord);
    if(!D){ fails.push(fam+': paragraph ¶'+F.ord+' did not render'); continue; }
    const b=D.find(x=>x.classList.contains('dim'));
    if(!b){ fails.push('1. '+fam+': no .jbtn.dim on the condemned paragraph (buttons: '
                       +D.map(x=>x.textContent+'['+x.className+']').join(' ')+')'); continue; }
    if(b.disabled||b.classList.contains('none'))
      fails.push('2. '+fam+': the dimmed button is disabled -- that is the "nothing here" state, not this one');
    const tip=b.getAttribute('title')||b.getAttribute('data-tip')||'';
    tips[fam]=tip;
    // 3. the tooltip must carry THIS family's own evidence, so the reader can
    //    check the accusation instead of taking it on trust.
    if(fam==='ordinal'){
      if(!/sutta/i.test(tip)) fails.push('3. ordinal: tooltip does not name the ordinal check: '+JSON.stringify(tip));
      if(tip.indexOf(String(F.d.says))<0||tip.indexOf(String(F.d.expected))<0)
        fails.push('3. ordinal: tooltip is missing one of the two numbers: '+JSON.stringify(tip));
    }else{
      if(tip.indexOf(F.d.target)<0)
        fails.push('3. concordance: tooltip does not name the volume the link reaches ('+F.d.target+'): '+JSON.stringify(tip));
      if(F.d.kind==='outside'&&(F.d.allowed||[]).length&&tip.indexOf(F.d.allowed[0])<0)
        fails.push('3. concordance: tooltip does not name the volumes the concordance does allow: '+JSON.stringify(tip));
    }
    console.log('  %s tooltip: %s', fam, JSON.stringify(tip));
  }

  // --- 4. THE WORDING MUST DIFFER.  This is the assertion the handoff asks
  //     for, and the only one that catches both families collapsing into
  //     `dim_generic` -- a regression every other check here would pass,
  //     because a generic tooltip is still a tooltip, still sits on a dimmed
  //     button, and still says the link opens.
  if(tips.ordinal&&tips.concordance){
    if(tips.ordinal===tips.concordance)
      fails.push('4. the two condemned families produce IDENTICAL wording -- a wrong volume and a wrong sutta '
                 +'inside the right volume are being told to the reader in the same words');
    else console.log('  wording differs between the two families: ok');
    for(const fam of Object.keys(tips))
      if(/An independent check is against this link|Una comprobaci/i.test(tips[fam]))
        fails.push('4. '+fam+' fell through to dim_generic -- its own branch of dimReason did not fire');
  }

  // --- 5. the control.  Without this the file passes on a build that dims all.
  await w.openKey(fx.clean.vol+'#'+fx.clean.ord,'canon');
  await wait(500);
  const C=btnsOf(fx.clean.vol,fx.clean.ord);
  if(!C) fails.push('5. control paragraph ¶'+fx.clean.ord+' did not render');
  else if(!C.length) fails.push('5. control paragraph has no jump button at all');
  else if(C.every(x=>x.classList.contains('dim')))
    fails.push('5. EVERY button on the control paragraph is dimmed -- the dimming is not discriminating');
  else console.log('  control ¶%s: %s', fx.clean.ord, C.map(x=>x.textContent+'['+x.className+']').join(' '));

  if(fails.length){ fails.forEach(f=>console.log('  FAIL '+f)); console.log('\ncheck_dimmed: FAIL'); process.exit(1); }
  console.log("\ncheck_dimmed: PASS (5 assertions over 2 condemned families, incl. the wording and discrimination controls)");
})();

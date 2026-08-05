// THE DIMMED CASE, ASSERTED.
//
// `claude/decision_dim_the_condemned_links.md`, "Before it ships": a gate run
// that exercises the DIMMED case, not just the undimmed one, because
// `claude/start_here_2026-08-04.md` §5 -- an assertion that exercises the
// shallowest case is not an assertion about the feature.
//
// So this does not merely load a page and find no error.  It picks a paragraph
// the build has marked condemned, boots the real reader over the real data, and
// requires FOUR things that can each fail on their own:
//
//   1. a `.jbtn.dim` button exists on that paragraph
//   2. it is NOT disabled -- dimmed means "the evidence is against it", never
//      "there is nothing here", and `.jbtn.none` is the other statement
//   3. its tooltip names the ordinal check and carries BOTH numbers
//   4. a control paragraph with an UNCONDEMNED link in the same volume has a
//      jump button and it is NOT dimmed
//
// (4) is the part that matters.  Without it the whole file passes on a build
// that dims every link, or none, or crashes before drawing any -- the vacuous
// pass this project has now shipped eight times.
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
function fixture(){
  const D='site/reader/linksk';
  for(const f of fs.readdirSync(D).sort()){
    if(!f.endsWith('.links.json')) continue;
    const vol=f.slice(0,-'.links.json'.length);
    const d=JSON.parse(fs.readFileSync(path.join(D,f),'utf8'));
    let dim=null, clean=null;
    for(const si of Object.keys(d).sort((a,b)=>a-b)){
      for(const layer of ['commentary','subcommentary']){
        for(const e of d[si][layer]||[]){
          if(e.state!=='direct') continue;
          const tg = layer==='commentary'?'A':'T';
          if(e.dim && !dim) dim={ord:si,tg:tg,d:e.dim};
          if(!e.dim && !clean) clean={ord:si,tg:tg};
        }
      }
    }
    if(dim&&clean) return {vol,dim,clean};
  }
  return null;
}

(async()=>{
  const fx=fixture();
  if(!fx){ console.log('FAIL  no volume carries both a condemned and an uncondemned link'); process.exit(1); }
  console.log('fixture: %s  condemned ¶%s %s (says %s, expected %s, name %s)  control ¶%s %s',
    fx.vol, fx.dim.ord, fx.dim.tg, fx.dim.d.says, fx.dim.d.expected, fx.dim.d.name, fx.clean.ord, fx.clean.tg);
  const w=boot();
  await wait(400);
  await w.openKey(fx.vol+'#'+fx.dim.ord,'canon');
  await wait(700);

  const fails=[];
  const btnsOf=(ord)=>{
    const el=w.document.getElementById('p-'+fx.vol+'-'+ord);
    return el?Array.from(el.querySelectorAll('.jbtn')):null;
  };
  const D=btnsOf(fx.dim.ord);
  if(!D) fails.push('condemned paragraph ¶'+fx.dim.ord+' did not render');
  else{
    const b=D.find(x=>x.classList.contains('dim'));
    if(!b) fails.push('1. no .jbtn.dim on the condemned paragraph (buttons: '
                      +D.map(x=>x.textContent+'['+x.className+']').join(' ')+')');
    else{
      if(b.disabled||b.classList.contains('none'))
        fails.push('2. the dimmed button is disabled -- that is the "nothing here" state, not this one');
      const tip=b.getAttribute('title')||b.getAttribute('data-tip')||'';
      if(!/sutta/i.test(tip)) fails.push('3. tooltip does not name the ordinal check: '+JSON.stringify(tip));
      if(tip.indexOf(String(fx.dim.d.says))<0||tip.indexOf(String(fx.dim.d.expected))<0)
        fails.push('3. tooltip is missing one of the two numbers: '+JSON.stringify(tip));
      if(!fails.length) console.log('  dimmed tooltip: %s', JSON.stringify(tip));
    }
  }
  // --- the control.  Without this the file passes on a build that dims all. ---
  await w.openKey(fx.vol+'#'+fx.clean.ord,'canon');
  await wait(500);
  const C=btnsOf(fx.clean.ord);
  if(!C) fails.push('4. control paragraph ¶'+fx.clean.ord+' did not render');
  else if(!C.length) fails.push('4. control paragraph has no jump button at all');
  else if(C.every(x=>x.classList.contains('dim')))
    fails.push('4. EVERY button on the control paragraph is dimmed -- the dimming is not discriminating');
  else console.log('  control ¶%s: %s', fx.clean.ord, C.map(x=>x.textContent+'['+x.className+']').join(' '));

  if(fails.length){ fails.forEach(f=>console.log('  FAIL '+f)); console.log('\ncheck_dimmed: FAIL'); process.exit(1); }
  console.log('\ncheck_dimmed: PASS (4 assertions, incl. the discrimination control)');
})();

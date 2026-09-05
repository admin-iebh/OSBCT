// THE READER'S OWN CONFIGURATION, ASSERTED — the arrival path, not the shortcut.
//
// !!! WHY THIS FILE EXISTS.  `528e4c62` made a canon paragraph draw its whole
// commentary RANGE and was proved in jsdom (27 assertions) and in real Chromium.
// The reader then photographed `18Khu01` `1. Saraṇattaya` drawing ONE commentary
// paragraph and no Read-more control, with `BUILD='44172f08f571'` confirmed by
// view-source in his own browser.  Both statements were true: his TAB was still
// executing `255a05e953fc`, and view-source issues its own request.
//
// But the proofs would not have caught a real regression here either, because
// every one of them reached the state by hand:
//
//     w.eval('state.active.A=true; state.view="single"; state.curbook=null; state.curvagga=null;')
//
// The reader does not have an eval.  He clicks the tree row `1. Saraṇattaya` —
// which sets `cursutta`, `curbook` and `titleVol`, and makes `BOOKSPAN` slice
// the stream — and then presses the `A` button, which goes through
// `ensureBandVols` and `keepPlace`.  The two paths agree today; nothing was
// asserting that they do.  `claude/start_here_2026-08-05.md` §5 names asserting
// the shallowest case as the pattern of the day.  This file asserts the deepest
// one available headlessly: the tree, the button, Spanish, Simple view.
//
// SECTION B asserts the thing that actually reached the reader — that a tab
// which was ALREADY OPEN when a build shipped can find out.
//
//   node pipeline/check_reader_range.js
//   node pipeline/check_reader_range.js --control    # MUST fail
//
// The control is not a mutation of the shipped file: it is `255a05e953fc`
// itself, taken from git, which is the document the reader's browser was
// running.  A control that cannot be produced is reported as such and exits
// non-zero — a control that quietly does not run is not a control.
const fs=require('fs'), path=require('path'), cp=require('child_process');
const {JSDOM,VirtualConsole}=require('jsdom');
const R='site/reader';
const CONTROL=process.argv.includes('--control');
const PREFIX_REV='528e4c62^:site/reader/reader2.html';   // the build the reader photographed

const resolve=u=>{u=String(u).split('?')[0];
  if(u.startsWith('../')) return path.join('site',u.slice(3));
  if(u.startsWith('http')){ try{ u=new URL(u).pathname.replace(/^\//,''); }catch(e){} return path.join(R,u); }
  return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));

let READER=null;
function readerHTML(){
  if(READER!=null) return READER;
  if(!CONTROL){ READER=fs.readFileSync(R+'/reader2.html','utf8'); return READER; }
  try{ READER=cp.execSync('git show '+PREFIX_REV,{encoding:'utf8',maxBuffer:1<<28}); }
  catch(e){ console.log('CONTROL UNAVAILABLE: could not read '+PREFIX_REV+' — '+(e.message||e)
                        +'\nA control that does not run is not a control.'); process.exit(2); }
  return READER;
}

// jsdom does not fetch `<script src>`, so i18n.js — which the page really does
// load — is inlined.  Without it `TIP()` answers from its English fallback and
// every Spanish assertion below is satisfied by absence.
function boot(opts){
  opts=opts||{};
  let html=readerHTML()
    .replace(/<script src="\.\.\/i18n\.js[^"]*"><\/script>/,
             '<script>'+fs.readFileSync('site/i18n.js','utf8')+'</'+'script>')
    .replace(/<script src="\.\.\/searchcore\.js[^"]*"><\/script>/,
             '<script>'+fs.readFileSync('site/searchcore.js','utf8')+'</'+'script>')
    .replace(/<script src="panel\.js[^"]*"( defer)?><\/script>/,'');
  const vc=new VirtualConsole();          // swallow jsdom's navigation notices
  const state={build:opts.build||null, replaced:[], vis:'visible'};
  const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/reader/reader2.html',
    virtualConsole:vc, beforeParse(w){
      w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
      try{ w.localStorage.setItem('osbct-lang',opts.lang||'es'); }catch(e){}
      if(opts.tried!=null) try{ w.sessionStorage.setItem('osbct-reload',opts.tried); }catch(e){}
      Object.defineProperty(w.document,'visibilityState',{get:()=>state.vis,configurable:true});
      Object.defineProperty(w.document,'hidden',{get:()=>state.vis==='hidden',configurable:true});
      w.fetch=(u)=>{
        // `build.json` is served from the harness so a deploy can happen while
        // the tab is open, which is the whole point of section B.
        if(String(u).indexOf('build.json')>=0){
          const b=state.build;
          return Promise.resolve({ok:b!=null,status:b!=null?200:404,
            json:()=>Promise.resolve({build:b}),text:()=>Promise.resolve(JSON.stringify({build:b}))});
        }
        const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,
          json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};
    }});
  const w=dom.window;
  // observe the decision instead of navigating (jsdom cannot navigate anyway)
  w.reloadOnto=(b)=>state.replaced.push(b);
  return {w,state};
}

let pass=0,fail=0;
function ok(name,cond,got){ if(cond){pass++;console.log('  ok   '+name);}
  else {fail++;console.log('  FAIL '+name+'   got: '+JSON.stringify(got));} }
const visible=el=>!el.closest('[hidden]');
const txt=el=>(el.textContent||'').replace(/\s+/g,' ').trim();

// ---------------------------------------------------------------- SECTION A
async function sectionA(){
  console.log('A. THE READER\'S CONFIGURATION: tree row "1. Saraṇattaya", then the A button, Spanish, Simple');
  const {w}=boot({lang:'es',build:'IGNORED-IN-A'});
  const errs=[]; w.addEventListener('error',e=>errs.push(e.message));
  const doc=w.document;
  await wait(1500);

  // the nav is lazy: the Khuddaka rows have to be opened before the sutta exists
  let rows=[...doc.querySelectorAll('.row')];
  for(const r of rows.filter(r=>/Khuddaka/i.test(r.textContent||'')).slice(0,4)){ r.click(); await wait(450); }
  rows=[...doc.querySelectorAll('.row')];
  const row=rows.find(r=>txt(r)==='1. Saraṇattaya');
  ok('the tree carries a row labelled exactly "1. Saraṇattaya"', !!row, rows.length+' rows');
  if(!row){ w.close(); return; }
  row.click(); await wait(2600);

  // THE STATE THE TREE LEAVES, WHICH THE OLD PROOFS ERASED.  `state.curbook`
  // makes BOOKSPAN slice the stream and `state.titleVol` names the header;
  // `prove.js` set `curbook=null; curvagga=null` before rendering, so nothing
  // ever exercised the configuration the reader is actually in.
  ok('the tree sets canonVol=18Khu01', w.eval('state.canonVol')==='18Khu01', w.eval('state.canonVol'));
  ok('the tree sets cursutta=18Khu01#0 and curbook=18Khu01#0 (NOT null)',
     w.eval('String(state.cursutta)')==='18Khu01#0' && w.eval('String(state.curbook)')==='18Khu01#0',
     w.eval('String(state.cursutta)+" / "+String(state.curbook)'));
  ok('the view is Simple and only P is lit', w.eval('state.view')==='single'
     && w.eval('JSON.stringify(state.active)')==='{"canon":true,"A":false,"T":false}',
     w.eval('state.view+" "+JSON.stringify(state.active)'));
  ok('the interface is Spanish', w.eval('String(typeof osbctLang!=="undefined"?osbctLang():"NO-I18N")')==='es',
     w.eval('String(typeof osbctLang!=="undefined"?osbctLang():"NO-I18N")'));

  // PRESS THE BUTTON.  Not `state.active.A=true`: the handler clears
  // `state.filter`, calls `ensureBandVols` and re-renders through `keepPlace`.
  const ab=[...doc.querySelectorAll('.lbtn')].find(b=>b.dataset.k==='A');
  ok('the layer bar has an A button', !!ab, !!ab);
  ab.click(); await wait(3200);
  ok('pressing A leaves P and A both on', w.eval('JSON.stringify(state.active)')==='{"canon":true,"A":true,"T":false}',
     w.eval('JSON.stringify(state.active)'));
  ok('no javascript errors', errs.length===0, errs.slice(0,2));

  // the header the reader photographed
  ok('the header reads "Saraṇattaya · 18Khu01 · 1869 ¶"',
     /^Saraṇattaya18Khu01 · 1869 ¶$/.test(txt(doc.querySelector('#doctitle'))), txt(doc.querySelector('#doctitle')));

  const c0=doc.getElementById('p-18Khu01-0');
  ok('canon ¶0 is on the page', !!c0, !!c0);
  if(!c0){ w.close(); return; }
  const band=c0.parentElement.querySelector('.subwrap.a');
  ok('canon ¶0 has an Aṭṭhakathā band', !!band, !!band);
  if(!band){ w.close(); return; }

  const ords=[...band.querySelectorAll('.para[id]')].map(p=>p.id)
    .map(id=>{ const m=/^p-20KhuA01-(\d+)$/.exec(id); return m?+m[1]:id; });
  ok('the band draws 20KhuA01 #9..#27 — the whole printed Saraṇattaya section',
     ords.join(',')===Array.from({length:19},(_,k)=>9+k).join(','), ords);
  ok('the run is 19 paragraphs, not the 1 the reader photographed', ords.length===19, ords.length);
  ok('it STOPS at "Saraṇattayavaṇṇanā niṭṭhitā." — #28 is not in it', ords.indexOf(28)<0, ords[ords.length-1]);

  const vis=[...band.querySelectorAll('.para[id]')].filter(visible);
  ok('two paragraphs are shown, the rest behind the control', vis.length===2, vis.map(p=>p.id));
  const rest=band.querySelector('.runrest');
  ok('the tail is hidden, not absent', !!rest && rest.hasAttribute('hidden')
     && rest.querySelectorAll('.para').length===17, rest?rest.querySelectorAll('.para').length:null);
  const btn=band.querySelector('button.runmore');
  ok('a Read-more control is drawn — IN SPANISH — naming 17',
     !!btn && btn.textContent==='Leer más — 17 párrafos más de esta sección', btn&&btn.textContent);
  if(btn){
    btn.dispatchEvent(new w.Event('click',{bubbles:true})); await wait(140);
    ok('opening it shows all 19', [...band.querySelectorAll('.para[id]')].filter(visible).length===19,
       [...band.querySelectorAll('.para[id]')].filter(visible).length);
    ok('and the control says "Mostrar menos"', btn.textContent==='Mostrar menos', btn.textContent);
    btn.dispatchEvent(new w.Event('click',{bubbles:true})); await wait(140);
    ok('closing it returns to two', [...band.querySelectorAll('.para[id]')].filter(visible).length===2,
       [...band.querySelectorAll('.para[id]')].filter(visible).length);
  } else { fail+=3; console.log('  FAIL (3 collapse assertions skipped: no control drawn)'); }

  // the sequence the screenshot shows AROUND the band
  const flow=[...doc.querySelectorAll('#scroll .para[id], #scroll .head, #scroll .uddana')]
    .map(el=>el.id||txt(el).slice(0,40));
  const i9=flow.indexOf('p-20KhuA01-9');
  ok('the canon colophon "Saraṇattayaṁ" and then "2. Dasasikkhāpada" follow the band, as printed',
     i9>=0 && flow.slice(i9,i9+30).some(x=>/^Saraṇattayaṁ/.test(x))
     && flow.slice(i9,i9+30).some(x=>/^2\. Dasasikkhāpada/.test(x)), flow.slice(i9,i9+6));

  // the duplication `528e4c62` also removed: `18Khu01` ¶1-¶5 all point at
  // `20KhuA01#39`, and before the range work each of them drew it
  const all=[...doc.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  ok('20KhuA01#39 is on the page exactly once (¶1-¶5 all name it)',
     all.filter(id=>id==='p-20KhuA01-39').length===1, all.filter(id=>id==='p-20KhuA01-39').length);
  ok('no paragraph is drawn twice anywhere on the page',
     new Set(all).size===all.length, all.filter((x,k)=>all.indexOf(x)!==k).slice(0,4));
  ok('the canon spine is intact under the book span',
     all.filter(id=>/^p-18Khu01-/.test(id)).length>0, all.filter(id=>/^p-18Khu01-/.test(id)).length);
  w.close();
}

// ---------------------------------------------------------------- SECTION B
async function sectionB(){
  console.log('\nB. A TAB THAT WAS ALREADY OPEN WHEN THE BUILD SHIPPED CAN FIND OUT');
  const OWN=(readerHTML().match(/const BUILD='([0-9a-f]+)'/)||[])[1];
  ok('the reader carries a build stamp', !!OWN, OWN);

  // B1 — fresh tab, a newer build is published: reload once, towards the
  // PUBLISHED build, and record THAT (not the stale page's own stamp).
  {
    const {w,state}=boot({build:'ffffffffffff'});
    await wait(900);
    ok('B1 a fresh stale tab reloads once, onto the published build',
       state.replaced.length===1 && state.replaced[0]==='ffffffffffff', state.replaced);
    ok('B1 the attempt is recorded against the build aimed AT',
       w.sessionStorage.getItem('osbct-reload')==='ffffffffffff', w.sessionStorage.getItem('osbct-reload'));
    w.close();
  }

  // B2 — we already tried to reach that build and came back stale anyway.
  // Do not loop; SAY SO.  Silence here is what sent the reader back with a
  // photograph of a fault that had already shipped.
  {
    const {w,state}=boot({build:'ffffffffffff',tried:'ffffffffffff'});
    await wait(900);
    ok('B2 a second attempt at the same build is not made', state.replaced.length===0, state.replaced);
    const bar=w.document.getElementById('newbuild');
    ok('B2 the tab says it is not the published version', !!bar && !bar.hidden, bar?bar.hidden:'no #newbuild');
    ok('B2 and says it in Spanish', !!bar && /no es la versión publicada/.test(txt(bar)), bar?txt(bar).slice(0,60):null);
  w.close();
  }

  // B3 — THE READER'S CASE.  The tab loaded when it WAS current; the deploy
  // happened afterwards.  Nothing in the old code could ever tell it.
  {
    const {w,state}=boot({build:OWN});
    await wait(900);
    const bar=w.document.getElementById('newbuild');
    ok('B3 a current tab is left alone', state.replaced.length===0 && !!bar && bar.hidden,
       state.replaced.concat([bar?bar.hidden:'no #newbuild']));
    state.build='eeeeeeeeeeee';                     // a deploy, with the tab open
    state.vis='hidden'; w.document.dispatchEvent(new w.Event('visibilitychange'));
    await wait(200);
    ok('B3 a hidden tab does not poll', !!bar && bar.hidden, bar?'polled while hidden':'no #newbuild');
    state.vis='visible'; w.document.dispatchEvent(new w.Event('visibilitychange'));
    await wait(600);
    const bar2=w.document.getElementById('newbuild');
    ok('B3 coming back to the tab discovers the new build and says so',
       !!bar2 && !bar2.hidden && /versión publicada/.test(txt(bar2)), bar2?[bar2.hidden,txt(bar2).slice(0,40)]:'no #newbuild');
    ok('B3 and it does NOT reload the page the reader is reading', state.replaced.length===0, state.replaced);
    const b=bar2&&!bar2.hidden&&bar2.querySelector('button');
    ok('B3 the control is offered, and taking it loads the published build', !!b, !!b);
    if(b){ b.dispatchEvent(new w.Event('click',{bubbles:true})); await wait(120);
      ok('B3 the control aims at the published build', state.replaced.join()==='eeeeeeeeeeee', state.replaced); }
    else { fail++; console.log('  FAIL B3 control target (no button)'); }
    w.close();
  }

  // B4 — the disarming the old guard did to itself: it wrote the STALE page's
  // own stamp, so `getItem===BUILD` matched for ever in the tab it had failed
  // to update, and every later build was ignored too.
  {
    const {w,state}=boot({build:'dddddddddddd',tried:OWN});
    await wait(900);
    ok('B4 a tab that recorded its OWN stamp still reaches a later build',
       state.replaced.join()==='dddddddddddd', state.replaced);
    w.close();
  }
}

(async()=>{
  console.log(CONTROL
    ? 'CONTROL RUN — driving '+PREFIX_REV+', the build the reader photographed. Failures are the point.\n'
    : 'node pipeline/check_reader_range.js\n');
  await sectionA();
  await sectionB();
  console.log('\n'+pass+' passed, '+fail+' failed');
  if(CONTROL){
    if(fail===0){ console.log('CONTROL DID NOT FAIL — the assertions do not discriminate. Treat as a failure.'); process.exit(1); }
    console.log('control failed as required'); process.exit(0);
  }
  process.exit(fail?1:0);
})();

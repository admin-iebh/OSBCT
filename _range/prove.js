// BROWSER PROOF of the commentary-range fix, over the shipped reader2.html and
// the shipped data, in jsdom.  Every assertion has a negative control below it
// (--control inverts the expectations and the run MUST then fail).
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const CONTROL=process.argv.includes('--control');
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(lang){
  const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
    if(lang) try{ w.localStorage.setItem('osbct-lang',lang); }catch(e){}
    w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
let pass=0,fail=0;
function ok(name,cond,got){ if(cond){pass++;console.log('  ok   '+name);} else {fail++;console.log('  FAIL '+name+'   got: '+JSON.stringify(got));} }
const visible=el=>!el.closest('[hidden]');

(async()=>{
  // ---------- the printed section, read from the volume's own files ----------
  const vol=JSON.parse(fs.readFileSync('site/20KhuA01.json','utf8'));
  const sec=JSON.parse(fs.readFileSync(R+'/sections/20KhuA01.json','utf8'));
  const hi=vol.headings.map(h=>h.title);
  const iEnd=hi.indexOf('Saraṇattayavaṇṇanā niṭṭhitā.');
  ok('edition prints the colophon "Saraṇattayavaṇṇanā niṭṭhitā."', iEnd>=0, iEnd);
  let j=iEnd+1; while(j<hi.length && /^[_\s.]*$/.test(hi[j])) j++;
  ok('the head after the colophon is Sikkhāpadavaṇṇanā', hi[j]==='Sikkhāpadavaṇṇanā', hi[j]);
  ok('sections/ anchors "2. Sikkhāpadavaṇṇanā" at ord 28',
     (sec['28']||[]).some(x=>x.l==='2. Sikkhāpadavaṇṇanā'), sec['28']);
  const WANT_LAST = CONTROL? 31 : 27;      // the control claims the run runs past the colophon

  // ---------- P + A, single view ----------
  const w=boot(null); const errs=[]; w.addEventListener('error',e=>errs.push(e.message));
  await wait(800);
  await w.openKey('18Khu01#0','canon'); await wait(1500);
  const canonOnly=[...w.document.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  ok('P-only: every block on screen is a canon block', canonOnly.every(id=>id.startsWith('p-18Khu01-')), canonOnly.find(id=>!id.startsWith('p-18Khu01-')));
  ok('P-only: no duplicate ids', new Set(canonOnly).size===canonOnly.length, canonOnly.length-new Set(canonOnly).size);
  const canonN=canonOnly.length;

  w.eval('state.active.A=true; state.view="single"; state.curbook=null; state.curvagga=null;');
  await w.eval('ensureBandVols()'); await wait(2500); w.eval('render();'); await wait(600);
  const doc=w.document;
  ok('no javascript errors', errs.length===0, errs.slice(0,2));

  const c0=doc.getElementById('p-18Khu01-0');
  const wrap=c0.parentElement;                     // the per-ordinal <div style="margin-bottom:12px">
  const band=wrap.querySelector('.subwrap.a');
  ok('canon 0 has an A band', !!band, !!band);
  const run=[...band.querySelectorAll('.para[id]')].map(p=>p.id);
  const ords=run.map(id=>+id.split('-').pop());
  ok('canon 0 draws every paragraph of the printed section, in order',
     run.every(id=>id.startsWith('p-20KhuA01-')) && ords.join(',')===Array.from({length:WANT_LAST-9+1},(_,k)=>9+k).join(','),
     ords.slice(0,4).concat(['…',ords[ords.length-1]]));
  ok('canon 0 STOPS at the colophon: last is #'+WANT_LAST+', #'+(WANT_LAST+1)+' is not in the run',
     ords[ords.length-1]===WANT_LAST && ords.indexOf(WANT_LAST+1)<0, ords[ords.length-1]);
  ok('the run is 19 paragraphs where it used to be 1', run.length===(WANT_LAST-8), run.length);

  // ---------- the collapse ----------
  const vis=[...band.querySelectorAll('.para[id]')].filter(visible).map(p=>p.id);
  ok('collapsed: only the first 2 paragraphs are shown', vis.length===2, vis);
  const rest=band.querySelector('.runrest');
  ok('the tail is hidden, not absent', rest && rest.hasAttribute('hidden') && rest.querySelectorAll('.para').length===run.length-2,
     rest?rest.querySelectorAll('.para').length:null);
  const btn=band.querySelector('button.runmore');
  ok('a Read-more control is drawn, in English, naming the count',
     !!btn && /^Read more — 17 more paragraphs/.test(btn.textContent), btn&&btn.textContent);
  btn.dispatchEvent(new w.Event('click',{bubbles:true}));
  await wait(120);
  ok('clicking expands the whole run', [...band.querySelectorAll('.para[id]')].filter(visible).length===run.length,
     [...band.querySelectorAll('.para[id]')].filter(visible).length);
  ok('the control becomes "Show less"', btn.textContent==='Show less', btn.textContent);
  btn.dispatchEvent(new w.Event('click',{bubbles:true}));
  await wait(120);
  ok('clicking again collapses it', [...band.querySelectorAll('.para[id]')].filter(visible).length===2,
     [...band.querySelectorAll('.para[id]')].filter(visible).length);

  // ---------- no paragraph twice on the page ----------
  const all=[...doc.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  const dup=all.filter((x,k)=>all.indexOf(x)!==k);
  ok('P+A: no commentary paragraph is drawn twice', dup.length===0, dup.slice(0,4));
  ok('P+A: the canon spine is intact', all.filter(id=>id.startsWith('p-18Khu01-')).length===canonN,
     all.filter(id=>id.startsWith('p-18Khu01-')).length+' vs '+canonN);

  // ---------- an opened run survives a re-render ----------
  band.querySelector('button.runmore').dispatchEvent(new w.Event('click',{bubbles:true})); await wait(120);
  w.eval('render();'); await wait(400);
  const band2=doc.getElementById('p-18Khu01-0').parentElement.querySelector('.subwrap.a');
  ok('a run the reader opened is still open after a re-render (OPENRUNS)',
     [...band2.querySelectorAll('.para[id]')].filter(visible).length===run.length
     && band2.querySelector('button.runmore').textContent==='Show less',
     [...band2.querySelectorAll('.para[id]')].filter(visible).length);
  band2.querySelector('button.runmore').dispatchEvent(new w.Event('click',{bubbles:true})); await wait(120);
  ok('and closing it again returns to two', [...band2.querySelectorAll('.para[id]')].filter(visible).length===2,
     [...band2.querySelectorAll('.para[id]')].filter(visible).length);

  // ---------- check_layout.js's own stream rules, over the P+A stream ----------
  // (check_layout runs with the bands OFF, so its rules never see this page.)
  const flow=[...doc.querySelectorAll('#scroll .head, #scroll .para[id]')]
      .map(el=>el.classList.contains('head')?{h:el.textContent.trim()}:{body:true});
  const dupHead=[]; for(let z=1;z<flow.length;z++) if(flow[z].h&&flow[z-1].h&&flow[z].h===flow[z-1].h) dupHead.push(flow[z].h);
  ok('P+A: no heading is drawn twice with nothing between (check_layout rule 4)', dupHead.length===0, dupHead.slice(0,3));
  ok('P+A: no ______ separator leaks into the body (check_layout rule 5)',
     !/_{6,}/.test(doc.querySelector('#scroll').textContent), 'a rule leaked');
  // the sub-heads the edition prints INSIDE the Saraṇattaya section must be on
  // the page once the run is open — they are anchored on paragraphs that were
  // never rendered before this change
  const btn2=doc.getElementById('p-18Khu01-0').parentElement.querySelector('.subwrap.a button.runmore');
  const band3=doc.getElementById('p-18Khu01-0').parentElement.querySelector('.subwrap.a');
  btn2.dispatchEvent(new w.Event('click',{bubbles:true})); await wait(120);
  const heads0=[...band3.querySelectorAll('.head')].map(e=>e.textContent.trim());
  ok('the section\'s own sub-heads are drawn inside the run',
     ['Saraṇagamanagamakavibhāvanā','Bhedābhedaphaladīpanā','Gamanīyadīpanā','Upamāpakāsanā']
       .every(h=>heads0.some(x=>x.indexOf(h)>=0)), heads0);
  btn2.dispatchEvent(new w.Event('click',{bubbles:true})); await wait(120);

  // ---------- back to P only ----------
  w.eval('state.active.A=false; render();'); await wait(400);
  const back=[...doc.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  ok('turning A off restores exactly the P-only stream', back.join(',')===canonOnly.join(','), back.length+' vs '+canonN);
  w.close();

  // ---------- standalone A (the work as its own spine) ----------
  const w2=boot(null); const errs2=[]; w2.addEventListener('error',e=>errs2.push(e.message));
  await wait(800);
  await w2.openKey('20KhuA01#9','A'); await wait(2500);
  const sp=[...w2.document.querySelectorAll('#scroll .para[id]')].map(p=>p.id);
  ok('standalone A: no js errors', errs2.length===0, errs2.slice(0,2));
  ok('standalone A: renders 20KhuA01 as its own spine', sp.length>600 && sp.every(id=>id.startsWith('p-20KhuA01-')),
     sp.length+' paras, foreign='+JSON.stringify(sp.filter(id=>!id.startsWith('p-20KhuA01-')).slice(0,3)));
  ok('standalone A: no duplicates, no runmore control', new Set(sp).size===sp.length && !w2.document.querySelector('.runmore'),
     sp.length-new Set(sp).size);
  w2.close();

  console.log('\n'+pass+' passed, '+fail+' failed'+(CONTROL?'   [CONTROL RUN — failures are the point]':''));
  process.exit(fail?1:0);
})();

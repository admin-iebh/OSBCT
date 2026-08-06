// WHERE A TOOLTIP GOES — asserted on the geometry, because jsdom has no layout.
//
// The reader reported (2026-08-05, screenshot) that hovering the Abhidhāna tab
// drew its tooltip straight over the panel's own `wl_eval` notice.  Cause: one
// `#tiptip` node placed at `element.bottom + 7`, flipping up only when the
// VIEWPORT had no room — and the word panel is a narrow column whose tab strip
// sits at the top, so "below" is always its own first line of content.
//
// !!! A GATE THAT HOVERED THE TAB AND READ THE TOOLTIP'S `top` WOULD BE
// VACUOUS.  jsdom implements no layout: every getBoundingClientRect is
// {0,0,0,0}, so such a gate compares 0 with 0 and passes on any rule at all —
// including the broken one.  That is the eighth instance of the pattern this
// project keeps paying for.  So `tipPlace` is a pure function of four
// rectangles and this feeds it numbers.
//
//   node pipeline/check_tipplace.js
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    return t==null?m:'<script>'+t+'</script>'; });
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
let pass=0, fail=0;
const ok=(what,cond,got)=>{ if(cond){pass++;console.log('  ok   '+what);}
                            else {fail++;console.log('  FAIL '+what+'   got: '+JSON.stringify(got));} };
const rect=(l,t,w,h)=>({left:l,top:t,width:w,height:h,right:l+w,bottom:t+h});

(async()=>{
  const w=boot(); await wait(300);
  // `w.eval` on an undeclared identifier THROWS a ReferenceError rather than
  // returning undefined, so the absent case has to be caught or the gate dies
  // with a stack trace instead of a verdict.
  let place=null; try{ place=w.eval('tipPlace'); }catch(e){}
  if(typeof place!=='function'){ console.log('  FAIL tipPlace is not defined — the rule is absent\n\n0 passed, 1 failed'); process.exit(1); }
  const VW=1400, VH=900, GAP=7, M=6;

  // the reported case: a tab near the TOP of the panel, plenty of room both ways
  const tab=rect(1240, 120, 90, 22), box=rect(0,0,260,52);

  let p=place(tab, box, VW, VH, false);
  ok('the old behaviour still exists: above=false puts it BELOW',
     p.top===tab.bottom+GAP, p);
  const below=p.top;

  p=place(tab, box, VW, VH, true);
  ok('1. above=true puts it ABOVE the element', p.top===tab.top-GAP-box.height, p);
  ok('1. and that is a different answer from the old rule', p.top!==below, [p.top,below]);
  ok('1. it clears the element entirely — no overlap',
     p.top+box.height <= tab.top-1, [p.top+box.height, tab.top]);

  // 2. the preference yields when its own side has no room
  const atTop=rect(1240, 8, 90, 22);
  p=place(atTop, box, VW, VH, true);
  ok('2. no room above: falls back BELOW rather than off-screen',
     p.top===atTop.bottom+GAP, p);
  const atBottom=rect(1240, VH-40, 90, 22);
  p=place(atBottom, box, VW, VH, false);
  ok('2. no room below: still flips ABOVE, as it always did',
     p.top===atBottom.top-GAP-box.height, p);

  // 3. never off the viewport, whichever way it is asked
  const tall=rect(1240, 300, 90, 22), huge=rect(0,0,260,VH);
  for(const a of [true,false]){
    p=place(tall, huge, VW, VH, a);
    ok('3. an over-tall tooltip is clamped to the margin (above='+a+')', p.top>=M, p);
  }

  // 4. horizontal clamping is unchanged — the panel sits at the right edge
  p=place(rect(VW-30, 200, 24, 22), box, VW, VH, true);
  ok('4. clamped inside the right edge', p.left+box.width<=VW-M, [p.left+box.width, VW-M]);
  p=place(rect(2, 200, 24, 22), box, VW, VH, true);
  ok('4. clamped inside the left edge', p.left>=M, p.left);

  // 5. WIRED IN: the panel opts in without naming itself at the call site
  const doc=w.document;
  const el=doc.createElement('div'); el.setAttribute('data-tip','x');
  const host=doc.createElement('div'); host.id='wl'; host.appendChild(el);
  doc.body.appendChild(host);
  ok('5. an element inside #wl is recognised as preferring above',
     !!(el.closest && el.closest('#wl')), true);
  const out=doc.createElement('div'); out.setAttribute('data-tip','x'); doc.body.appendChild(out);
  ok('5. and one outside it is not', !out.closest('#wl'), false);
  out.setAttribute('data-tip-above','');
  ok('5. anything may opt in with data-tip-above', out.hasAttribute('data-tip-above'), true);

  console.log('\n%d passed, %d failed', pass, fail);
  process.exit(fail?1:0);
})();

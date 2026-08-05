// WHERE THE "READ MORE" CONTROL GOES — the rule, asserted directly.
//
// `check_reader_range.js` proves the control is WIRED IN, on one fixture
// (18Khu01 ¶0 -> 20KhuA01 #9..#27, 2 shown / 17 hidden).  It cannot prove the
// RULE, because one run exercises one outcome, and the rule's whole purpose is
// to behave differently on runs of different shape.  Anything not asserted
// regresses silently (check_layout.js's own header), so the rule gets its own
// file.
//
// The cut is a CHARACTER BUDGET over whole paragraphs, not a paragraph count.
// Measured over 89,512 corpus paragraphs: median 237 chars, p90 1,891, p99
// 18,406, max 191,160 -- so a count of two was showing anywhere from ~200
// characters to most of a book.
//
// Every case below distinguishes the NEW rule from the OLD one, or it is not
// worth running:  under `RUNOPEN=2` cases 1, 2 and 4 all give a different
// answer.  A gate that would pass on the code it replaced asserts nothing.
//
//   node pipeline/check_runcut.js
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

(async()=>{
  const w=boot(); await wait(400);
  if(typeof w.runShow!=='function'){ console.log('FAIL runShow is not exposed — the rule cannot be tested'); process.exit(1); }
  // !!! A TOP-LEVEL `const` IS NOT A WINDOW PROPERTY.  `let`/`const` at the top
  // of a classic script go into the global LEXICAL environment, not onto the
  // global object, so `w.RUNCHARS` and `w.cache` are both `undefined` while the
  // identifiers resolve perfectly inside the page.  Reading them through
  // `w.eval` at global scope is how a gate sees the real values instead of
  // silently testing `undefined` -- which is exactly the vacuous pass this file
  // exists to avoid.  `cache` comes back as the live object, so seeding it here
  // seeds the reader's own.
  const B=w.eval('RUNCHARS'); const cache=w.eval('cache');
  ok('the budget is a stated constant', typeof B==='number'&&B>0, B);

  // a synthetic volume, so the lengths under test are exactly the lengths meant
  const mk=(lens)=>{ cache['ZZTest']={paras:lens.map(n=>({text:'x'.repeat(n)})),bold:{},app:{}};
                     return lens.map((_,i)=>({key:'ZZTest#'+i})); };
  const chars=(grp,n)=>grp.slice(0,n).reduce((s,t)=>s+w.paraLen(t.key),0);

  // 1. SHORT paragraphs: the rule must show MORE than the old two.
  let g=mk(Array(19).fill(100)), n=w.runShow(g);
  ok('1. 19 short ¶ (100 chars): shows more than the old fixed 2', n>2, n);
  ok('1. and stops at the budget', chars(g,n)<=B && chars(g,n+1)>B, [chars(g,n),B]);

  // 2. ONE paragraph longer than the whole budget: still shown, never zero.
  g=mk([50000,300,300]); n=w.runShow(g);
  ok('2. a single over-budget ¶ is still shown (at least one, always)', n===1, n);

  // 3. LONG paragraphs: the second must not be added past the budget.
  g=mk([1200,1200,1200,1200]); n=w.runShow(g);
  ok('3. 4 long ¶: only the first fits', n===1, n);
  ok('3. and three are hidden, so a control is drawn', g.length-n===3, g.length-n);

  // 4. A tail of exactly one that would have fitted is NOT put behind a control.
  g=mk([1400,200]); n=w.runShow(g);
  ok('4. never a control that hides a single ¶ which fits', n===2, n);
  // ...but a single over-budget tail IS hidden: the guard is about cost, not size.
  g=mk([1400,50000]); n=w.runShow(g);
  ok('4. a single tail bigger than the budget stays behind the control', n===1, n);

  // 5. whole paragraphs only -- never a cut inside one
  g=mk([700,700,700]); n=w.runShow(g);
  ok('5. cuts only between paragraphs', Number.isInteger(n)&&n>=1&&n<=g.length, n);

  // 6. the real fixture is unchanged, so check_reader_range still asserts truth
  const P=JSON.parse(fs.readFileSync('site/20KhuA01.json','utf8')).paragraphs;
  cache['ZZReal']={paras:P.slice(9,28),bold:{},app:{}};
  const real=P.slice(9,28).map((_,i)=>({key:'ZZReal#'+i}));
  ok('6. the 18Khu01 fixture still shows 2 of 19', w.runShow(real)===2, w.runShow(real));

  console.log('\n%d passed, %d failed', pass, fail);
  process.exit(fail?1:0);
})();

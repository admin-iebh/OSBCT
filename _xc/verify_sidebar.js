// Regression guard for the sidebar that could never open on a phone
// (2026-07-31c). JSDOM does not evaluate media queries, so this reads the two
// rules out of reader2.html and simulates them directly: at each width, walk
// the ☰ toggle and the on-select auto-close and assert what the reader sees.
const fs=require('fs');
const html=fs.readFileSync('site/reader/reader2.html','utf8');
const wideNosb = /@media\(min-width:861px\)\{body\.nosb\{[^}]*\}body\.nosb \.side\{display:none\}\}/.test(html);
const narrowHide = /@media\(max-width:860px\)\{[\s\S]{0,400}?body:not\(\.showsb\) \.side\{display:none\}\}/.test(html);
// Strip every @media block (brace-balanced) before looking for a TOP-LEVEL
// `body.nosb .side` rule — a naive regex matches the rule INSIDE the media
// query and reports the bug as still present when it is fixed.
function stripMedia(css){
  let out='',i=0;
  while(i<css.length){
    const m=css.indexOf('@media',i);
    if(m<0){ out+=css.slice(i); break; }
    out+=css.slice(i,m);
    let j=css.indexOf('{',m); if(j<0) break;
    let d=1; j++;
    while(j<css.length&&d>0){ if(css[j]==='{')d++; else if(css[j]==='}')d--; j++; }
    i=j;
  }
  return out;
}
const cssOnly=(html.match(/<style[\s\S]*?<\/style>/g)||[]).join('\n');
const unconditional = /body\.nosb\s+\.side\s*\{\s*display:\s*none/.test(stripMedia(cssOnly));
console.log('  nosb rule scoped to >=861px      : '+wideNosb);
console.log('  narrow hide rule present         : '+narrowHide);
console.log('  UNSCOPED nosb rule still present : '+unconditional+(unconditional?'   <-- the bug':''));
const hidden=(w,c)=> w<=860 ? !c.has('showsb') : c.has('nosb');
let fail=0;
for(const [w,label] of [[390,'iPhone 390px'],[834,'iPad portrait 834px'],[1024,'iPad landscape 1024px'],[1440,'desktop']]){
  const c=new Set();
  const tog=()=>{['nosb','showsb'].forEach(k=>c.has(k)?c.delete(k):c.add(k));};
  const steps=[];
  steps.push(['on load', hidden(w,c)]);
  tog();  steps.push(['after tapping the toggle', hidden(w,c)]);
  if(w<=860) c.delete('showsb');            // the on-select auto-close
  steps.push(['after opening a text', hidden(w,c)]);
  tog();  steps.push(['toggle again', hidden(w,c)]);
  // expectations: narrow starts hidden then opens; wide starts shown then hides
  const want = w<=860 ? [true,false,true,false] : [false,true,true,false];
  const got = steps.map(s=>s[1]);
  const ok = JSON.stringify(want)===JSON.stringify(got);
  if(!ok) fail++;
  console.log('\n  '+(ok?'ok  ':'FAIL')+' '+label);
  steps.forEach((s,i)=>console.log('        '+s[0].padEnd(26)+(s[1]?'pane hidden':'pane VISIBLE')
     +(got[i]===want[i]?'':'   <-- expected '+(want[i]?'hidden':'VISIBLE'))));
}
console.log('\n'+(fail||unconditional||!wideNosb?'FAILED':'sidebar behaves at every width'));
process.exit(fail||unconditional||!wideNosb?1:0);

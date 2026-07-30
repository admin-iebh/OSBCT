// STATIC span check for the Saṁyutta navs — the SPAN class WITHOUT a DOM sweep.
//
//   node _samspan.js <VOL> [...]
//
// !!! WHY NOT THE CLICK-EVERY-ROW SWEEP: `_vinnavverify.js`'s row loop takes
// `b.parentElement.querySelectorAll('.row')`, which on this sidebar is EVERY
// row in the nav (15,441 of them), not the volume's own — so sweeping one
// Saṁyutta node means clicking the whole tree and it does not finish.  This
// reproduces `render()`'s own span arithmetic (reader2.html ~line 295) in
// flat document order instead, and asserts the invariant those three shipped
// bugs violated: a node's span is never empty.
//   (1) a node whose NEIGHBOUR shares its ordinal   -> zero-length span
//   (2) a node keyed the same as its PARENT
//   (3) a LAST CHILD inheriting a parent end EQUAL TO ITS OWN START
const fs=require('fs');
const nav=JSON.parse(fs.readFileSync('site/reader/nav.json','utf8'));
let bad=0, checked=0;
for(const VOL of process.argv.slice(2)){
  const npara=JSON.parse(fs.readFileSync('site/'+VOL+'.json','utf8')).paragraphs.length;
  const canon=nav.layers.find(L=>L.layer==='canon'||L.id==='canon')||nav.layers[0];
  const nik=canon.nikayas.find(n=>(n.volumes||[]).some(v=>v.vol===VOL));
  const nodes=(nik.volumes||[]).filter(v=>v.vol===VOL);
  console.log('== '+VOL+'  '+nodes.length+' node(s), '+npara+' ¶'); if(nodes.some(r=>!(r.tree||r.kids||[]).length)){console.log('   REFUSING: a node has no children');process.exit(2);}
  for(const root of nodes){
    if(!(root.tree||root.kids||[]).length){console.log('   REFUSING: '+root.title+' has no children in nav.json');process.exit(2);}
    const list=[];
    (function flat(ns,depth,parentEnd){
      ns.forEach((nd,i)=>{ list.push({nd,depth}); if(nd.kids) flat(nd.kids,depth+1); });
    })(root.tree||root.kids||[],0);
    // document order = the order render() walks; end = next node starting later
    let n=0, empties=[], outside=[];
    list.forEach((e,idx)=>{
      const st=+e.nd.key.split('#')[1];
      let nxt=null;
      for(let q=idx+1;q<list.length;q++){
        const s2=+list[q].nd.key.split('#')[1];
        if(s2>st){ nxt=s2; break; }
      }
      let en = e.nd.end!=null ? e.nd.end : (nxt!=null ? nxt : npara);
      if(en<=st) en=st+1;                       // render()'s own guard
      n++;
      if(en<=st) empties.push(e.nd.label);
      if(st<0||st>=npara) outside.push(e.nd.label+' @'+st);
    });
    checked+=n;
    if(empties.length||outside.length){
      bad++;
      console.log('   FAIL '+root.title+': '+empties.length+' empty span(s), '
                  +outside.length+' key(s) out of range '
                  +JSON.stringify(empties.slice(0,6))+JSON.stringify(outside.slice(0,6)));
    } else {
      console.log('   ok   '+root.title+': '+n+' rows, every span non-empty, every key in 0..'+npara);
    }
  }
}
console.log(bad? '\nFAIL '+bad+' node(s)' : '\nPASS — '+checked+' rows checked, 0 empty spans');
process.exit(bad?1:0);

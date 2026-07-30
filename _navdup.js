// One nav node per BOOK, none left over. A volume holding several books
// legitimately has several nodes (18Khu01 has five); what must never happen is
// two nodes for the SAME book, which is how a rebuilt volume's old node
// survived alongside its replacement and showed Peṭakopadesapāḷi twice.
const fs=require('fs');
const nav=JSON.parse(fs.readFileSync('site/reader/nav.json','utf8'));
let bad=0,n=0;
for(const L of nav.layers) for(const nik of (L.nikayas||[])){
  const seen=new Map();
  for(const v of (nik.volumes||[])){
    n++;
    const k=v.vol+'|'+(v.first||'');
    if(seen.has(k)){bad++;console.log(`   DUPLICATE ${L.layer} ${v.vol} first=${v.first} title=${v.title} / ${seen.get(k)}`);}
    else seen.set(k,v.title);
  }
  // and no two nodes of one volume may share a title
  const t=new Map();
  for(const v of (nik.volumes||[])){
    const k=v.vol+'|'+(v.title||'');
    if(t.has(k)){bad++;console.log(`   SAME TITLE TWICE ${L.layer} ${v.vol} ${v.title}`);}
    else t.set(k,1);
  }
  // !!! AND NO TWO BOOK NODES ANYWHERE IN A NIKĀYA MAY SHARE A TITLE.
  // The two tests above are both keyed by VOLUME, so a name repeated ACROSS
  // volumes slipped straight through — which is how the Abhidhamma listed
  // "Tikapaṭṭhānapāḷi" three times and "Dukapaṭṭhānapāḷi" three times, one per
  // volume, for as long as this check has existed.  User-reported from the
  // sidebar, not by any check.  A work printed in several bhāgas must be
  // labelled as the edition labels it — "Paṭṭhānapāḷi (Paṭhamo bhāgo)" — which
  // is distinct by construction.  (A repeated label INSIDE one node's tree is
  // a different matter and is untouched: 25Khu08 prints "Pārāyanavagga" twice
  // and the edition nowhere distinguishes them.)
  const g=new Map();
  for(const v of (nik.volumes||[])){
    const k=v.title||'';
    if(g.has(k)){bad++;console.log(`   TITLE REPEATED ACROSS VOLUMES ${L.layer} ${nik.nikaya}: ${k} (${g.get(k)} and ${v.vol})`);}
    else g.set(k,v.vol);
  }
}
// !!! AND NO TWO *ADJACENT SIBLINGS* ANYWHERE IN A TREE MAY SHARE A LABEL.
// This is the rule that would have caught the defect 39Abhi11 shipped with:
// where the top level is an open (`re:`) set, the Paṭṭhāna reprints the outer
// section's name at the head of every inner one, and each reprint opened a NEW
// top — "1. Hetuduka" twenty-two times and "1. Kusalattika" fifty-two times,
// as adjacent siblings.  Every test above is about BOOK nodes, so none of them
// could see it, and the per-volume row sweeps could not either: a duplicated
// row still opens text.
//
// A label repeated NON-adjacently is a different thing and is left alone — the
// edition really does make a second and third pass over the same tikas or
// dukas (39Abhi11's Tikaduka crosses all 22 tikas with the first duka, then
// the first tika with all the remaining dukas, then all 22 tikas with the last
// duka), and those passes are not contiguous, so each needs its own node.
//
// TWO ADJACENT REPEATS ARE THE EDITION'S OWN and are named rather than
// tolerated by a widened rule:
const ADJ_OK=new Set([
  // the Cūḷaniddesa sets the Pārāyanavagga TEXT and then its NIDDESA, both
  // headed with the bare name, in the body and in its own mātikā alike
  '25Khu08|Pārāyanavagga',
  // 39Abhi11 printed p357-358 sets "Paccayacatukka-hetu" for the Paṭiccādivāra
  // block and again for the Pañhāvāra block with no heading between, which
  // check_layout.js's duplicate-heading rule already records as the edition's
  '39Abhi11|Paccayacatukka-hetu',
  // 01Vin01 sets a centred 'Idaṁ sabbamūlakaṁ' over each of two successive
  // numbered units under the Catutthapārājika (0-based pdf p154, p156) and
  // again under the Sukkavissaṭṭhisikkhāpada (p180, p183), and a centred
  // 'Idaṁ dasamūlakaṁ' over EIGHT successive units under the
  // Sañcarittasikkhāpada (p227-p238) — the peyyāla working one root at a time,
  // each heading printed identically over its own unit.  Counted off the PDF:
  // 4 and 8 printed lines, 4 and 8 rows in the tree.  Named, not admitted by
  // widening the rule.
  '01Vin01|Idaṁ sabbamūlakaṁ',
  '01Vin01|Idaṁ dasamūlakaṁ',
  // 02Vin02 sets a centred 'Mūlaṁ saṁkhittaṁ' over each of two successive
  // abbreviated passages of the Duṭṭhullārocana peyyāla (0-based pdf p55 and
  // p57) — two printed lines, two rows.
  '02Vin02|Mūlaṁ saṁkhittaṁ',
]);
// !!! AND A VOLUME OF THE COMMENTARY OR ṬĪKĀ LAYERS CONTRIBUTES EXACTLY ONE
// TOP-LEVEL NODE.  Nothing anywhere asserted that the number of names in a
// nikāya matches the number of volumes the edition prints, so the sidebar
// listed NINE Vinaya-Aṭṭhakathā names for SIX printed volumes and a USER
// counting them was the only test — the same way the Abhidhamma's
// "Tikapaṭṭhānapāḷi three times" was found.  Every test above is about
// DUPLICATE labels, and nine distinct correct names are not duplicates.
//
// It is layer-scoped because it is a fact about these layers and not about the
// canon: 01VinA01-04VinA04 are four bhāgas of ONE work, the Samantapāsādikā,
// and their inner books are the first TREE level (2026-07-27ae).  In the canon
// a volume legitimately carries several BOOKS of the piṭaka — 18Khu01 has five,
// 15An01 four — so there the invariant is only that every volume has a node.
//
// THE ELEVEN THAT STILL FAIL IT ARE NAMED, not tolerated by a widened rule.
// Every one still carries the old font-heuristic tree from build_nav.py and
// has never been built; each entry comes off this list when its volume is.
const MULTITOP_PENDING=new Set([
  '50AbhiA03',                                                      // commentary, unbuilt
  // 18AnA02 and 19AnA03 came off this list 2026-07-27am, when the
  // Aṅguttara-Aṭṭhakathā navs were written and each volume dropped to the ONE
  // top-level node the invariant requires.
  '03ViT03','07ViT07','15MaT03','19AnT02','20AnT03','22AbhiT01','23AbhiT02','24AbhiT03',
]);
{
  const top=new Map(), lay=new Map();
  for(const L of nav.layers) for(const nik of (L.nikayas||[])) for(const v of (nik.volumes||[])){
    top.set(v.vol,(top.get(v.vol)||0)+1); lay.set(v.vol,L.layer);
  }
  for(const [vol,c] of top){
    const l=lay.get(vol);
    if((l==='commentary'||l==='subcommentary') && c>1 && !MULTITOP_PENDING.has(vol)){
      bad++; console.log(`   ${c} TOP-LEVEL NODES for one ${l} volume ${vol} (the edition prints one)`);
    }
  }
  const pend=[...MULTITOP_PENDING].filter(v=>(top.get(v)||0)>1);
  if(pend.length) console.log(`   (${pend.length} volume(s) awaiting a real nav still carry several top nodes: ${pend.join(', ')})`);
  // and no volume the manifest lists may be missing from the tree entirely
  const man=JSON.parse(fs.readFileSync('site/reader/manifest.json','utf8'));
  const miss=Object.keys(man.volumes).filter(v=>!top.has(v));
  if(miss.length){ bad+=miss.length; console.log(`   VOLUME WITH NO NAV NODE: ${miss.join(', ')}`); }
  console.log(`${top.size} volumes carry a nav node; ${[...top.values()].reduce((a,b)=>a+b,0)} top-level nodes in all`);
}
let adj=0,rows=0;
function walk(vol,ns){
  for(let i=0;i+1<ns.length;i++){
    rows++;
    if(ns[i].label===ns[i+1].label && !ADJ_OK.has(vol+'|'+ns[i].label)){
      adj++;
      console.log(`   ADJACENT SIBLINGS SHARE A LABEL ${vol}: ${ns[i].label} (${ns[i].key} / ${ns[i+1].key})`);
    }
  }
  if(ns.length) rows++;
  for(const x of ns) walk(vol,x.kids||[]);
}
for(const L of nav.layers) for(const nik of (L.nikayas||[])) for(const v of (nik.volumes||[])) if(v.tree) walk(v.vol,v.tree);
console.log(`${rows} tree rows checked for adjacent duplicates, ${adj} found`);
bad+=adj;
console.log(`${n} nav nodes checked, ${bad} duplicate book node(s) [${bad?'FAIL':'PASS'}]`);
process.exit(bad?1:0);

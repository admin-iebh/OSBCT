# -*- coding: utf-8 -*-
import io,sys
P='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/site/reader/reader2.html'
s=io.open(P,encoding='utf-8').read()

# ---------------------------------------------------------------- 1. runBounds + runsFor
OLD_TF="""function targetsFor(ord,kind){ // kind 'A'|'T' -> list of {key,state,worktag?}"""
NEW_PRE = u"""// !!! A CANON PARAGRAPH'S COMMENTARY IS A RANGE, NOT A POINT (2026-08-04,
// reader-reported with a screenshot).  Reading `18Khu01` with the A band on,
// `1. Saraṇattaya` drew EXACTLY ONE commentary paragraph — `20KhuA01#9`,
// "Ayaṁ tāva atthato Buddhavibhāvanā" — while the printed commentary on the
// Saraṇattaya runs to p.13 and closes at `Saraṇattayavaṇṇanā niṭṭhitā.`:
// nineteen paragraphs, of which the reader was shown one.
//
// `linksk/<vol>.links.json` records ONE target per canon paragraph, and that
// was enough only by accident: before `75ee5904` re-segmented `20KhuA01` to
// 673 paragraphs it held 109 LUMPS, and the single link landed on a lump that
// happened to contain the whole section.  Re-segmenting turned every such lump
// into real paragraphs and the same link now points at the first of them.
// The fault is general — every canon paragraph whose commentary spans more
// than one paragraph, in every re-segmented volume.
//
// So the range: a canon paragraph's commentary runs from its own target up to,
// but not including, whatever comes first of
//
//   (a) the next canon paragraph's target in the SAME volume, and
//   (b) the next work boundary the EDITION ITSELF prints.
//
// (b) is not optional and it is not decoration.  Measured over the 42 canon
// volumes that carry links, 19,145 targets have both bounds available; the
// arithmetic and the printed headings AGREE on 3,470 (18.1%), the next target
// falls first on 14,158 (74.0%) — the ordinary case of several canon
// paragraphs inside one commentary section — and on **1,517 (7.9%) the
// arithmetic runs PAST a printed section end** and only the heading stops it.
// Canon ¶0 of `18Khu01` is one of the 1,517: its next target is `20KhuA01#39`,
// eleven paragraphs INSIDE `2. Sikkhāpadavaṇṇanā`.
//
// NOTHING IS MANUFACTURED HERE.  This draws paragraphs that already exist
// between two attested targets; no record is created, and `linksk/` is not
// touched.  `6f7e5629` removed 52.4% of the targets because they were
// invented, and inventing a range would be the same fault in a new place.
const RUNB={};
function runBounds(vol){
  // The ordinals in `vol` at which a new WORK begins, by two independent routes:
  //
  //   colophon — the edition closes a work with `X niṭṭhitā.` / `X samattā.`,
  //     and `sections/` deliberately drops those end markers
  //     (`extract_toc.is_endmarker`), so they are read from the volume's own
  //     `headings` array and resolved to the ordinal of the head that FOLLOWS.
  //   number   — a section head carrying the edition's own printed number,
  //     `2. Sikkhāpadavaṇṇanā`.
  //
  // On `20KhuA01` the two routes agree on 8 of 8 boundaries the colophon route
  // can resolve {28,72,170,204,406,500,541,606}; the colophon route loses the
  // last two of ten because `Nigamanakathā` and the back-matter index are not
  // in `sections/`.  The union is used: a boundary either route attests.
  if(RUNB[vol]) return RUNB[vol];
  const c=cache[vol]; if(!c) return [];
  const sm=c.sec||{}, heads=c.headings||[];
  const strip=t=>String(t||'').trim().replace(/^\\d+(-\\d+)?\\.\\s*/,'');
  const fold=t=>hfold(strip(t)).replace(/[^a-z ]/g,'').trim();
  const isEnd=t=>{const w=fold(t).split(' ').filter(Boolean); if(!w.length) return false;
    return /(nitthita|nitthitam|nitthito|samatta|samattam|samatto)$/.test(w[w.length-1]);};
  const anch=[];
  Object.keys(sm).map(Number).sort((a,b)=>a-b).forEach(o=>{
    (sm[String(o)]||[]).forEach(x=>anch.push([o,fold(x.l||'')])); });
  const B=new Set(); let ptr=0;
  for(let i=0;i<heads.length;i++){
    if(!isEnd(heads[i].title)) continue;
    let j=i+1;
    while(j<heads.length && (/^[_\\s.]*$/.test(heads[j].title||'') || isEnd(heads[j].title))) j++;
    if(j>=heads.length) continue;
    const want=fold(heads[j].title); if(want.length<4) continue;
    let hit=-1;
    for(let k=ptr;k<anch.length;k++) if(anch[k][1]===want){hit=k;break;}
    if(hit<0) for(let k=0;k<anch.length;k++) if(anch[k][1]===want){hit=k;break;}
    if(hit<0) continue;                       // unresolved colophon: no boundary claimed
    ptr=hit+1; B.add(anch[hit][0]);
  }
  Object.keys(sm).forEach(o=>{ if((sm[o]||[]).some(x=>/^\\s*\\d+(-\\d+)?\\.\\s/.test(x.l||''))) B.add(+o); });
  return RUNB[vol]=[...B].sort((a,b)=>a-b);
}
// canonVol|kind -> {end:{targetKey:lastOrdinal}, first:{targetKey:canonOrdinal}}
let RUNS={};
function runsFor(kind){
  const ck=state.canonVol+'|'+kind; if(RUNS[ck]) return RUNS[ck];
  const SLOT=(kind==='A')?'commentary':'subcommentary';
  const L=state.links||{}; const byVol={};
  Object.keys(L).map(Number).sort((a,b)=>a-b).forEach(i=>{
    ((L[String(i)]||{})[SLOT]||[]).forEach(t=>{ if(t.state!=='direct') return;
      const a=parseKey(t.key); (byVol[a[0]]=byVol[a[0]]||[]).push([i,a[1]]); }); });
  const end={},first={}; let cold=false;
  for(const v of Object.keys(byVol)){
    const arr=byVol[v], c=cache[v];
    if(!c){ cold=true; }
    // !!! A TARGET VOLUME THE CONCORDANCE DOES NOT ALLOW GETS NO RANGE.
    // `check_concordance.py` counts 3,163 targets pointing at a volume the
    // edition's own map does not pair with that canon volume, and 1,000 of
    // them are in these maps.  They are DIMMED, not suppressed
    // (`claude/decision_dim_the_condemned_links.md`), so the paragraph they
    // name still draws — but a link three criteria condemn must not be the
    // authority for a run: unguarded, `18Khu01`'s single stray target into
    // `42KhuA23` expanded to 118 paragraphs of the Jātaka commentary, and
    // `34KhuA15` to 81.  Refusing the range costs nothing that was there
    // before and is the "flag rather than guess" rule applied to a range.
    const ok=!!c && !!VOLGROUP[v] && VOLGROUP[v]===VOLGROUP[state.canonVol];
    const B=ok?runBounds(v):[]; const n=ok?(c.paras||[]).length:0;
    const HD=ok?Object.keys(c.sec||{}).map(Number).sort((a,b)=>a-b):[];
    for(let k=0;k<arr.length;k++){
      const ci=arr[k][0], o=arr[k][1], key=v+'#'+o;
      if(first[key]==null) first[key]=ci;
      if(end[key]!=null) continue;
      if(!ok||!n){ end[key]=o; continue; }
      let nxt=null; for(let j=k+1;j<arr.length;j++){ const o2=arr[j][1]; if(o2>o&&(nxt==null||o2<nxt)) nxt=o2; }
      let b=null; for(let z=0;z<B.length;z++) if(B[z]>o){ b=B[z]; break; }
      let e;
      if(nxt==null&&b==null){
        // NEITHER BOUND EXISTS.  Do not run to the end of the volume — clip at
        // the next section head of any level, and where there is none at all,
        // draw the single paragraph, which is exactly what was drawn before.
        let h=null; for(let z=0;z<HD.length;z++) if(HD[z]>o){ h=HD[z]; break; }
        e=(h!=null)?h-1:o;
      } else e=Math.min.apply(null,[nxt,b].filter(x=>x!=null))-1;
      end[key]=Math.max(o,Math.min(e,n-1));
    }
  }
  const r={end,first};
  // a cold cache would freeze "no range" into the memo; recompute next pass
  if(!cold) RUNS[ck]=r;
  return r;
}
function targetsFor(ord,kind){ // kind 'A'|'T' -> list of {key,state,runOf,worktag?}"""
assert OLD_TF in s
s=s.replace(OLD_TF,NEW_PRE,1)

# ---------------------------------------------------------------- 2. expand in targetsFor
OLD_RET = """  const multi=arr.length>1;
  // `src` is the paragraph this block is being drawn UNDER.  It travels with
  // the target so the band's own tools never have to guess (see hasBand).
  return arr.map(t=>{const v=parseKey(t.key)[0]; return {key:t.key,state:t.state,
    src:state.canonVol+'#'+ord,
    worktag: multi? ((shortWork(VOLWORK[v])||'')+' · '+v) : null};});
}"""
NEW_RET = u"""  const multi=arr.length>1;
  // `src` is the paragraph this block is being drawn UNDER.  It travels with
  // the target so the band's own tools never have to guess (see hasBand).
  // `runOf` is the ATTESTED target the paragraph hangs off — the head of the
  // run and every paragraph drawn after it carry the same value, which is what
  // lets render() wrap one run in one block and collapse its tail.
  const R=runsFor(kind), out=[];
  arr.forEach(t=>{
    const a=parseKey(t.key), v=a[0], o=a[1];
    const wt=multi?((shortWork(VOLWORK[v])||'')+' · '+v):null;
    // A REPEATED TARGET DRAWS ONLY ITS OWN PARAGRAPH.  `18Khu01` ¶1–¶5 all
    // point at `20KhuA01#39` (Purimapañcasikkhāpadavaṇṇanā glosses five
    // sikkhāpada at once); the run belongs to the FIRST of them and expanding
    // it five times would put the same 27 paragraphs on the page five times.
    const last=(R.first[t.key]===ord && R.end[t.key]!=null)?R.end[t.key]:o;
    for(let x=o;x<=last;x++){
      const c=cache[v]; if(c&&c.hide&&c.hide[String(x)]) continue;
      out.push({key:v+'#'+x,state:t.state,src:state.canonVol+'#'+ord,runOf:t.key,worktag:wt});
    }
  });
  return out;
}"""
assert OLD_RET in s
s=s.replace(OLD_RET,NEW_RET,1)

io.open(P,'w',encoding='utf-8').write(s)
print('patch1 ok')

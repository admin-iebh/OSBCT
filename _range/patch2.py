# -*- coding: utf-8 -*-
import io
P='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/site/reader/reader2.html'
s=io.open(P,encoding='utf-8').read()

OLD = """    const dedup=!state.active.canon; let lastA=null,lastT=null; let _drew=0,_drewA=0,_drewT=0;"""
NEW = """    const dedup=!state.active.canon; let lastA=null,lastT=null; let _drew=0,_drewA=0,_drewT=0;
    // A COMMENTARY PARAGRAPH IS DRAWN AT MOST ONCE PER PAGE.  Before the range
    // work this was true only when the canon band was OFF (`dedup`), so with
    // P+A on, `18Khu01` ¶1–¶5 each drew `20KhuA01#39`: the same paragraph five
    // times, one under each sikkhāpada.  A run makes that five times
    // twenty-seven, so the dedup has to be by KEY over the whole pass.
    const drawnA=new Set(), drawnT=new Set();"""
assert OLD in s; s=s.replace(OLD,NEW,1)

OLD2 = """      if(state.active.A) targetsFor(i,'A').forEach((t,ti)=>{ if(dedup&&t.key===lastA)return; lastA=t.key; _drew++; _drewA++; parts.push(((spine==='A'&&ti>0)?_front(t.key):'')+(state.active.canon?'<div class="subwrap a"><span class="lchip a">Aṭṭhakathā</span>'+_bandHead(t.key,'A'):'<div>')+block('A',t.key,t)+'</div>'); });
      if(state.active.T) targetsFor(i,'T').forEach((t,ti)=>{ if(dedup&&t.key===lastT)return; lastT=t.key; _drew++; _drewT++; parts.push(((spine==='T'&&ti>0)?_front(t.key):'')+(state.active.canon?'<div class="subwrap t"><span class="lchip t">Ṭīkā</span>'+_bandHead(t.key,'T'):'<div>')+block('T',t.key,t)+'</div>'); });"""
NEW2 = u"""      // ONE RUN, ONE BLOCK, AND ITS TAIL BEHIND A CONTROL.  `targetsFor` now
      // returns every paragraph of the range, each carrying `runOf` — the
      // attested target it hangs off — so consecutive entries sharing a
      // `runOf` are one run and get one chip, one heading pass and one
      // "Read more".  Requested by the reader: some runs are long (the longest
      // in `18Khu01` is 98 paragraphs), and a band that dumps ninety-eight
      // paragraphs under one canon line is not readable either.
      //
      // The collapse is decided from the DATA — how many paragraphs the run
      // holds — never from measured layout.  `claude/the_layout_was_an_estimate.md`
      // records what happens when a scroll aims at a document that has not
      // finished measuring itself; the tail is `hidden`, so it has no height at
      // render, and expanding it grows the page BELOW the button, which cannot
      // move what the reader is looking at.  `toggleRun` does not re-render.
      const bandHTML=(k)=>{
        const ts=targetsFor(i,k); if(!ts.length) return '';
        const cls=(k==='A')?'a':'t', nm=(k==='A')?'Aṭṭhakathā':'Ṭīkā';
        const drawn=(k==='A')?drawnA:drawnT;
        let out='', g=0;
        while(g<ts.length){
          let e=g+1; while(e<ts.length && ts[e].runOf===ts[g].runOf) e++;
          const grp=ts.slice(g,e), g0=g; g=e;
          const headKey=grp[0].runOf;
          if(drawn.has(grp[0].key)) continue;
          if(dedup && grp[0].key===((k==='A')?lastA:lastT)) continue;
          grp.forEach(t=>drawn.add(t.key));
          if(k==='A') lastA=grp[grp.length-1].key; else lastT=grp[grp.length-1].key;
          _drew+=grp.length; if(k==='A') _drewA+=grp.length; else _drewT+=grp.length;
          const isOpen=OPENRUNS.has(headKey);
          const nshow=(grp.length<=RUNOPEN+1||isOpen)?grp.length:RUNOPEN;
          let body='', rest='';
          grp.forEach((t,gi)=>{
            const blk=((spine===k&&(g0+gi)>0)?_front(t.key):'')
                     +(state.active.canon?_bandHead(t.key,k):'')+block(k,t.key,t);
            if(gi<nshow) body+=blk; else rest+=blk;
          });
          const hid=grp.length-nshow;
          const rid='run-'+headKey.replace('#','-')+'-'+i+'-'+k;
          let ctl='';
          if(hid>0) ctl='<div class="runrest" id="'+rid+'" hidden>'+rest+'</div>'
                       +'<button class="runmore" data-box="'+rid+'" data-run="'+escA(headKey)
                       +'" data-n="'+hid+'" onclick="toggleRun(this)">'
                       +esc(TIP('run_more','Read more — %s more paragraphs of this section').replace('%s',hid))+'</button>';
          else if(isOpen && grp.length>RUNOPEN+1)
            ctl='<button class="runmore" data-run="'+escA(headKey)+'" data-n="'+(grp.length-RUNOPEN)
               +'" onclick="toggleRun(this)">'+esc(TIP('run_less','Show less'))+'</button>';
          out += state.active.canon
            ? '<div class="subwrap '+cls+'"><span class="lchip '+cls+'">'+nm+'</span>'+body+ctl+'</div>'
            : '<div>'+body+ctl+'</div>';
        }
        return out;
      };
      if(state.active.A){ const h=bandHTML('A'); if(h) parts.push(h); }
      if(state.active.T){ const h=bandHTML('T'); if(h) parts.push(h); }"""
assert OLD2 in s; s=s.replace(OLD2,NEW2,1)

# RUNOPEN / OPENRUNS / toggleRun — declared next to the other render globals
OLD3 = """function activeKeys(){return ['canon','A','T'].filter(k=>state.active[k]);}"""
NEW3 = u"""function activeKeys(){return ['canon','A','T'].filter(k=>state.active[k]);}
// How much of a run is open before the reader asks for the rest, and which runs
// the reader has already opened.  `OPENRUNS` survives a re-render so that
// pressing T does not silently re-collapse a commentary the reader opened.
const RUNOPEN=2; const OPENRUNS=new Set();
window.toggleRun=function(btn){
  const key=btn.dataset.run, box=btn.dataset.box?document.getElementById(btn.dataset.box):null;
  if(box){
    const opening=box.hasAttribute('hidden');
    if(opening){ box.removeAttribute('hidden'); OPENRUNS.add(key); btn.textContent=TIP('run_less','Show less'); }
    else { box.setAttribute('hidden',''); OPENRUNS.delete(key);
           btn.textContent=TIP('run_more','Read more — %s more paragraphs of this section').replace('%s',btn.dataset.n); }
    return;
  }
  // the run was rendered fully open (it was open before this render): collapse
  // it by asking render() for the collapsed shape, holding the reader's place.
  OPENRUNS.delete(key); keepPlace(render);
};"""
assert OLD3 in s; s=s.replace(OLD3,NEW3,1)

# CSS
OLD4 = """.subwrap.a{margin-left:20px}.subwrap.t{margin-left:40px}"""
NEW4 = """.subwrap.a{margin-left:20px}.subwrap.t{margin-left:40px}
.runmore{display:block;margin:2px 0 10px 2px;padding:5px 12px;font-family:'Inter',sans-serif;font-size:12px;line-height:1.4;color:var(--mut);background:transparent;border:1px dashed var(--line);border-radius:16px;cursor:pointer}
.runmore:hover{color:var(--ink);border-style:solid}"""
assert OLD4 in s; s=s.replace(OLD4,NEW4,1)

io.open(P,'w',encoding='utf-8').write(s)
print('patch2 ok')

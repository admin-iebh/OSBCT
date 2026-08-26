// COLUMNS VIEW: is each layer in its own column, on every row?
//
// READER-REPORTED 2026-08-26, with a screenshot of `12Sam01` (Oghataraṇasutta),
// P and A both on: the left column headed PĀḶI (TIPIṬAKA) was EMPTY but for a
// `page 1` rule, and the right column headed AṬṬHAKATHĀ carried the CANON text
// of the sutta.  The report was "P should be on the left and A on the right".
//
// THE COLUMN ORDER WAS NEVER WRONG, AND THAT IS WHY THIS GATE ASSERTS CELLS AND
// NOT ORDER.  `activeKeys()` is `['canon','A','T'].filter(...)`, so canon is
// first by construction, and the two headers in the screenshot were in the right
// order.  What was wrong is the number of GRID ITEMS a row emits:
//
//   `.grid` is the grid, `.rowline` is `display:contents`, so every child of a
//   rowline is a direct grid item.  `block()` returns `rule + <div class=para>`
//   — a `<div class="pgrule">page 1</div>` in front of the paragraph wherever a
//   printed page turns there.  That rule takes a CELL.  With two columns, a row
//   emitting [pgrule, canon, pgrule, A] puts `page 1` in column 1, the CANON
//   paragraph in column 2 — under the Aṭṭhakathā heading — and wraps the rest
//   onto an implicit row.  Measured on `12Sam01`: 517 rows, 77 of them emitting
//   more items than there are columns.
//
//   A band cell holding SEVERAL targets does the same thing, for the same
//   reason: `ts.map(block).join('')` is several `.para` siblings, not one cell.
//
// So the invariant is: A ROW EMITS EXACTLY ONE GRID ITEM PER ACTIVE LAYER, and
// the item at index k belongs to the layer at `activeKeys()[k]`.  Anything else
// puts a layer under another layer's heading, which is what was on screen.
//
//   node pipeline/check_columns.js                 # the default cases
//   node pipeline/check_columns.js 12Sam01 18Khu01 # named canon volumes
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    if(t==null){ console.log('  !! could not inline '+u); return m; }
    return '<script>'+t+'</script>';
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

// which class marks a cell belonging to each layer key
const MARK={canon:'canon', A:'l-A', T:'l-T'};

async function run(w, vol, active){
  const keys=['canon','A','T'].filter(k=>active[k]);
  try{ w.eval('state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
  try{ await w.openKey(vol+'#0','canon'); }catch(e){}
  for(let k=0;k<70;k++){ await wait(90);
    const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
  try{ w.eval("state.view='columns'; state.active="+JSON.stringify(active)+";"); }catch(e){}
  try{ await w.ensureBandVols(); }catch(e){}
  try{ w.render(); }catch(e){ return {err:e.message, keys}; }
  await wait(500);
  const d=w.document;
  const heads=[...d.querySelectorAll('.colhead .ch')].map(e=>e.textContent.trim());
  const rows=[...d.querySelectorAll('.grid .rowline')];
  let wide=0, misplaced=0, firstWide=null, firstMis=null;
  rows.forEach((r,ri)=>{
    const cells=[...r.children];
    if(cells.length!==keys.length){ wide++; if(firstWide==null) firstWide=[ri,cells.length,
      cells.map(c=>(c.className||'').split(' ')[0]+(c.id?('#'+c.id):'')).join(' | ')]; }
    keys.forEach((k,ci)=>{
      const c=cells[ci]; if(!c) return;
      const cls=' '+(c.className||'')+' ';
      // the cell for key k must carry that layer's paragraph (or be the
      // deliberate empty placeholder) — never another layer's, never a rule
      const ok = cls.includes(' '+MARK[k]+' ') || cls.includes(' empty ')
              || (c.querySelector && c.querySelector('.para.'+MARK[k]))
              || (c.querySelector && c.querySelector('.para.empty'));
      if(!ok){ misplaced++; if(firstMis==null) firstMis=[ri,ci,k,(c.className||''),
        (c.textContent||'').replace(/\s+/g,' ').trim().slice(0,60)]; }
    });
  });
  return {keys, heads, rows:rows.length, wide, misplaced, firstWide, firstMis};
}

const CASES=[
  // the reader's own case, and the one in the screenshot
  ['12Sam01', {canon:true,A:true,T:false}],
  ['12Sam01', {canon:true,A:true,T:true}],
  ['12Sam01', {canon:true,A:false,T:true}],
  // a second book, so this is not one volume's accident
  ['18Khu01', {canon:true,A:true,T:false}],
  ['09Ma01',  {canon:true,A:true,T:false}],
];

(async()=>{
  const argv=process.argv.slice(2);
  const cases=argv.length? argv.map(v=>[v,{canon:true,A:true,T:false}]) : CASES;
  let fails=[];
  console.log('columns view: one grid cell per active layer, on every row');
  for(const [vol,active] of cases){
    // !!! A FRESH WINDOW PER CASE.  Re-using one window across cases keeps every
    // volume any case loaded in `cache`, and three openings of a Saṁyutta volume
    // with all three bands on was enough to hit node's 2 GB heap ceiling and
    // abort the run AFTER it had printed passes — a gate that dies mid-way looks
    // like a gate that ran.
    const w=boot(); await wait(1400);
    const r=await run(w, vol, active);
    try{ w.close(); }catch(e){}
    const tag=vol+' ['+r.keys.join('+')+']';
    if(r.err){ console.log('  FAIL  '+tag+' render threw: '+r.err); fails.push(tag+' threw'); continue; }
    if(!r.rows){ console.log('  FAIL  '+tag+' drew no rows'); fails.push(tag+' no rows'); continue; }
    if(r.wide||r.misplaced){
      console.log('  FAIL  '+tag+'  '+r.rows+' rows, '+r.wide+' emit more cells than there are '
                  +'columns, '+r.misplaced+' cell(s) hold the wrong layer');
      if(r.firstWide) console.log('          first wide row '+r.firstWide[0]+': '+r.firstWide[1]
                                  +' items — '+r.firstWide[2]);
      if(r.firstMis)  console.log('          first misplaced: row '+r.firstMis[0]+' column '
                                  +r.firstMis[1]+' should hold '+r.firstMis[2]+', has class '
                                  +JSON.stringify(r.firstMis[3])+' '+JSON.stringify(r.firstMis[4]));
      fails.push(tag+': '+r.wide+' wide, '+r.misplaced+' misplaced');
    } else {
      console.log('  ok    '+tag+'  '+r.rows+' rows, every row '+r.keys.length+' cells, '
                  +'each under its own heading  ['+r.heads.join(' | ')+']');
    }
  }
  if(fails.length){ console.log('\nCOLUMNS FAILED:'); fails.forEach(f=>console.log('  - '+f));
    process.exit(1); }
  console.log('\nall green');
  process.exit(0);
})();

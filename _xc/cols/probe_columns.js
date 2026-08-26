// What is actually in each COLUMN when P and A are both on?
//
// Reader-reported 2026-08-26 with a screenshot of `12Sam01` (Oghataraṇasutta):
// the left column is headed PĀḶI (TIPIṬAKA) and is EMPTY; the right column is
// headed AṬṬHAKATHĀ and carries what reads as the CANON text of the sutta.
// The report was "P should be on the left tab and A on the right".
//
// `activeKeys()` is `['canon','A','T'].filter(...)`, so the column ORDER cannot
// be the fault — canon is first by construction, and the headers in the
// screenshot are in the right order.  So the question this probe answers is not
// "which order" but "WHAT IS IN EACH CELL", read off a real render rather than
// inferred from the source.
//
//   node _xc/cols/probe_columns.js 12Sam01 [ord]
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

(async()=>{
  const vol=process.argv[2]||'12Sam01';
  const ord=process.argv[3]!=null?+process.argv[3]:0;
  const w=boot();
  await wait(1400);
  try{ await w.openKey(vol+'#'+ord,'canon'); }catch(e){ console.log('open failed:',e.message); }
  for(let k=0;k<70;k++){ await wait(90);
    const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
  // Columns, with P and A on and T off — the state in the screenshot.
  try{ w.eval("state.view='columns'; state.active={canon:true,A:true,T:false};"); }catch(e){}
  try{ await w.ensureBandVols(); }catch(e){}
  try{ w.render(); }catch(e){ console.log('render threw:',e.message); }
  await wait(700);

  const d=w.document;
  const heads=[...d.querySelectorAll('.colhead .ch')].map(e=>e.textContent.trim());
  console.log('column headers, left to right:', JSON.stringify(heads));
  try{ console.log('activeKeys():', JSON.stringify(w.eval('activeKeys()'))); }catch(e){}

  const rows=[...d.querySelectorAll('.grid .rowline')];
  console.log('rows drawn:', rows.length);
  let emptyL=0, emptyR=0;
  rows.slice(0,6).forEach((r,i)=>{
    const cells=[...r.children];
    console.log('\n-- row '+i+', '+cells.length+' cell(s)');
    cells.forEach((c,j)=>{
      const cls=(c.className||'')+'';
      const t=c.textContent.replace(/\s+/g,' ').trim();
      console.log('   cell '+j+'  class='+JSON.stringify(cls)+'  id='+JSON.stringify(c.id||'')
                  +'\n           '+JSON.stringify(t.slice(0,90)));
    });
  });
  rows.forEach(r=>{ const c=[...r.children];
    if(c[0]&&/\bempty\b/.test(c[0].className||''))emptyL++;
    if(c[1]&&/\bempty\b/.test(c[1].className||''))emptyR++; });
  console.log('\nover all '+rows.length+' rows: left cell empty '+emptyL+', right cell empty '+emptyR);
  process.exit(0);
})();

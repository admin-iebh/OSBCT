// PROOF: bold draws on BOTH SIDES of a mid-paragraph page rule, in BOTH views.
// canon volumes render with asSpine=true (kind==='canon'); a COMMENTARY volume
// opened without opts.spine takes the fmtBold band path.  One of each.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{let t=null;try{t=fs.readFileSync(resolve(u),'utf8');}catch(e){}return t==null?m:'<script>'+t+'</script>';});}
function boot(){const dom=new JSDOM(inlineScripts(fs.readFileSync(R+'/reader2.html','utf8')),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}

function report(tag, doc, vol){
  const paras=[...doc.querySelectorAll('#scroll .para')].filter(p=>(p.id||'').includes('-'+vol+'-'));
  let withRule=0, both=0, boldTotal=0, examples=[];
  for(const p of paras){
    const rules=[...p.querySelectorAll('.pgrule')];
    if(!rules.length) continue;
    withRule++;
    const bolds=[...p.querySelectorAll('b.lemma, b')];
    boldTotal+=bolds.length;
    for(const r of rules){
      const before=bolds.filter(b=>r.compareDocumentPosition(b)&doc.defaultView.Node.DOCUMENT_POSITION_PRECEDING).length;
      const after =bolds.filter(b=>r.compareDocumentPosition(b)&doc.defaultView.Node.DOCUMENT_POSITION_FOLLOWING).length;
      if(before&&after){ both++; if(examples.length<2) examples.push(p.id+' @'+(r.textContent||'').trim()+'  bold before='+before+' after='+after); }
    }
  }
  let inGatha=0, cutMid=0;
  for(const p of paras) for(const r of p.querySelectorAll('.pgrule')){
    if(r.closest('.gatha')||r.closest('.gatha-after')){ inGatha++;
      // a rule that CUT a drawn string has text before AND after it inside the
      // same .gatha div -- the `drawnOffset` half of the repair, on screen
      const g=r.closest('.gatha')||r.closest('.gatha-after');
      const kids=[...g.childNodes]; const i=kids.indexOf(r);
      const before=kids.slice(0,i).map(x=>x.textContent).join('').replace(/\s/g,'');
      const after =kids.slice(i+1).map(x=>x.textContent).join('').replace(/\s/g,'');
      if(before&&after) cutMid++; }
  }
  console.log('  '+tag+': '+paras.length+' ¶ of '+vol+', '+withRule+' carry a page rule, '+boldTotal+' <b> in them, '
    +both+' rule(s) with bold on BOTH sides; '+inGatha+' rule(s) drawn INSIDE a .gatha, '+cutMid+' of them CUTTING the drawn string');
  examples.forEach(e=>console.log('      e.g. '+e));
  return both;
}


function hostsOf(vol){
  let rev={}; try{ rev=JSON.parse(fs.readFileSync(R+'/linksk/'+vol+'.rev.json','utf8')); }catch(e){}
  const first={};
  for(const [ord,e] of Object.entries(rev)){ if(!e||!e.canon) continue;
    const cv=e.canon.split('#')[0]; if(first[cv]==null||+ord<first[cv]) first[cv]=+ord; }
  return Object.keys(first).sort().map(cv=>vol+'#'+first[cv]);
}
async function openCommentary(w, vol, kind){
  let n=0;
  for(const key of hostsOf(vol)){
    try{ w.eval('state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
    try{ await w.openKey(key, kind); }catch(e){}
    for(let k=0;k<60;k++){ await wait(90);
      const s=w.document.querySelector('#scroll');
      if(s&&[...s.querySelectorAll('.para')].some(p=>(p.id||'').includes('-'+vol+'-'))){ n++; break; } }
    if(n) return true;
  }
  return false;
}
(async()=>{
  // !!! THE RULES MUST BE ADDITIVE.  `_boldRange` is now called on PIECES of a
  // drawn string, and `fmtPiece` renders a piece with no spans; either could
  // silently drop bold or letters.  Rendered twice -- with the pbreak map and
  // with it withheld -- the letters and the <b> count must be IDENTICAL and only
  // the rules may differ.
  const V=process.argv[2];
  async function shot(){
    const w=boot(); await wait(700);
    try{ await w.openKey(V+'#0','canon'); }catch(e){}
    for(let k=0;k<70;k++){ await wait(90); const s=w.document.querySelector('#scroll'); if(s&&[...s.querySelectorAll('.para')].some(p=>(p.id||'').includes('-'+V+'-'))) break; }
    const d=w.document;
    const paras=[...d.querySelectorAll('#scroll .para')].filter(p=>(p.id||'').includes('-'+V+'-'));
    let letters='', bolds=0, boldletters='', rules=0;
    const L=t=>String(t||'').replace(/[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]/g,'');
    for(const p of paras){
      rules+=p.querySelectorAll('.pgrule').length;
      for(const r of p.querySelectorAll('.pgrule')) r.remove();   // the rules themselves are the difference
      letters+=L(p.textContent);
      const bs=[...p.querySelectorAll('b')]; bolds+=bs.length;
      boldletters+=bs.map(b=>L(b.textContent)).join('|');
    }
    const r=[paras.length, letters.length, bolds, boldletters.length,
             require('crypto').createHash('sha1').update(letters).digest('hex').slice(0,12),
             require('crypto').createHash('sha1').update(boldletters).digest('hex').slice(0,12)];
    r.push(rules); w.close(); return r;
  }
  const a=await shot();
  console.log('  WITH pbreak   : ¶='+a[0]+' letters='+a[1]+' <b>='+a[2]+' boldletters='+a[3]+' sha='+a[4]+' boldsha='+a[5]+'  rules='+a[6]);
  fs.renameSync('site/reader/pbreak/'+V+'.json','site/reader/pbreak/'+V+'.WITHHELD');
  let b;
  try{ b=await shot(); }
  finally{ fs.renameSync('site/reader/pbreak/'+V+'.WITHHELD','site/reader/pbreak/'+V+'.json'); }
  console.log('  WITHOUT pbreak: ¶='+b[0]+' letters='+b[1]+' <b>='+b[2]+' boldletters='+b[3]+' sha='+b[4]+' boldsha='+b[5]+'  rules='+b[6]);
  const same=a.slice(0,6).join()===b.slice(0,6).join();
  // NOT VACUOUS: the map must actually have drawn rules the withheld run did not.
  const bite=a[6]-b[6];
  console.log('  IDENTICAL once the rules are removed: '+same+(same?'':'   <<< THE RULES CHANGED THE TEXT'));
  console.log('  rules the map added: '+bite+(bite>0?'':'   <<< VACUOUS, the map drew nothing'));
  process.exit((same&&bite>0)?0:1);
})();

// PROBE 2: are the apparatus MARKERS all rendered?
// Reader: "some markers on the same page render as superscripts and some do
// not".  Probe 1 established the .appx note block is drawn on every paragraph
// whose data carries notes, in every band -- so the defect, if there is one, is
// in the MARKER in the running text, not in the note.
//
// Method: for every drawn paragraph of a volume, count the marker digits the
// raw `text` carries and the `sup.fnm` elements the DOM ended up with.  Any
// paragraph where the two differ is reported with its printed page.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }

const MARK=/[a-zāīūṁṅñṭḍṇḷ](\d{1,2})(?!\d)/g;
const VOLS=process.argv.slice(2).length?process.argv.slice(2)
  :['31KhuA12','32KhuA13','19Khu02','21Khu04','09DiT02'];

(async()=>{
  const w=boot();
  if(!await ready(w)){ console.log('nav never built'); process.exit(1); }
  for(const vol of VOLS){
    try{ await w.eval('openKey')(vol+'#0','canon'); }catch(e){ console.log(vol+' ERR '+e.message); continue; }
    for(let k=0;k<60;k++){ await wait(80);
      const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
    const c=(w.eval('cache')||{})[vol]||{}; const P=c.paras||[]; const bold=c.bold||{};
    let drawn=0, want=0, got=0, bad=[], badBold=0, badPlain=0;
    w.document.querySelectorAll('#scroll [id^="p-'+vol+'-"]').forEach(x=>{
      const o=+x.id.slice(('p-'+vol+'-').length); const p=P[o]; if(!p) return;
      drawn++;
      // the paragraph number is stripped before formatting, so strip it here too
      const t=String(p.text||'').replace(/^\s*\d+(-\d+)?\.\s*/,'');
      const exp=(t.match(MARK)||[]).length;
      const sup=x.querySelectorAll('sup.fnm').length;
      want+=exp; got+=sup;
      if(exp!==sup){ const hb=(bold[String(o)]||[]).length>0;
        if(hb) badBold++; else badPlain++;
        if(bad.length<8) bad.push({o,exp,sup,pg:p.printed,bold:hb}); }
    });
    console.log(`${vol}: drawn=${drawn}  markers in text=${want}  sup.fnm drawn=${got}`
      +`  paragraphs disagreeing=${badBold+badPlain} (with bold ${badBold}, without ${badPlain})`);
    bad.forEach(b=>console.log(`    ord ${b.o} p.${b.pg} bold=${b.bold}  text has ${b.exp}, page drew ${b.sup}`));
  }
  process.exit(0);
})();

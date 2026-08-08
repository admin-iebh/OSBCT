// PROBE 3: WHICH markers are lost, and where do the extra ones come from.
// Probe 2 localised the defect to paragraphs carrying BOLD spans.  This one
// lines the raw text's markers up against the ones the DOM ended with.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
async function ready(w){ for(let k=0;k<80;k++){ await wait(100);
  if(w.document.querySelectorAll('.row').length>3) return true; } return false; }
const MARK=/([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})(?!\d)/g;
const CASES=[['31KhuA12',[3,6,8,28]],['32KhuA13',[8,30]],['09DiT02',[14,13]],['19Khu02',[269,985]]];

(async()=>{
  const w=boot();
  if(!await ready(w)){ console.log('nav never built'); process.exit(1); }
  for(const [vol,ords] of CASES){
    try{ await w.eval('openKey')(vol+'#0','canon'); }catch(e){ console.log(vol+' ERR '+e.message); continue; }
    for(let k=0;k<60;k++){ await wait(80);
      const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>800) break; }
    const c=(w.eval('cache')||{})[vol]||{}; const P=c.paras||[];
    for(const o of ords){
      const p=P[o]; if(!p){ console.log(`${vol}#${o} not in volume`); continue; }
      const el=w.document.getElementById('p-'+vol+'-'+o);
      if(!el){ console.log(`${vol}#${o} not drawn`); continue; }
      const t=String(p.text||'').replace(/^\s*\d+(-\d+)?\.\s*/,'');
      const spans=(c.bold||{})[String(o)]||[];
      const off=String(p.text||'').length-t.length;
      const sp=spans.map(a=>[a[0]-off,a[1]-off]);
      const exp=[]; let m; MARK.lastIndex=0;
      while((m=MARK.exec(t))){
        const at=m.index+1;
        // does a bold span end exactly at this digit, or start on it?
        const endsHere=sp.some(a=>a[1]===at), startsHere=sp.some(a=>a[0]===at),
              inside=sp.some(a=>a[0]<at&&a[1]>at);
        exp.push({d:m[2], ctx:t.slice(Math.max(0,m.index-14),m.index+m[0].length+2),
                  endsHere, startsHere, inside});
      }
      const got=[...el.querySelectorAll('sup.fnm')].map(x=>x.textContent);
      console.log(`\n=== ${vol}#${o} p.${p.printed}  bold spans=${spans.length}  text markers=${exp.length}  drawn=${got.length}`);
      console.log('    drawn: '+got.join(' '));
      exp.forEach(e=>console.log(`    ${e.d}  boldEndsAtDigit=${e.endsHere} boldStartsAtDigit=${e.startsHere} insideBold=${e.inside}   …${e.ctx}…`));
    }
  }
  process.exit(0);
})();

// Exhaustive check of the REAL reader's resolveXref over every stored xref.
// One boot, all 32,259 citations — stronger than counting anchors per volume,
// and it catches a resolver that has started pointing at the wrong paragraph
// (which is exactly what the stale pageindex.json was doing, silently).
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
setTimeout(()=>{
  const w=dom.window; const PAR={};
  const printedAt=(vol,ord)=>{ if(!PAR[vol]) PAR[vol]=JSON.parse(fs.readFileSync('site/'+vol+'.json','utf8')).paragraphs.map(p=>p.printed); return PAR[vol][ord]; };
  let tot=0,live=0,grey=0,exact=0,near=0,wrong=[],byWork={};
  for(const f of fs.readdirSync(R+'/apparatus').filter(x=>x.endsWith('.appk.json'))){
    const vol=f.replace('.appk.json',''); const d=JSON.parse(fs.readFileSync(R+'/apparatus/'+f,'utf8'));
    for(const o of Object.keys(d)) for(const n of d[o]) for(const x of (n.xrefs||[])){
      tot++;
      const r=w.resolveXref(x.work,x.vol,x.page,vol);
      if(!r){ grey++; byWork[x.work]=(byWork[x.work]||0)+1; continue; }
      live++;
      const [tv,ord]=r.key.split('#');
      const got=printedAt(tv,+ord);
      if(String(got)===String(x.page)) exact++;
      else if(+got<=x.page) near++;
      else if(wrong.length<10) wrong.push([vol,x.work,x.vol,x.page,r.key,got]);
    }
  }
  console.log('xrefs           '+tot);
  console.log('  resolve       '+live+'  ('+(100*live/tot).toFixed(2)+'%)');
  console.log('    exact page  '+exact);
  console.log('    earlier page (page carries no paragraph start) '+near);
  console.log('    LANDS PAST THE CITED PAGE  '+wrong.length+(wrong.length?' <-- DEFECT':''));
  wrong.forEach(x=>console.log('      ',x.join(' ')));
  console.log('  grey          '+grey);
  Object.entries(byWork).sort((a,b)=>b[1]-a[1]).slice(0,10).forEach(([k,v])=>console.log('      '+String(v).padStart(4)+'  '+k));
  process.exit(0);
},3000);

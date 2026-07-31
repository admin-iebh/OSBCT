// Do the footnotes moved out of xrefs/ actually RENDER now?
// Boots the real reader, opens the ordinal each stranded note was filed under,
// and looks for the note's own words in the rendered apparatus.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){return new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;}
const KIND={canon:'canon',commentary:'A',subcommentary:'T'};
const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
const layerOf=v=>{for(const L of nav.layers)for(const n of L.nikayas)for(const x of n.volumes)if(x.vol===v)return L.layer;return 'canon';};
(async()=>{
  let ok=0,miss=0;
  for(const vol of process.argv.slice(2)){
    const raw=JSON.parse(fs.readFileSync(R+'/xrefs/'+vol+'.json','utf8'));
    const ords=Object.keys(raw).filter(o=>raw[o].length);
    if(!ords.length){console.log('  --   '+vol+' nothing stranded');continue;}
    const o=ords[0];
    // A citation-only note renders as its LINK LABEL, not as its source text —
    // `Khu 1. 399; Khu 10. 6, 59 piṭṭhesupi.` becomes `Khu 1. 399 ->`.  Probing
    // for the raw text called four of six volumes MISS on the first run, when
    // the notes were in fact on the page.  So probe for whichever form the
    // reader is going to draw.
    const src=raw[o][0].replace(/^\s*[*+]\s*/,'').replace(/\s+/g,' ').trim();
    const app=JSON.parse(fs.readFileSync(R+'/apparatus/'+vol+'.appk.json','utf8'));
    const note=(app[o]||[]).find(n=>(n.text||'').replace(/\s+/g,' ').trim()===src);
    const xs=note&&note.xrefs&&note.xrefs.length?note.xrefs:null;
    const probe=xs? (xs[0].work+(xs[0].vol?' '+xs[0].vol:'')+'. '+xs[0].page) : src.slice(0,40);
    const w=boot(); await wait(600);
    try{ w.openKey(vol+'#'+o, KIND[layerOf(vol)]); }catch(e){}
    await wait(900);
    const el=w.document.getElementById('p-'+vol+'-'+o);
    const scope=el?el.textContent:w.document.body.textContent;
    const txt=scope.replace(/\s+/g,' ');
    const found=txt.includes(probe);
    found?ok++:miss++;
    console.log('  '+(found?'ok  ':'MISS')+' '+vol.padEnd(11)+' ord '+o.padEnd(5)
      +(el?'':'[¶ NOT DRAWN] ')+(xs?'[as link] ':'[as text] ')+'"'+probe+'"');
    w.close();
  }
  console.log('\n'+ok+' rendered, '+miss+' missing');
  process.exit(miss?1:0);
})();

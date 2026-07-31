// Coverage of the in-place citation linking, over every note in the apparatus,
// using the reader's own appTextLinked(). Reports how many notes keep their
// words, how many fall back, and how many characters of the edition are
// recovered — and asserts the anchor count never falls.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const w=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}}).window;
setTimeout(()=>{
  let elig=0,inline=0,fell=0,gained=0,anchorsOld=0,anchorsNew=0;const ex=[];
  for(const f of fs.readdirSync(R+'/apparatus').filter(x=>x.endsWith('.appk.json'))){
    const vol=f.replace('.appk.json','');
    const d=JSON.parse(fs.readFileSync(R+'/apparatus/'+f,'utf8'));
    for(const o of Object.keys(d)) for(const n of d[o]){
      if(n.variants&&n.variants.length) continue;
      if(!n.xrefs||!n.xrefs.length||!n.text) continue;
      elig++;
      const old=n.xrefs.map(x=>x.work+(x.vol?' '+x.vol:'')+'. '+x.page).join('; ');
      anchorsOld+=n.xrefs.length;
      const html=w.appTextLinked(n.text,n.xrefs,vol);
      // A FALLBACK STILL DRAWS ITS CITATIONS, by the old path — counting only
      // the inline ones made this report 10 anchors "LOST" that were never lost.
      if(html==null){ fell++; anchorsNew+=n.xrefs.length; if(ex.length<6) ex.push([vol,n.text.slice(0,70)]); continue; }
      inline++;
      anchorsNew+=(html.match(/class="xref"/g)||[]).length;
      gained+=Math.max(0,n.text.length-old.length);
    }
  }
  console.log('notes with citations and no variants : '+elig);
  console.log('  linked in place, words kept        : '+inline+'  ('+(100*inline/elig).toFixed(1)+'%)');
  console.log('  fell back to the old rendering     : '+fell);
  console.log('  characters of the edition recovered: ~'+gained.toLocaleString());
  console.log('  xref elements: old '+anchorsOld+' -> new '+anchorsNew+(anchorsNew<anchorsOld?'   <-- LOST':'   (none lost)'));
  ex.forEach(e=>console.log('   fallback e.g. '+e[0]+'  '+JSON.stringify(e[1])));
  process.exit(anchorsNew<anchorsOld?1:0);
},3000);

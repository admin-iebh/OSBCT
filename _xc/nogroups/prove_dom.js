// Browser proof (jsdom) that the no-`groups` `before`/`after` material now
// reaches the rendered DOM -- and did not before.
//
//   node _xc/nogroups/prove_dom.js <READER.html> <VOL>#<ORD> [...]
//
// !!! JSDOM DOES NOT FETCH `<script src>`.  reader2.html pulls in `../i18n.js`
// and `panel.js` that way; booting it unmodified runs a reader missing two of
// its scripts, which is how a "verified" fix reached the reader broken on
// 2026-08-02.  Both are INLINED into a temp copy here before the DOM is built.
const fs=require('fs'), path=require('path'), os=require('os');
const {JSDOM}=require('jsdom');
const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];
  if(u.startsWith('../'))return path.join('site',u.slice(3));
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}
  return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));

function inlined(readerPath){
  let h=fs.readFileSync(readerPath,'utf8');
  let n=0;
  h=h.replace(/<script src="([^"]+)"([^>]*)><\/script>/g,(m,src,attrs)=>{
    const f=resolve(src);
    let t; try{ t=fs.readFileSync(f,'utf8'); }catch(e){ return m; }
    n++;
    // `defer` on an inline script is ignored by the parser, so a deferred file
    // must still run after the document is parsed: wrap it in DOMContentLoaded.
    if(/defer/.test(attrs))
      return '<script>document.addEventListener("DOMContentLoaded",function(){'+t+'\n});</script>';
    return '<script>'+t+'</script>';
  });
  if(n<2) throw new Error('expected to inline 2 <script src>, inlined '+n);
  const p=path.join(R,'_prove_tmp_reader.html');
  fs.writeFileSync(p,h);
  return {p,n};
}

function boot(file){
  const dom=new JSDOM(fs.readFileSync(file,'utf8'),{runScripts:'dangerously',
    pretendToBeVisual:true,url:'http://x/',beforeParse(w){
      w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,
          json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};
    }});
  return dom.window;
}

const ALPHA=/[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]/g;
const L=s=>String(s||'').replace(ALPHA,'');

function flat(e,role){
  const x=e[role]; if(x==null) return [];
  const xs=Array.isArray(x)?x:[x]; const out=[];
  for(const p of xs){
    if(p&&typeof p==='object'&&p.gatha) for(const l of p.gatha) out.push(['gatha',l]);
    else if(p&&typeof p==='object'&&p.t!=null) out.push(['t',p.t]);
    else out.push(['str',p]);
  }
  return out;
}

(async()=>{
  const readerArg=process.argv[2];
  const targets=process.argv.slice(3);
  const {p:tmp,n}=inlined(readerArg);
  console.log('reader:',readerArg,' inlined <script src>:',n);
  const w=boot(tmp);
  await wait(1500);
  let fail=0;
  for(const tg of targets){
    const [vol,ord]=tg.split('#');
    const layer=(()=>{try{const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
      for(const Lr of nav.layers||[])for(const nk of Lr.nikayas||[])for(const v of nk.volumes||[])
        if(v.vol===vol) return Lr.layer;}catch(e){} return 'canon';})();
    const kind={canon:'canon',commentary:'A',subcommentary:'T'}[layer];
    try{ w.eval('state.curbook=null;state.curvagga=null;state.cursutta=null;'); }catch(e){}
    try{ await w.openKey(vol+'#'+ord, kind); }catch(e){ console.log('openKey threw',e.message); }
    for(let k=0;k<80;k++){ await wait(90);
      const s=w.document.querySelector('#scroll'); if(!s) continue;
      if(s.querySelector('#p-'+vol+'-'+ord)) break; }
    const el=w.document.querySelector('#p-'+vol+'-'+ord);
    const doc=L(w.document.querySelector('#scroll').textContent);
    const V=JSON.parse(fs.readFileSync(`${R}/verse/${vol}.json`,'utf8'))[ord];
    let tot=0,hit=0,inpara=0;
    const para=el?L(el.textContent):'';
    for(const role of ['before','after'])
      for(const [k,t] of flat(V||{},role)){
        tot++; const s=L(t); if(!s){hit++;inpara++;continue;}
        if(doc.includes(s)) hit++;
        if(para.includes(s)) inpara++;
      }
    const cls=el?el.className:'(paragraph not rendered)';
    console.log(`  ${tg}  items ${tot}  in #scroll ${hit}  inside the paragraph div ${inpara}   [${cls}]`);
    if(hit<tot) fail++;
    // where the number went: it must be INSIDE the block that carries the
    // corpus text, not stranded above the `before` material
    if(el){
      const pn=el.querySelector('.pn');
      const kids=[...el.children].map(c=>c.className).join(' | ');
      console.log('     first .pn parent:', pn?pn.parentElement.className:'(none)',
                  ' | child blocks:', kids.slice(0,180));
    }
  }
  try{ fs.unlinkSync(tmp); }catch(e){ try{fs.renameSync(tmp,'_to_delete/'+path.basename(tmp)+'.'+Date.now());}catch(e2){} }
  process.exit(fail?1:0);
})();

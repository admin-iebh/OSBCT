// The paragraph number must go INSIDE the block that carries the corpus text
// when a groupless entry supplies `before` material -- emitted outside `body`
// it would stand on a line of its own ABOVE the `before`, which the printed
// page never does.
//
// NO SHIPPED ENTRY EXERCISES THIS: all 75 groupless entries sit on paragraphs
// with no printed number.  So the case is made SYNTHETICALLY here, in the live
// reader's own cache, and the assertion is on the rendered DOM.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];
  if(u.startsWith('../'))return path.join('site',u.slice(3));
  if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}
  return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlined(rp){let h=fs.readFileSync(rp,'utf8');let n=0;
  h=h.replace(/<script src="([^"]+)"([^>]*)><\/script>/g,(m,src,attrs)=>{const f=resolve(src);
    let t;try{t=fs.readFileSync(f,'utf8');}catch(e){return m;}n++;
    return /defer/.test(attrs)?'<script>document.addEventListener("DOMContentLoaded",function(){'+t+'\n});</script>':'<script>'+t+'</script>';});
  if(n<2) throw new Error('inlined only '+n+' <script src>');
  const p=path.join(R,'_prove_num_tmp.html');fs.writeFileSync(p,h);return p;}
(async()=>{
  const tmp=inlined('site/reader/reader2.html');
  const dom=new JSDOM(fs.readFileSync(tmp,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',
    beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
      w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}
        return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  const w=dom.window; await wait(1500);
  const vol='50AbhiA03', kind='A';
  try{ await w.openKey(vol+'#47', kind); }catch(e){}
  for(let k=0;k<80;k++){ await wait(90); const s=w.document.querySelector('#scroll');
    if(s&&s.querySelector('.para.l-A .pn')) break; }
  // ANY numbered paragraph on screen: its verse entry is REPLACED by a
  // groupless `{before:[...]}`, which is the shape under test.
  const ord=w.eval(`(function(){const c=cache['${vol}'];
      const els=[...document.querySelectorAll('.para')];
      for(const el of els){ const m=/^p-${vol}-(\\d+)$/.exec(el.id||''); if(!m) continue;
        const i=+m[1];
        if(c.paras[i]&&c.paras[i].n!=null) return i; }
      return -1;})()`);
  if(ord<0){
    console.log('DEBUG cache keys:', w.eval("Object.keys(cache).join(',')"));
    console.log('DEBUG paras:', w.eval(`(cache['${vol}']&&cache['${vol}'].paras||[]).length`));
    console.log('DEBUG ids:', w.eval("[...document.querySelectorAll('.para')].slice(0,6).map(e=>e.id).join(' ')"));
    console.log('DEBUG n at 47:', w.eval(`JSON.stringify((cache['${vol}'].paras[47]||{}).n)`));
    console.log('DEBUG rendered:', w.eval(`(function(){const c=cache['${vol}'];return [...document.querySelectorAll('.para')].map(e=>{const m=/^p-${vol}-(\\d+)$/.exec(e.id||'');return m?(m[1]+':'+JSON.stringify((c.paras[+m[1]]||{}).n)):'?';}).slice(0,40).join(' ');})()`));
    console.log('DEBUG probe47:', w.eval(`JSON.stringify([ (cache['${vol}'].paras[47]||{}).n, !!(cache['${vol}'].verse||{})['47'], !!document.getElementById('p-${vol}-47') ])`));
    console.log('FAIL: no numbered on-screen paragraph found'); process.exit(1); }
  const before=w.eval(`document.getElementById('p-${vol}-${ord}').outerHTML`);
  const bpn=/class="pn[^"]*"/.test(before);
  w.eval(`cache['${vol}'].verse=cache['${vol}'].verse||{};
          cache['${vol}'].verse['${ord}']={before:['SYNTHETICBEFORELINE']};render();`);
  await wait(600);
  const el=w.document.getElementById('p-'+vol+'-'+ord);
  const pn=el.querySelector('.pn');
  const kids=[...el.children].map(c=>c.className);
  const hasSynth=el.textContent.includes('SYNTHETICBEFORELINE');
  const pnParent=pn?pn.parentElement.className:'(none)';
  const pnIsDirectChild = pn && pn.parentElement===el;
  console.log('ord',ord,'| had .pn before injection:',bpn);
  console.log('  synthetic `before` drawn:',hasSynth);
  console.log('  .pn parent after injection:',pnParent,'| direct child of .para:',!!pnIsDirectChild);
  console.log('  child blocks:',kids.join(' | '));
  const ok = hasSynth && pn && !pnIsDirectChild && /gatha-after/.test(pnParent);
  console.log(ok?'PASS  the number moved inside the corpus-text block'
                :'FAIL  the number is not inside the corpus-text block');
  try{ fs.unlinkSync(tmp); }catch(e){}
  process.exit(ok?0:1);
})();

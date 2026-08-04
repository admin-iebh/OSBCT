// REPRODUCE THE READER'S CONFIGURATION: sidebar click on "1. Saraṇattaya",
// then press A, Spanish, Simple view.  Drive the real UI, not state.eval.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const RES=process.argv.includes('--res');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(lang){
  let HTML=fs.readFileSync(R+'/reader2.html','utf8');
  if(RES){ HTML=HTML.replace(/<script src="\.\.\/i18n\.js[^"]*"><\/script>/,'<script>'+fs.readFileSync('site/i18n.js','utf8')+'</'+'script>')
                     .replace(/<script src="panel\.js[^"]*" defer><\/script>/,'')
                     .replace('</body>','<script>'+fs.readFileSync(R+'/panel.js','utf8')+'</'+'script></body>'); }
  const dom=new JSDOM(HTML,{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
    if(lang) try{ w.localStorage.setItem('osbct-lang',lang); }catch(e){}
    w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
  return dom.window;
}
const LANG=process.argv[2]||'es';
const VIA=process.argv[3]||'tree';   // tree | direct
(async()=>{
  const w=boot(LANG); const errs=[]; w.addEventListener('error',e=>errs.push(e.message));
  await wait(1200);
  const doc=w.document;
  if(VIA==='tree'){
    // find the sidebar row labelled "1. Saraṇattaya" the way the reader does
    const rows=[...doc.querySelectorAll('#tree .row, .row')];
    let hit=rows.filter(r=>/Sara[ṇn]attaya/.test(r.textContent||''));
    console.log('rows total='+rows.length+'  Saranattaya rows='+hit.length+' -> '+hit.map(r=>JSON.stringify(r.textContent.trim())).join(' | '));
    if(!hit.length){
      // expand: the nav is lazy.  click Khuddaka volume rows first
      const kv=rows.filter(r=>/Khuddaka/i.test(r.textContent||''));
      console.log('khuddaka rows='+kv.length+' :: '+kv.slice(0,8).map(r=>r.textContent.trim()).join(' | '));
      for(const r of kv.slice(0,4)){ r.click(); await wait(400); }
      const rows2=[...doc.querySelectorAll('.row')];
      hit=rows2.filter(r=>/Sara[ṇn]attaya/.test(r.textContent||''));
      console.log('after expand: rows='+rows2.length+' Saranattaya='+hit.length);
    }
    if(!hit.length){ console.log('COULD NOT FIND THE TREE ROW'); }
    else { hit.forEach((r,ix)=>console.log('  hit['+ix+'] = '+JSON.stringify(r.textContent.trim())+' depth-class='+r.className));
      const pick=(process.env.PICK!=null)?hit[+process.env.PICK]:hit[0];
      pick.click(); await wait(2500); }
  } else {
    await w.openKey('18Khu01#0','canon'); await wait(1800);
  }
  console.log('state: canonVol='+w.eval('state.canonVol')+' cursutta='+w.eval('String(state.cursutta)')
    +' curbook='+w.eval('String(state.curbook)')+' curvagga='+w.eval('String(state.curvagga)')
    +' view='+w.eval('state.view')+' filter='+w.eval('String(state.filter)')
    +' lang='+w.eval('String(typeof osbctLang!=="undefined"?osbctLang():"NO-I18N")'));
  console.log('doctitle: '+(doc.querySelector('#doctitle')||{}).textContent);
  // now PRESS A exactly as the reader does
  const ab=[...doc.querySelectorAll('.lbtn')].find(b=>b.dataset.k==='A');
  console.log('A button found='+!!ab+' classes='+(ab?ab.className:''));
  ab.click(); await wait(3000);
  console.log('after A: active='+w.eval('JSON.stringify(state.active)')+' filter='+w.eval('String(state.filter)'));
  const c0=doc.getElementById('p-18Khu01-0');
  console.log('canon p-18Khu01-0 present='+!!c0);
  if(c0){
    const band=c0.parentElement.querySelector('.subwrap.a');
    console.log('A band under canon 0 = '+!!band);
    if(band){
      const ids=[...band.querySelectorAll('.para[id]')].map(p=>p.id);
      console.log('RUN LENGTH = '+ids.length);
      console.log('ords = '+ids.map(i=>i.split('-').pop()).join(','));
      console.log('runmore control = '+!!band.querySelector('button.runmore')
        +'  text='+JSON.stringify((band.querySelector('button.runmore')||{}).textContent));
    }
  }
  const allA=[...doc.querySelectorAll('#scroll .para[id^="p-20KhuA01-"]')].map(p=>p.id);
  console.log('total 20KhuA01 paras on page = '+allA.length);
  console.log('errors: '+JSON.stringify(errs.slice(0,3)));
  const R2=w.eval('JSON.stringify(Object.keys(RUNS))');
  console.log('RUNS keys='+R2);
  console.log('runsFor A end[20KhuA01#9]='+w.eval('String(runsFor("A").end["20KhuA01#9"])')
    +'  first='+w.eval('String(runsFor("A").first["20KhuA01#9"])'));
  console.log('VOLGROUP 18Khu01='+w.eval('String(VOLGROUP["18Khu01"])')+' 20KhuA01='+w.eval('String(VOLGROUP["20KhuA01"])'));
  console.log('cache has 20KhuA01='+w.eval('String(!!cache["20KhuA01"])'));
  console.log('runBounds(20KhuA01)='+w.eval('JSON.stringify(runBounds("20KhuA01").slice(0,6))'));
  w.close();
})();

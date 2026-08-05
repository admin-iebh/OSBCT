// Where to look, taken from the RENDERED page rather than guessed from data.
//
// Twice now a locator given from the link map has sent the reader to the wrong
// paragraph, because the map is keyed by paragraph INDEX and the page shows the
// PRINTED number.  So this boots the reader, renders, finds the actual
// `.runmore` controls on the page, and reports for each one: the canon
// paragraph's printed number, how many paragraphs are shown before the control,
// how many it hides, and how many characters are visible.
//
//   node _xc/hy2/wherelook.js <CANONVOL> [maxRows]
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inlineScripts(html){
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g,(m,u)=>{
    const f=resolve(u); let t=null; try{ t=fs.readFileSync(f,'utf8'); }catch(e){}
    return t==null?m:'<script>'+t+'</script>'; });
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
const VOL=process.argv[2]||'19Khu02', MAX=+(process.argv[3]||8);
(async()=>{
  const w=boot(); await wait(400);
  // PRESS THE BUTTON, do not set state.active — the handler clears the filter,
  // calls ensureBandVols and re-renders through keepPlace.  Setting the flag
  // renders nothing and reports zero controls, which is what the first version
  // of this file did.
  await w.openKey(VOL+'#0','canon'); await wait(1500);
  const ab=[...w.document.querySelectorAll('.lbtn')].find(b=>b.dataset.k==='A');
  if(!ab){ console.log('no A layer button'); process.exit(1); }
  ab.click(); await wait(4000);
  const doc=w.document;
  const paras=JSON.parse(fs.readFileSync('site/'+VOL+'.json','utf8')).paragraphs;
  const rows=[];
  doc.querySelectorAll('button.runmore').forEach(btn=>{
    const box=doc.getElementById(btn.dataset.box);
    const wrap=btn.parentElement;
    // the canon paragraph this band hangs under
    let el=wrap, canon=null;
    while(el&&!canon){ el=el.previousElementSibling||el.parentElement;
      if(el&&el.id&&el.id.startsWith('p-'+VOL+'-')) canon=el.id; }
    const shown=[...wrap.querySelectorAll('.para[id]')]
      .filter(p=>!box.contains(p));
    const chars=shown.reduce((s,p)=>s+p.textContent.length,0);
    const idx=canon?+canon.slice(('p-'+VOL+'-').length):null;
    // !!! THE PRINTED NUMBER IS NOT UNIQUE WITHIN A VOLUME EITHER.  19Khu02
    // prints ¶618 three times -- Vimānavatthu p48, Petavatthu p195, Theragāthā
    // p309 -- so "19Khu02 ¶618" still sends the reader to one of three places.
    // A locator is only a locator with the book and vagga on it.
    const P=idx!=null?paras[idx]:null;
    rows.push({printed:P?P.n:'?', idx,
               book:P?(P.book||''):'', vagga:P?(P.vagga||''):'', page:P?P.printed:'',
               band:wrap.className.indexOf('t')>=0?'T':'A',
               shown:shown.length, hidden:+btn.dataset.n, chars,
               first:(shown[0]?shown[0].textContent:'').slice(0,60)});
  });
  rows.sort((a,b)=>b.hidden-a.hidden);
  console.log('%s — %d Read-more controls on the opened page\n', VOL, rows.length);
  // Node's console.log understands %s but NOT printf width specifiers, so
  // '%-9s' prints literally.  padEnd, not a format string.
  const P=(v,n)=>String(v).padEnd(n);
  console.log(P('¶',7)+P('pg',6)+P('band',5)+P('shown',6)+P('hid',5)+P('chars',7)
              +P('book',24)+'vagga');
  rows.slice(0,MAX).forEach(r=>console.log(
    P(r.printed,7)+P('p'+r.page,6)+P(r.band,5)+P(r.shown,6)+P(r.hidden,5)+P(r.chars,7)
    +P(r.book,24)+r.vagga));
})();

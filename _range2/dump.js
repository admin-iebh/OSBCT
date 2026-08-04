const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');
const RDR=process.env.RDR||'site/reader/reader2.html'; const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
let HTML=fs.readFileSync(RDR,'utf8');
HTML=HTML.replace(/<script src="\.\.\/i18n\.js[^"]*"><\/script>/,'<script>'+fs.readFileSync('site/i18n.js','utf8')+'</'+'script>');
HTML=HTML.replace(/<script src="panel\.js[^"]*"( defer)?><\/script>/,'');
const dom=new JSDOM(HTML,{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){
  w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
  w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};
  try{ w.localStorage.setItem('osbct-lang','es'); }catch(e){}
  w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;
(async()=>{
  await wait(1200);
  const doc=w.document;
  let rows=[...doc.querySelectorAll('.row')];
  for(const r of rows.filter(r=>/Khuddaka/i.test(r.textContent||'')).slice(0,4)){ r.click(); await wait(400); }
  rows=[...doc.querySelectorAll('.row')];
  const hit=rows.filter(r=>/^1\. Saraṇattaya$/.test((r.textContent||'').trim()));
  hit[0].click(); await wait(2500);
  const ab=[...doc.querySelectorAll('.lbtn')].find(b=>b.dataset.k==='A'); ab.click(); await wait(3000);
  console.log('BUILD='+w.eval('BUILD')+'  title='+doc.querySelector('#doctitle').textContent);
  // walk the visible stream from the top
  const sc=doc.querySelector('#scroll');
  global.OUT=[]; const out=global.OUT; let n=0;
  (function walk(el){ for(const c of el.children){
      if(c.hasAttribute&&c.hasAttribute('hidden')){ out.push('  [HIDDEN BOX: '+c.querySelectorAll('.para').length+' paras]'); continue; }
      if(c.classList.contains('para')){ const t=(c.textContent||'').replace(/\s+/g,' ').trim();
        out.push((c.id||'?')+' :: '+t.slice(0,70)+' … '+t.slice(-45)); n++; if(n>26) throw 'STOP'; continue; }
      if(c.classList.contains('head')||c.classList.contains('lchip')||c.classList.contains('runmore')||c.classList.contains('pgrule')||c.classList.contains('uddana')||c.classList.contains('incipit')||c.classList.contains('gatha')||c.classList.contains('secprose')){
        out.push('<'+c.className+'> '+(c.textContent||'').replace(/\s+/g,' ').trim().slice(0,80)); if(!c.children.length) continue; }
      walk(c); } })(sc);
})().catch(e=>{ if(e!=='STOP') console.log('ERR',e); }).finally(()=>{
  if(global.OUT) console.log(global.OUT.join('\n'));
  console.log('--- end ---'); process.exit(0);
});

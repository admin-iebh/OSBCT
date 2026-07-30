// Apadāna cross-volume tree — presentation assertions.
// The tree is the thing the user specified, so its shape is asserted here: the
// edition's own division (one Apadānapāḷi -> Therāpadāna -> Therīapadāna),
// Therāpadāna's vagga numbering CONTINUOUS 1-56 across the physical volume
// break, and each vagga opening only its own text.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
const N=s=>s.normalize('NFC').replace(/\s+/g,' ').toLowerCase();
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<80;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);

(async()=>{
  const w=boot(); let err=null; w.addEventListener('error',e=>err=e.message);
  if(!await ready(w)){console.log('nav never rendered');process.exit(1);}
  A(!err,'JS error on boot: '+err);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(60);}}

  const book=find(w,'Apadānapāḷi');
  A(!!book,'no Apadānapāḷi row — the tree still follows the physical volumes');
  if(!book){console.log(`\n${pass} passed, ${fail} failed`);process.exit(1);}
  book.click(); await wait(80);
  const bk=book.parentElement.querySelector('.kids');
  const works=[...bk.children].map(c=>c.querySelector(':scope > .row')).filter(Boolean).map(lbl);
  A(works.length===2&&works[0]==='Therāpadāna'&&works[1]==='Therīapadāna',
    'Apadāna divisions = '+JSON.stringify(works));

  // Therāpadāna: 56 vaggas, numbered continuously across the 20Khu03/21Khu04 break
  const tw=[...bk.children][0]; tw.querySelector(':scope > .row').click(); await wait(80);
  const vk=tw.querySelector('.kids');
  const vags=[...vk.children].map(c=>c.querySelector(':scope > .row')||c);
  A(vags.length===56,'Therāpadāna vaggas = '+vags.length+', the edition has 56');
  const nums=vags.map(v=>parseInt(lbl(v),10));
  const want=Array.from({length:56},(_,i)=>i+1);
  A(JSON.stringify(nums)===JSON.stringify(want),
    'vagga numbering must be 1-56 CONTINUOUS across the volume break, got '+JSON.stringify(nums));
  // the break itself: vagga 42 in 20Khu03, vagga 43 in 21Khu04
  // Leaf counts come from nav.json — the same data the tree renders — because
  // expanding all 559 rows in three jsdom windows exhausts the heap.
  const nav=JSON.parse(fs.readFileSync(R+'/nav.json','utf8'));
  const kh=nav.layers.find(L=>L.layer==='canon').nikayas.find(n=>n.nikaya==='Khuddakanikāya');
  const apa=kh.volumes.find(v=>v.title==='Apadānapāḷi');
  const cnt=w2=>w2.kids.reduce((a,v)=>a+v.kids.length,0);
  A(cnt(apa.tree[0])===563,'Therāpadāna apadāna leaves = '+cnt(apa.tree[0])+', the edition has 563 (10 a vagga, +2 in Buddhavagga, +1 in Yasavagga)');
  const bad=apa.tree[0].kids.filter(v=>v.kids.length!==({'1. Buddhavagga':12,'56. Yasavagga':11}[v.label]||10));
  A(bad.length===0,'vaggas not matching the edition 10-a-vagga rule: '+JSON.stringify(bad.map(v=>[v.label,v.kids.length])));
  A(cnt(apa.tree[1])===40,'Therīapadāna apadāna leaves = '+cnt(apa.tree[1])+', the edition has 40');
  // the volume break falls between vagga 42 and 43 and nowhere else
  const vv=apa.tree[0].kids.map(v=>v.key.split('#')[0]);
  const brk=vv.map((x,i)=>i>0&&x!==vv[i-1]?i:-1).filter(i=>i>=0);
  A(brk.length===1&&brk[0]===42,'volume break at vagga index '+brk+', expected exactly one at 42');

  // a vagga on each side of the break opens ONLY its own text
  for(const [name,openWord,notWord] of [
      ['1. Buddhavagga','Tathāgataṁ Jetavane vasantaṁ','Vipassino Bhagavato, pāṭaliṁ'],
      ['43. Sakiṁsammajjakavagga','Vipassino Bhagavato, pāṭaliṁ','Tathāgataṁ Jetavane vasantaṁ']]){
    const w2=w;
    const row=find(w2,name); A(!!row,'no row for '+name);
    if(row){ row.click();
      for(let k=0;k<70;k++){await wait(80);const s=w2.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
      const txt=N(w2.document.querySelector('#scroll').textContent);
      A(txt.includes(N(openWord)), name+': its own opening verse is missing');
      A(!txt.includes(N(notWord)), name+': BLEEDS text from the other side of the volume break');
    }
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

// The four things reported from the screenshots.
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
  const w=boot(); await ready(w);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(60);}}

  // (1) the four apadānas the edition numbers "3-N." are in the tree
  find(w,'Apadānapāḷi').click(); await wait(60);
  find(w,'Therāpadāna').click(); await wait(60);
  const bv=find(w,'1. Buddhavagga'); A(!!bv,'no Buddhavagga row');
  bv.click(); await wait(80);
  const kids=[...bv.parentElement.querySelector('.kids').children].map(c=>lbl(c.querySelector(':scope > .row')||c));
  for(const t of ['3-1. Sāriputtatthera-apadāna','3-2. Mahāmoggallānatthera-apadāna',
                  '3-9. Khadiravaniyarevatatthera-apadāna','3-10. Ānandatthera-apadāna'])
    A(kids.includes(t), 'missing from the tree: '+t);
  A(kids.length===12,'Buddhavagga leaves = '+kids.length+', the edition sets 12');

  // (2) the book title renders centred and larger than any heading inside the book
  find(w,'1. Buddhavagga').click();
  for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1500)break;}
  const doc=w.document;
  const bt=doc.querySelector('#scroll .head.booktitle');
  A(!!bt && bt.textContent.trim()==='Therāpadānapāḷi','book title not rendered as .head.booktitle');
  // printed order: title -> homage -> first heading
  const html=doc.querySelector('#scroll').innerHTML;
  const iT=html.indexOf('booktitle'), iI=html.indexOf('incipit'), iV=html.indexOf('Buddhavagga');
  A(iT>=0&&iT<iI&&iI<iV,'printed order must be book title -> homage -> first heading');
  // (3) it must not still be inside a gatha block
  A(![...doc.querySelectorAll('#scroll .gatha')].some(g=>g.textContent.trim()==='Therāpadānapāḷi'),
    'book title still rendered as a gāthā line');
  // and the opener sits under its own heading, not above it
  const t2=N(doc.querySelector('#scroll').textContent);
  const iH=t2.indexOf(N('3-1. Sāriputtatthera-apadāna')), iA=t2.indexOf(N('Atha therāpadānaṁ suṇātha'));
  A(iH>=0&&iA>iH,'"Atha therāpadānaṁ suṇātha–" must follow its heading, not precede it');

  // (4) a book must STOP at its own end
  for(const [name,own,notWord] of [
      ['56. Yasavagga','Raṭṭhapālattherassāpadānaṁ','Sumedhātherī'],
      ['4. Khattiyāvagga','Pesalātheriyāpadānaṁ','Brahmā ca lokādhipatī']]){
    const row=find(w,name); A(!!row,'no row for '+name);
    if(!row) continue;
    row.click();
    for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1200)break;}
    const t=N(w.document.querySelector('#scroll').textContent);
    A(t.includes(N(own)), name+': its own closing colophon is missing');
    A(!t.includes(N(notWord)), name+': RUNS ON past the end of its book into "'+notWord+'"');
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

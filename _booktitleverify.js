// EVERY book must announce itself with the name its title page prints, as a
// title — centred, larger than any heading inside the book, and above the
// homage. A volume holding several books otherwise runs one into the next with
// nothing marking the change, which is what the user reported for all nine
// books of 18Khu01 and 19Khu02.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function boot(){const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});return dom.window;}
let pass=0,fail=0; const A=(ok,m)=>{ok?pass++:(fail++,console.log('   FAIL: '+m));};
async function ready(w){for(let k=0;k<80;k++){await wait(100);if(w.document.querySelectorAll('.row').length>100)return true;}return false;}
const lbl=r=>((r.querySelector('.lbl')||{}).textContent||'').trim();
const find=(w,t)=>[...w.document.querySelectorAll('.row')].find(r=>lbl(r)===t);

// DATA LAYER: every canon volume must carry a title for each of its book heads,
// and every printed homage must have one at the same ordinal.
const man=JSON.parse(fs.readFileSync(R+'/manifest.json','utf8')).volumes;
const VOLS=Object.keys(man).filter(v=>man[v].layer==='canon').sort();
// 40Abhi12's Paṭṭhāna restarts a book mid-page with no title page at all; those
// heads are FLAGGED by the builder, not guessed, and are excluded here until
// that volume's book structure is built.
const NOTITLEPAGE={'40Abhi12':true};
(async()=>{
  let vols=0, titles=0;
  for(const v of VOLS){
    let btl={}; try{btl=JSON.parse(fs.readFileSync(R+'/booktitle/'+v+'.json','utf8'));}catch(e){}
    A(Object.keys(btl).length>0, v+': no book title at all');
    vols++; titles+=Object.keys(btl).length;
    let inc={}; try{inc=JSON.parse(fs.readFileSync(R+'/incipit/'+v+'.json','utf8'));}catch(e){}
    if(NOTITLEPAGE[v]) continue;
    for(const k of Object.keys(inc))
      A(btl[k]!==undefined, `${v}#${k}: prints a homage but has no book title`);
    // the value is the printed stack: [series…, book]. The edition names the
    // collection above the book on every one of these title pages, so a single
    // line means the series line was dropped.
    const SERIES=/^(Dīghanikāya|Majjhimanikāya|Saṁyuttanikāya|Aṅguttaranikāya|Khuddakanikāya|Vinayapiṭaka|Abhidhammapiṭaka)$/;
    // ...EXCEPT WHERE THE PAGE ITSELF SETS ONE LINE.  02Vin02's SECOND title
    // page (printed p287) heads the Bhikkhunīvibhaṅga with its name alone and
    // does NOT repeat "Vinayapiṭaka" above it, where its first title page
    // does.  Read off that page and checked against it; NAMED here rather than
    // relaxing the rule, so any other one-line stack is still a dropped series
    // line.  (2026-07-26ag)
    const ONELINE={'02Vin02#661':'Bhikkhunīvibhaṅga'};
    for(const k of Object.keys(btl)){
      const t=Array.isArray(btl[k])?btl[k]:[btl[k]];
      if(ONELINE[v+'#'+k]!==undefined){
        A(t.length===1 && t[0]===ONELINE[v+'#'+k],
          `${v}#${k}: the edition sets ONE line here; got ${JSON.stringify(t)}`);
        continue;
      }
      A(t.length>=2, `${v}#${k}: only ${JSON.stringify(t)} — the series line above the book name is missing`);
      A(SERIES.test(t[0]), `${v}#${k}: first line ${JSON.stringify(t[0])} is not a nikāya/piṭaka name`);
      const last=t[t.length-1];
      A(last && last.length>3 && !/[.!?]$/.test(last), `${v}#${k}: implausible book name ${JSON.stringify(last)}`);
    }
  }
  console.log(`   (${vols} canon volumes, ${titles} book titles)`);

  // and it must actually render, above the homage, in the title class
  const w=boot(); await ready(w);
  for(const t of ['Pāḷi','Khuddakanikāya']){const r=find(w,t); if(r){r.click(); await wait(60);}}
  for(const [book,title] of [['Khuddakapāṭhapāḷi','Khuddakapāṭhapāḷi'],
                             ['Suttanipātapāḷi','Suttanipātapāḷi'],
                             ['Theragāthāpāḷi','Theragāthāpāḷi'],
                             ['Therīgāthāpāḷi','Therīgāthāpāḷi']]){
    const row=find(w,book); A(!!row,'no nav row for '+book);
    if(!row) continue;
    row.click();   // a book row must OPEN the book, not merely expand it
    for(let k=0;k<70;k++){await wait(80);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>1200)break;}
    const doc=w.document, bt=doc.querySelector('#scroll .head.booktitle');
    A(!!bt && bt.textContent.trim()===title, book+': title not rendered (.head.booktitle)');
    const sr=doc.querySelector('#scroll .head.bookseries');
    A(!!sr && sr.textContent.trim()==='Khuddakanikāya', book+': series line above the title missing');
    const html=doc.querySelector('#scroll').innerHTML;
    const iT=html.indexOf('booktitle'), iI=html.indexOf('incipit');
    A(iT>=0 && iI>=0 && iT<iI, book+': the title must sit ABOVE the homage, as the page sets it');
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})();

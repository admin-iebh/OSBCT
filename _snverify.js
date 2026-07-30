// jsdom render check for the rebuilt Suttanipāta side-maps.
// Renders each of the 5 vaggas in turn (which also exercises VAGGASPAN slicing)
// and asserts against the printed PDF content.
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const rows=()=>[...w.document.querySelectorAll('.row')];
let fails=0;
function ck(name,cond,extra){ if(!cond) fails++; console.log((cond?'  ok  ':'  FAIL')+' '+name+(extra!=null?'  ['+extra+']':'')); }
(async()=>{
  await wait(900);
  rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click(); await wait(200);
  const sn=rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi'); sn?.click(); await wait(250);
  const VAGGAS=['1. Uragavagga','2. Cūḷavagga','3. Mahāvagga','4. Aṭṭhakavagga','5. Pārāyanavagga'];
  const inSN=()=>{const b=rows().find(r=>r.textContent.trim()==='Suttanipātapāḷi');
                  return b?[...b.parentElement.querySelectorAll('.row')]:[];};
  let txt='', stats={para:0,gatha:0,prose:0};
  for(const v of VAGGAS){
    const row=inSN().find(r=>r.textContent.trim()===v);
    if(!row){ console.log('  FAIL could not find vagga row '+v); fails++; continue; }
    row.click();
    for(let k=0;k<80;k++){ await wait(80); const s=w.document.querySelector('#scroll'); if(s&&s.textContent.length>3000) break; }
    const s=w.document.querySelector('#scroll');
    const t=s?s.textContent:'';
    stats.para+=w.document.querySelectorAll('#scroll .para.canon').length;
    stats.gatha+=w.document.querySelectorAll('#scroll .gatha').length;
    stats.prose+=w.document.querySelectorAll('#scroll .gatha-after').length;
    console.log('  rendered '+v+': '+t.length+' chars, '+w.document.querySelectorAll('#scroll .para.canon').length+' ¶');
    txt+='\n'+t;
  }
  console.log('JS error:',err||'none');
  console.log('TOTAL paragraphs:',stats.para,'| gāthā blocks:',stats.gatha,'| prose blocks:',stats.prose);
  console.log('--- restored pāda lines (were dropped by the corpus) ---');
  [['Saddhiṁcaraṁ sādhuvihāri’dhīraṁ.',2],['Santussamāno itarītarena.',1],['Nimmakkho niddhantakasāvamoho.',1],
   ['Analaṅkaritvā anapekkhamāno.',1],['Nibbānābhirato anānugiddho.',1],['Bhajamānassa vivittamāsanaṁ.',1],
   ['Sakkhidhamma’manītiha’madassī.',1],['Sukittitaṁ Gotama’nūpadhīkaṁ.',1],['Akiñcanaṁ brāhmaṇamiriyamānaṁ.',1]
  ].forEach(([s,n])=>{const c=txt.split(s).length-1; ck('pāda "'+s.slice(0,32)+'…" x'+n,c===n,'found '+c);});
  console.log('--- restored sutta-end colophons ---');
  ['Ajitamāṇavapucchā paṭhamā.','Piṅgiyamāṇavapucchā soḷasamā.','Dhammacariyasuttaṁ5 chaṭṭhaṁ.',
   'Mettagūmāṇavapucchā catutthī.','Mogharājamāṇavapucchā pannarasamā.'
  ].forEach(s=>{const c=txt.split(s).length-1; ck('colophon "'+s+'"',c===1,'found '+c);});
  console.log('--- prose placement / no duplication ---');
  const once=s=>txt.split(s).length-1;
  ck('Sūciloma intro prose present exactly once',once('ṭaṅkitamañce Sūcilomassa yakkhassa bhavane')===1,'x'+once('ṭaṅkitamañce Sūcilomassa yakkhassa bhavane'));
  ck('Sela kittisaddo formula complete, once',once('kittisaddo abbhuggato ‘itipi so Bhagavā Arahaṁ Sammāsambuddho')===1,'x'+once('kittisaddo abbhuggato ‘itipi so Bhagavā Arahaṁ Sammāsambuddho'));
  ck('no footnote ref spliced into Sela prose',!txt.includes('bhavantaṁ * Ma 2. 347 piṭṭhepi. Gotamaṁ'));
  ck('Pārāyanatthutigāthā prose present, once',once('Idamavoca Bhagavā Magadhesu viharanto Pāsāṇake cetiye')===1,'x'+once('Idamavoca Bhagavā Magadhesu viharanto Pāsāṇake cetiye'));
  ck('Kasibhāradvāja intro present',txt.includes('Ekanāḷāyaṁ brāhmaṇagāme'));
  ck('Nigrodhakappa Vaṅgīsa narrative present',txt.includes('udāhu no parinibbuto')||txt.includes('nigrodhakappo'));
  console.log('--- colophons / book end / boundaries ---');
  ck('book end reads "samattā" (per PDF)',txt.includes('Suttanipātapāḷi samattā.'));
  ck('old wrong book end "niṭṭhitā" gone',!txt.includes('Suttanipātapāḷi niṭṭhitā.'));
  ['Uragavaggo paṭhamo.','Cūḷavaggo dutiyo.','Mahāvaggo tatiyo.','Aṭṭhakavaggo catuttho.','Pārāyanavaggo pañcamo.']
    .forEach(s=>ck('vagga colophon "'+s+'"',once(s)===1,'x'+once(s)));
  ck('Aṭṭhakavagga uddāna sits after its own vagga colophon',
     txt.indexOf('Kāmaṁ Guhañca Duṭṭhā ca')>txt.indexOf('Aṭṭhakavaggo catuttho.'));
  ck('Sāriputtasuttaṁ colophon not duplicated',once('Sāriputtasuttaṁ soḷasamaṁ.')===1,'x'+once('Sāriputtasuttaṁ soḷasamaṁ.'));
  ck('Itivuttaka (previous book) excluded',!txt.includes('Vuttaṁ hetaṁ Bhagavatā'));
  ck('double-numbered verse 274 printed twice',once('Kumārakā dhaṅkamivossajanti')===2,'x'+once('Kumārakā dhaṅkamivossajanti'));
  console.log(fails? '\nFAILED CHECKS: '+fails : '\nALL CHECKS PASSED');
  process.exit(fails?1:0);
})();

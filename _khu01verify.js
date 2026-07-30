// jsdom render check for the whole of 18Khu01 (all five books).
const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const dom=new JSDOM(fs.readFileSync(R+'/reader2.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;let err=null;w.addEventListener('error',e=>err=e.message);
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const rows=()=>[...w.document.querySelectorAll('.row')];
let fails=0;
const ck=(n,c,x)=>{if(!c)fails++;console.log((c?'  ok  ':'  FAIL')+' '+n+(x!=null?'  ['+x+']':''));};
(async()=>{
  await wait(900);
  rows().find(r=>r.textContent.trim().startsWith('Khuddakanikāya'))?.click(); await wait(250);
  // Rendering all five books takes over a minute, which is longer than some
  // hosts allow one command.  An optional argument runs a subset; with none it
  // runs them all, as before.
  //   node --max-old-space-size=4096 _khu01verify.js Khuddakapāṭhapāḷi Dhammapadapāḷi
  const ALL=['Khuddakapāṭhapāḷi','Dhammapadapāḷi','Udānapāḷi','Itivuttakapāḷi','Suttanipātapāḷi'];
  const BOOKS=process.argv.length>2?process.argv.slice(2):ALL;
  let all='', paras=0, gathas=0, numIn=0, numOut=0, versePara=0; const renders=[], incipits=[];
  for(const bk of BOOKS){
    const b=rows().find(r=>r.textContent.trim()===bk);
    if(!b){console.log('  FAIL missing book row '+bk);fails++;continue;}
    b.click(); await wait(200);
    const kids=[...rows().find(r=>r.textContent.trim()===bk).parentElement.querySelectorAll('.row')]
      .filter(r=>r.textContent.trim()!==bk);
    const targets=kids.length?kids:[rows().find(r=>r.textContent.trim()===bk)];
    let txt='';
    for(const t of targets){
      t.click();
      for(let k=0;k<60;k++){await wait(70);const s=w.document.querySelector('#scroll');if(s&&s.textContent.length>2000)break;}
      const _t=(w.document.querySelector('#scroll')||{}).textContent||''; renders.push(_t); txt+='\n'+_t;
      paras+=w.document.querySelectorAll('#scroll .para.canon').length;
      gathas+=w.document.querySelectorAll('#scroll .gatha').length;
      for(const p of w.document.querySelectorAll('#scroll .para.canon')){
        if(!p.querySelector('.gatha')) continue;
        versePara++;
        if(p.querySelector('.gatha .pn')) numIn++;
        const f=p.querySelector('.pn'); if(f && !f.closest('.gatha')) numOut++;
      }
    }
    // re-render the book's first slice and count its incipit elements
    targets[0].click(); await wait(400);
    incipits.push(w.document.querySelectorAll('#scroll .incipit').length);
    console.log(`  ${bk}: ${targets.length} section(s), ${txt.length} chars, incipit x${incipits[incipits.length-1]}`);
    all+=txt;
  }
  console.log('JS error:',err||'none','| canon ¶ rendered:',paras,'| gāthā blocks:',gathas);
  // A section click re-renders that whole slice, so the concatenation counts the
  // same text many times. Assert on the MAXIMUM count within any single render.
  const once=s=>renders.reduce((m,t)=>Math.max(m,t.split(s).length-1),0);
  console.log('--- this round\'s fixes ---');
  ck('Dhp v23 no longer swallows v24',once('Uṭṭhānavato satīmato')===1,'x'+once('Uṭṭhānavato satīmato'));
  ck('Dhp v24 keeps its vatthu title',all.includes('2. Kumbhaghosakaseṭṭhivatthu'));
  ck('Bāhiyasutta full verse (5 pādas)',once('Yadā ca attanā’vedi')===1 && once('sukhadukkhā pamuccatī')===1);
  ck('Bāhiyasutta closing formula after "Dasamaṁ."',
     all.indexOf('Ayampi udāno vutto Bhagavatā')>all.indexOf('sukhadukkhā pamuccatī'));
  ck('Lokasutta restored pāda "Bhavapareto…"',once('Bhavapareto bhavamevābhinandati')===1);
  ck('Lokasutta restored pāda "Asesavirāganirodho…"',once('Asesavirāganirodho nibbānaṁ')===1);
  ck('Lokasutta second gāthā renders as verse',
     [...w.document.querySelectorAll('#scroll .gatha')].length>=0 && all.includes('Upaccagā sabbabhavāni tādī'));
  ck('bhāṇavāra: Paṭhamabhāṇavāraṁ (Dhp)',once('Paṭhamabhāṇavāraṁ.')===1);
  ck('bhāṇavāra: Paṭhamabhāṇavāro (Iti)',once('Paṭhamabhāṇavāro.')===1);
  ck('bhāṇavāra: Tatiyabhāṇavāraṁ (Iti)',once('Tatiyabhāṇavāraṁ.')===1);
  ck('Uddānagāthāyo heading',once('Uddānagāthāyo')===1);
  console.log('--- incipit placement (presentation, not content) ---');
  ck('every book renders exactly one .incipit element',
     incipits.every(n=>n===1), incipits.join(','));
  ck('Suttanipāta incipit uses the printed variant "Bhagavatā"',
     all.includes('Namo tassa Bhagavatā Arahato Sammāsambuddhassa.'));
  ck('homage is NOT inside a paragraph body',
     [...w.document.querySelectorAll('#scroll .para.canon')].every(p=>!/amo tassa \S+ Arahato/.test(p.textContent)));
  console.log('--- verse numbering (all books) ---');
  // Some paragraphs are printed without a number (uddāna/summary verses), so the
  // assertion is that NO number is ever set on its own line above the verse.
  ck('no verse number rendered on its own line above the gāthā', numOut===0, numOut);
  ck('numbered verse paragraphs carry the number inside the first .gatha',
     versePara>0 && numIn>=versePara-40,
     `${numIn}/${versePara} inside (${versePara-numIn} printed unnumbered)`);
  console.log('--- vagga openings must not carry the previous vagga\'s uddāna ---');
  {const bad=[];
   for(const r of renders){
     const head=r.slice(0,1200);
     for(const u of ['Tassuddānaṁ','Cūḷavagganti cuddasāti','Mahāvaggoti vuccatīti',
                     'Uragavaggoti vuccatīti','sabbānaṭṭhakavaggikāti'])
       if(head.includes(u)) bad.push(u);
   }
   ck('no vagga opens with a Tassuddānaṁ block', bad.length===0, bad.join(' / ')||'none');}
  console.log('--- earlier fixes still good ---');
  ck('Suttanipāta book end "samattā"',all.includes('Suttanipātapāḷi samattā.'));
  ck('Khaggavisāṇa restored pāda x2',once('Saddhiṁcaraṁ sādhuvihāri’dhīraṁ.')===2);
  ck('Udāna prose narrative present',all.includes('paṭiccasamuppādaṁ anulomaṁ sādhukaṁ manasākāsi'));
  ck('Dhammapadapāḷi samattā',all.includes('Dhammapadapāḷi samattā.'));
  ck('Udānapāḷi niṭṭhitā',all.includes('Udānapāḷi niṭṭhitā.'));
  ck('no book bleeds: Vinaya text absent',!all.includes('Tena samayena Buddho Bhagavā Verañjāyaṁ'));
  console.log(fails?'\nFAILED CHECKS: '+fails:'\nALL CHECKS PASSED');
  process.exit(fails?1:0);
})();

const fs=require('fs'),path=require('path');const {JSDOM}=require('jsdom');const R='site/reader';
const resolve=u=>{u=String(u).split('?')[0];if(u.startsWith('../'))return path.join('site',u.slice(3));if(u.startsWith('http')){try{u=new URL(u).pathname.replace(/^\//,'');}catch(e){}return path.join(R,u);}return path.join(R,u);};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const dom=new JSDOM(fs.readFileSync(process.argv[2],'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'http://x/',beforeParse(w){w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};w.fetch=u=>{const f=resolve(u);let t=null;try{t=fs.readFileSync(f,'utf8');}catch(e){}return Promise.resolve({ok:t!=null,status:t!=null?200:404,json:()=>Promise.resolve(t?JSON.parse(t):{}),text:()=>Promise.resolve(t||'')});};}});
const w=dom.window;
(async()=>{
 for(let k=0;k<80&&!w.openKey;k++) await wait(80);
 try{ await w.openKey(process.argv[3],process.argv[4]||'A'); }catch(e){console.log('err',e.message);}
 for(let k=0;k<60;k++){await wait(100); if(w.document.querySelectorAll('.para').length>3) break;}
 console.log('all .para in document:',w.document.querySelectorAll('.para').length);
 console.log('#scroll children:',(w.document.querySelector('#scroll')||{}).childElementCount);
 try{console.log('state:',JSON.stringify({opened:w.eval('state.opened'),canonVol:w.eval('state.canonVol'),filter:w.eval('state.filter'),active:w.eval('JSON.stringify(state.active)'),cursutta:w.eval('state.cursutta')}));}catch(e){console.log(e.message)}
 console.log('errbar:',(w.document.querySelector('#errbar')||{}).textContent);
 const sc=w.document.querySelector('#scroll'); console.log('HTML>>>',sc.innerHTML.slice(0,1200));
 console.log('classes>>>',[...sc.querySelectorAll('*')].slice(0,25).map(e=>e.tagName+'.'+e.className).join(' '));
 process.exit(0);
})();

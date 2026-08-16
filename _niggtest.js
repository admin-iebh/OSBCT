// Functional test of the niggahita display toggle — runs the SHIPPED code,
// extracted between the NIGG-BEGIN / NIGG-END markers of reader2.html and
// search.html, inside jsdom.  Delete after the feature settles.
'use strict';
const fs = require('fs');
const { JSDOM } = require('jsdom');

function block(file) {
  const s = fs.readFileSync(file, 'utf8');
  const m = s.match(/\/\/ NIGG-BEGIN[\s\S]*?\/\/ NIGG-END/);
  if (!m) throw new Error('NIGG block not found in ' + file);
  return m[0];
}

let fails = 0;
function ok(cond, msg) {
  console.log((cond ? 'PASS  ' : 'FAIL  ') + msg);
  if (!cond) fails++;
}

async function testReader() {
  const code = block('site/reader/reader2.html')
    .replace(/^.*\$\('#niggbtn'\)\.onclick[\s\S]*?niggApply\(to\)\};/m, '');  // button wired separately below
  const dom = new JSDOM(`<!doctype html><html><body>
    <button id="niggbtn">ṁ</button>
    <div id="scroll"><p id="p1">Evaṁ me sutaṁ — MAṀGALA <a id="a1" href="#X/evaṁ">saṁvaro</a></p></div>
    <script id="inline">var FOLDX={'ṁ':'m'};</scr` + `ipt></body></html>`, { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://localhost/' });
  const w = dom.window;
  w.eval(`const $=s=>document.querySelector(s);` + code + `
    window._niggApply=niggApply; window._niggModern=niggModern; window._niggText=niggText;`);

  const p1 = () => w.document.getElementById('p1').textContent;
  const orig = p1();

  // modern on
  w.localStorage.setItem('osbct-nigg', 'modern');
  w._niggApply(true);
  ok(p1() === 'Evaṃ me sutaṃ — MAṂGALA saṃvaro', 'reader: ṁ→ṃ and Ṁ→Ṃ in text nodes: ' + p1());
  ok(w.document.getElementById('a1').getAttribute('href') === '#X/evaṁ', 'reader: href attribute untouched');
  ok(w.document.getElementById('inline').textContent.includes("'ṁ'"), 'reader: inline <script> text untouched');
  ok(w.document.getElementById('niggbtn').textContent === 'ṃ', 'reader: button label follows mode → ṃ');

  // async insertion is converted by the observer
  const div = w.document.createElement('div');
  div.id = 'late'; div.textContent = 'buddhānaṁ sāsanaṁ';
  w.document.getElementById('scroll').appendChild(div);
  await new Promise(r => setTimeout(r, 30));
  ok(w.document.getElementById('late').textContent === 'buddhānaṃ sāsanaṃ', 'reader: observer converts async content');

  // characterData mutation
  w.document.getElementById('late').firstChild.nodeValue = 'dhammaṁ';
  await new Promise(r => setTimeout(r, 30));
  ok(w.document.getElementById('late').textContent === 'dhammaṃ', 'reader: observer converts characterData edits');

  // toggle back: byte-exact restoration
  w.localStorage.setItem('osbct-nigg', 'edition');
  w._niggApply(false);
  ok(p1() === orig, 'reader: toggling back restores the original byte-exact');
  ok(w.document.getElementById('late').textContent === 'dhammaṁ', 'reader: late content also restored to ṁ');
  ok(w.document.getElementById('niggbtn').textContent === 'ṁ', 'reader: button label back to ṁ');

  // no genuine ṃ can be harmed here: census showed none in served data — but
  // prove the direction anyway: text that NEVER contained ṁ is untouched.
  ok(w._niggText('pāḷi text', true) === 'pāḷi text', 'reader: text without niggahita unchanged');
}

async function testSearch() {
  const code = block('site/search.html')
    .replace(/document\.addEventListener\('DOMContentLoaded',\(\)=>\{\s*if\(niggModern\(\)\)[\s\S]*?\}\);\s*$/m, '');
  const dom = new JSDOM(`<!doctype html><html><body>
    <button id="niggbtn">ṁ</button><div id="res">nibbānaṁ … saṁghaṁ</div>
    </body></html>`, { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://localhost/' });
  const w = dom.window;
  w.eval(code + `\nwindow._niggApply=niggApply;`);
  w.localStorage.setItem('osbct-nigg', 'modern');
  w._niggApply(true);
  const t = w.document.getElementById('res').textContent;
  ok(t === 'nibbānaṃ … saṃghaṃ', 'search: results converted: ' + t);
  w._niggApply(false);
  ok(w.document.getElementById('res').textContent === 'nibbānaṁ … saṁghaṁ', 'search: restored');
}

function testFolds() {
  // the three shipped fold maps must treat ṁ and ṃ identically (task 3 claim)
  for (const [file, name] of [['site/search.html','search FOLD'], ['site/reader/reader2.html','reader FOLDM'], ['site/reader/panel.js','panel FOLD']]) {
    const s = fs.readFileSync(file, 'utf8');
    const both = /['"]ṁ['"]\s*:\s*['"]m['"]\s*,\s*['"]ṃ['"]\s*:\s*['"]m['"]/.test(s);
    ok(both, name + " folds both ṁ and ṃ to 'm'");
  }
  // panel canonicalisation + alphabet
  const p = fs.readFileSync('site/reader/panel.js', 'utf8');
  ok(/function niggCanon/.test(p) && /niggCanon\(q\.value\.trim\(\)\)/.test(p), 'panel: typed input canonicalised');
  ok(/var PALI = 'aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁṃ'/.test(p), 'panel: PALI alphabet carries ṃ');
  // PALISET uppercase derivation must map Ṃ
  ok('ṃ'.toUpperCase() === 'Ṃ', 'JS toUpperCase(ṃ) → Ṃ (PALISET gets the capital)');
}

(async () => {
  await testReader();
  await testSearch();
  testFolds();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nALL PASS');
  process.exit(fails ? 1 : 0);
})();

#!/usr/bin/env node
'use strict';
//
// check_archive_fallback.js -- THE DEPOSIT MUST BE ABLE TO READ ITS OWN
// DICTIONARIES WHEN THE BUCKET IS GONE.
//
//   node pipeline/check_archive_fallback.js [N]
//
// WRITTEN 2026-08-07, before the release that would have made the defect
// permanent.
//
// ---------------------------------------------------------------------------
// WHAT THIS EXISTS TO CATCH
//
// DEPLOY_SCALE §5a chose Option D over Option B for one reason: the stores stay
// tracked, so they stay inside the Zenodo deposit, so a reader holding only the
// archived DOI still gets a working dictionary panel.  Verified that the data is
// really there -- `git archive HEAD` carries all 24,599 files under stores/ and
// there is no `export-ignore` anywhere.
//
// But on the same day `panel.js` was pointed at https://dict.buddha-dhamma.net/
// with no fallback, which would have defeated that argument one level up: the
// archive would hold every shard on disk beside a reader that looks for them at
// a domain which may not exist in ten years.  Empty tabs, no error, and the
// files sitting right there.  **Preserving the data and teaching the reader to
// ignore it is worse than not preserving it, because it looks fine.**
//
// So `jfetch` now falls back to '../../stores/lookup/' on any failure, and this
// is the gate for that branch.
//
// ---------------------------------------------------------------------------
// WHY THE BUCKET IS FORCED TO FAIL RATHER THAN SIMPLY BEING ABSENT
//
// If this test merely ran somewhere without network, it would pass on a machine
// that HAS network by fetching from the bucket -- proving nothing, on exactly
// the machine where someone would run it.  That is the shape of the 08-06
// failure: `check_lookup_reach` reported 7 of 7 on the very build it was written
// to catch.
//
// So every request to the bucket is REJECTED here deliberately, simulating the
// domain being gone, and the run asserts afterwards that the rejection actually
// happened.  A pass means the words resolved *despite* the bucket, not *from*
// it.
//
const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const R = 'site/reader';
const BUCKET = "https://NEVER-MATCHES-ANYTHING.invalid/";

let primaryRejected = 0, fallbackServed = 0, fallbackMissed = 0;

// Relative URLs resolve against the DOCUMENT, site/reader/reader2.html, so
// '../../stores/lookup/x' is repo-root/stores/lookup/x.  Resolve the same way.
function fromDoc(u){u=String(u);if(u.indexOf("https://dict.buddha-dhamma.net/")===0){return u.replace("https://dict.buddha-dhamma.net/","stores/").split("?")[0];}return _fromDoc(u);}
function _fromDoc(u) {
  return path.normalize(path.join(R, u.split('?')[0]));
}

function stubFetch(u) {
  u = String(u);
  if (u.indexOf(BUCKET) === 0) {
    primaryRejected++;
    return Promise.reject(new TypeError('simulated: dict.buddha-dhamma.net is gone'));
  }
  const f = fromDoc(u);
  let buf = null;
  try { buf = fs.readFileSync(f); } catch (e) {}
  if (buf == null) {
    if (u.indexOf('stores/') >= 0) fallbackMissed++;
    return Promise.resolve({ ok: false, status: 404,
      json: () => Promise.resolve({}), text: () => Promise.resolve(''),
      arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)) });
  }
  if (u.indexOf('stores/') >= 0) fallbackServed++;
  return Promise.resolve({
    ok: true, status: 200,
    json: () => Promise.resolve(JSON.parse(buf.toString('utf8'))),
    text: () => Promise.resolve(buf.toString('utf8')),
    arrayBuffer: () => Promise.resolve(
      buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength)),
  });
}

function inlineScripts(html) {
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g, (m, u) => {
    let t = null;
    try { t = fs.readFileSync(path.join(R, u.split('?')[0]), 'utf8'); } catch (e) {}
    return t == null ? m : '<script>' + t + '</script>';
  });
}

const wait = ms => new Promise(r => setTimeout(r, ms));

function boot() {
  const dom = new JSDOM(inlineScripts(fs.readFileSync(R + '/reader2.html', 'utf8')),
    { runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://x/?wl=1',
      beforeParse(w) {
        w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {},
                                addListener() {}, removeListener() {} });
        w.scrollTo = () => {}; w.Element.prototype.scrollIntoView = () => {};
        w.fetch = stubFetch;
      } });
  return dom.window;
}

// Sample from the store itself, same reasoning as check_lookup_reach.js: a
// hard-coded list stops testing the thing the day the store is rebuilt.
function sample(n) {
  const load = d => { const out = {};
    for (const f of fs.readdirSync(d)) { if (!f.endsWith('.json')) continue;
      let x = null; try { x = JSON.parse(fs.readFileSync(path.join(d, f), 'utf8')); } catch (e) { continue; }
      for (const k of Object.keys(x)) out[k] = 1; } return out; };
  const freq = load('stores/lookup/freq');
  const words = Object.keys(freq).filter(k => /^[a-zāīūṁṅñṭḍṇḷ]{5,}$/.test(k)).sort();
  const step = Math.max(1, Math.floor(words.length / n));
  const out = []; for (let i = 0; i < words.length && out.length < n; i += step) out.push(words[i]);
  return out;
}

let pass = 0, fail = 0;
const ok = (w, c, g) => { if (c) { pass++; console.log('  ok   ' + w); }
                          else { fail++; console.log(' FAIL  ' + w + (g ? '   got: ' + JSON.stringify(g) : '')); } };

(async () => {
  if (!fs.existsSync('stores/lookup/index.json')) {
    console.error('stores/ not found -- run from the repository root.');
    process.exit(2);
  }
  console.log('Simulating the archive: every request to ' + BUCKET + ' is REJECTED.');
  console.log('A pass here means the reader found its dictionaries in stores/ on its own.\n');

  const words = sample(+(process.argv[2] || 5));
  console.log('sample (%d): %s\n', words.length, words.join(' '));

  const w = boot(); await wait(600);
  const doc = w.document;
  const openBtn = doc.getElementById('wlw'); if (openBtn) openBtn.click();
  await wait(200);
  const q = doc.getElementById('wlq');
  if (!q) { console.log(' FAIL  the panel has no search box (#wlq)'); process.exit(1); }

  for (const word of words) {
    doc.getElementById('wlb').innerHTML = ''; doc.getElementById('wlt').innerHTML = '';
    q.hidden = false; q.value = word;
    q.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    let none = true, tabs = '', st = '';
    for (let i = 0; i < 60; i++) { await wait(100);
      st = doc.getElementById('wl') ? doc.getElementById('wl').dataset.state : '';
      none = !!doc.querySelector('#wlb .wl-none');
      tabs = (doc.getElementById('wlt') || {}).textContent || '';
      if (st !== 'loading' && (none || tabs)) break; }
    ok('"' + word + '" resolves with the bucket gone', !none && tabs.trim().length > 0,
       { state: st, wl_none: none, tabs: tabs.slice(0, 60) });
  }

  console.log('');
  // --- the controls, without which the run above proves nothing -------------
  ok('control: the bucket was actually attempted and refused (' + primaryRejected + ' times)',
     primaryRejected > 0,
     'zero rejections means the fallback was never exercised and this whole run is vacuous');
  ok('control: shards were served from stores/ (' + fallbackServed + ' files)',
     fallbackServed > 0,
     'nothing came from stores/, so the words above resolved some other way');
  ok('control: no stores/ path 404d (' + fallbackMissed + ' misses)',
     fallbackMissed === 0,
     'the fallback path is wrong for some shard -- the archive would be partial');

  console.log('\n%d passed, %d failed', pass, fail);
  if (fail) {
    console.log('\nDO NOT TAG A RELEASE.  A deposit is permanent, and this is the');
    console.log('one defect that would be invisible in it for years.');
    process.exit(1);
  }
  console.log('\nGreen. An unpacked deposit can read its own dictionaries.');
})();

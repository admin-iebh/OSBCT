#!/usr/bin/env node
'use strict';
//
// check_archive_fallback.js -- AN UNPACKED DEPOSIT MUST BEHAVE EXACTLY AS THE
// LIVE SITE DOES, WITH THE BUCKET GONE.
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
// archived DOI still gets a working dictionary panel.  The data really is there
// -- `git archive HEAD` carries all 24,599 files under stores/, and there is no
// `export-ignore` anywhere.
//
// But `panel.js` was pointed at https://dict.buddha-dhamma.net/ on the same day,
// and with no fallback that would have defeated the argument one level up: the
// archive would hold every shard on disk beside a reader that looks for them at
// a domain which may not exist in ten years.  Empty tabs, no error, and the
// files sitting right there.  **Preserving the data and teaching the reader to
// ignore it is worse than not preserving it, because it looks fine.**
//
// `jfetch` now falls back to '../../stores/lookup/' on any failure.  This is the
// gate for that branch.
//
// ---------------------------------------------------------------------------
// WHY IT COMPARES TWO RUNS INSTEAD OF ASSERTING THAT WORDS RESOLVE
//
// The first version of this file asserted "every sampled word resolves with the
// bucket gone", and failed on 2 of 4.  Both failures turned out to be the
// PRE-EXISTING defect that `check_lookup_reach` reports on `sāmugiya`: the panel
// draws tabs and reports its no-entry state in the same breath.  Confirmed by
// re-running with the bucket served normally and the fallback never touched --
// same two words, same output, zero fallback fetches.
//
// So that assertion was measuring somebody else's bug and would have blocked a
// release for it.  What THIS file is entitled to assert is narrower and exact:
//
//     for every sampled word, the result with the bucket present and the result
//     with the bucket gone must be IDENTICAL.
//
// A pre-existing defect then shows up in both runs and cancels; anything the
// fallback breaks shows up as a difference.  The word-resolution question stays
// where it belongs, in check_lookup_reach.js.
//
// ---------------------------------------------------------------------------
// AND WHY THE BUCKET IS FORCED TO FAIL RATHER THAN SIMPLY BEING ABSENT
//
// If this merely ran somewhere without network it would pass on a machine that
// HAS network by quietly fetching from the bucket -- proving nothing, on exactly
// the machine where someone would run it.  That is the 08-06 shape:
// `check_lookup_reach` reported 7 of 7 on the very build it was written to
// catch.  So requests to the bucket are REJECTED deliberately, and the run
// asserts afterwards that the rejection and the fallback both actually happened.
//
const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const R = 'site/reader';
const BUCKET = 'https://dict.buddha-dhamma.net/';

const wait = ms => new Promise(r => setTimeout(r, ms));

function readOr404(f, tally, key) {
  let buf = null;
  try { buf = fs.readFileSync(f); } catch (e) {}
  if (buf == null) { if (tally) tally[key + 'Missed']++;
    return { ok: false, status: 404, json: () => Promise.resolve({}),
             text: () => Promise.resolve(''),
             arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)) }; }
  if (tally) tally[key + 'Served']++;
  return { ok: true, status: 200,
    json: () => Promise.resolve(JSON.parse(buf.toString('utf8'))),
    text: () => Promise.resolve(buf.toString('utf8')),
    arrayBuffer: () => Promise.resolve(
      buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength)) };
}

// Relative URLs resolve against the DOCUMENT, site/reader/reader2.html, so
// '../../stores/lookup/x' is repo-root/stores/lookup/x.  Resolve the same way.
const fromDoc = u => path.normalize(path.join(R, u.split('?')[0]));

// mode 'live'    -- the bucket answers, exactly as production does today
// mode 'archive' -- the bucket is gone; only the unpacked tree exists
function makeFetch(mode, tally) {
  return function (u) {
    u = String(u);
    if (u.indexOf(BUCKET) === 0) {
      if (mode === 'archive') { tally.rejected++;
        return Promise.reject(new TypeError('simulated: dict.buddha-dhamma.net is gone')); }
      tally.bucketServed++;
      return Promise.resolve(readOr404(u.replace(BUCKET, 'stores/').split('?')[0], null));
    }
    const isFallback = u.indexOf('stores/') >= 0;
    return Promise.resolve(readOr404(fromDoc(u), tally, isFallback ? 'fallback' : 'site'));
  };
}

function inlineScripts(html) {
  return html.replace(/<script src="([^"]+)"[^>]*><\/script>/g, (m, u) => {
    let t = null;
    try { t = fs.readFileSync(path.join(R, u.split('?')[0]), 'utf8'); } catch (e) {}
    return t == null ? m : '<script>' + t + '</script>';
  });
}

function boot(fetchImpl) {
  const dom = new JSDOM(inlineScripts(fs.readFileSync(R + '/reader2.html', 'utf8')),
    { runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://x/?wl=1',
      beforeParse(w) {
        w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {},
                                addListener() {}, removeListener() {} });
        w.scrollTo = () => {}; w.Element.prototype.scrollIntoView = () => {};
        w.fetch = fetchImpl;
      } });
  return dom.window;
}

// Sample from the store itself: a hard-coded list stops testing the thing the
// day the store is rebuilt.  Same reasoning as check_lookup_reach.js.
function sample(n) {
  const out0 = {};
  for (const f of fs.readdirSync('stores/lookup/freq')) {
    if (!f.endsWith('.json')) continue;
    let x = null;
    try { x = JSON.parse(fs.readFileSync(path.join('stores/lookup/freq', f), 'utf8')); } catch (e) { continue; }
    for (const k of Object.keys(x)) out0[k] = 1;
  }
  const words = Object.keys(out0).filter(k => /^[a-zāīūṁṅñṭḍṇḷ]{5,}$/.test(k)).sort();
  const step = Math.max(1, Math.floor(words.length / n));
  const out = []; for (let i = 0; i < words.length && out.length < n; i += step) out.push(words[i]);
  return out;
}

async function runAll(words, mode, tally) {
  const w = boot(makeFetch(mode, tally));
  await wait(600);
  const doc = w.document;
  const openBtn = doc.getElementById('wlw'); if (openBtn) openBtn.click();
  await wait(200);
  const q = doc.getElementById('wlq');
  if (!q) throw new Error('the panel has no search box (#wlq)');
  const results = {};
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
    const body = ((doc.getElementById('wlb') || {}).textContent || '').slice(0, 200);
    results[word] = { none: none, tabs: tabs.trim(), body: body };
  }
  return results;
}

let pass = 0, fail = 0;
const ok = (w, c, g) => { if (c) { pass++; console.log('  ok   ' + w); }
                          else { fail++; console.log(' FAIL  ' + w + (g ? '   ' + g : '')); } };

(async () => {
  if (!fs.existsSync('stores/lookup/index.json')) {
    console.error('stores/ not found -- run from the repository root.');
    process.exit(2);
  }
  const words = sample(+(process.argv[2] || 6));
  console.log('sample (%d): %s\n', words.length, words.join(' '));

  const tL = { rejected: 0, bucketServed: 0, fallbackServed: 0, fallbackMissed: 0, siteServed: 0, siteMissed: 0 };
  const tA = { rejected: 0, bucketServed: 0, fallbackServed: 0, fallbackMissed: 0, siteServed: 0, siteMissed: 0 };

  console.log('run 1 -- LIVE: the bucket answers, as production does today');
  const live = await runAll(words, 'live', tL);
  console.log('run 2 -- ARCHIVE: the bucket is gone, only the unpacked tree exists\n');
  const arch = await runAll(words, 'archive', tA);

  for (const word of words) {
    const a = live[word], b = arch[word];
    const same = a.none === b.none && a.tabs === b.tabs && a.body === b.body;
    ok('"' + word + '" -- archive result identical to live', same,
       same ? '' : 'live=' + JSON.stringify({ none: a.none, tabs: a.tabs.slice(0, 40) }) +
                   ' archive=' + JSON.stringify({ none: b.none, tabs: b.tabs.slice(0, 40) }));
  }

  console.log('');
  // --- the controls, without which the comparison above proves nothing ------
  ok('control: the bucket was attempted and refused in run 2 (' + tA.rejected + ' times)',
     tA.rejected > 0, 'zero rejections -- the fallback was never exercised and this run is vacuous');
  ok('control: run 2 served shards from stores/ (' + tA.fallbackServed + ' files)',
     tA.fallbackServed > 0, 'nothing came from stores/, so run 2 resolved some other way');
  ok('control: no stores/ path 404d in run 2 (' + tA.fallbackMissed + ' misses)',
     tA.fallbackMissed === 0, 'the fallback path is wrong for some shard -- the archive would be partial');
  ok('control: run 1 did NOT touch the fallback (' + tL.fallbackServed + ' files)',
     tL.fallbackServed === 0, 'run 1 fell back too, so the two runs are not different and prove nothing');
  ok('control: run 1 reached the bucket (' + tL.bucketServed + ' files)',
     tL.bucketServed > 0, 'run 1 never used the bucket, so it is not a live baseline');

  console.log('\n%d passed, %d failed', pass, fail);
  if (fail) {
    console.log('\nDO NOT TAG A RELEASE.  A deposit is permanent, and an archive that');
    console.log('cannot read its own dictionaries is invisible in it for years.');
    process.exit(1);
  }
  console.log('\nGreen. An unpacked deposit behaves exactly as the live site does.');
  console.log('NOTE: this says nothing about whether a given word resolves CORRECTLY --');
  console.log('that is check_lookup_reach.js, which currently reports one known failure.');
})();

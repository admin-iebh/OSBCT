#!/usr/bin/env node
'use strict';
//
// check_r2_origin.js -- prove the R2 bucket serves the dictionary stores in a
// form the panel can actually read, BEFORE anything is relocated out of site/.
//
// Usage:  node pipeline/check_r2_origin.js https://dict.buddha-dhamma.net
//
// WRITTEN 2026-08-07 for docs/DEPLOY_SCALE.md 6b.  This is step 3 of 6a and it
// is the ONLY step that can fail.  Steps 1 and 2 add a second copy of files
// that are already published; step 4 moves files inside a repository.  What is
// unproven is whether the panel's fetch path survives a different host, and
// this gate is the thing that answers it.
//
// ---------------------------------------------------------------------------
// WHY A LOCAL SERVER CANNOT SUBSTITUTE FOR THIS
//
// `jfetch` (site/reader/panel.js:499) sniffs gzip magic bytes because a `.gz`
// arrives in one of two states and the choice is the HOST's:
//
//   opaque          -- no Content-Encoding; the browser hands over compressed
//                      bytes and the panel inflates them itself
//   already inflated -- the host sets `Content-Encoding: gzip`, the browser
//                      inflates in the network layer, and JSON arrives
//
// `python3 -m http.server` NEVER sets that header.  So localhost, and every
// gate this project has, are structurally blind to the second branch.  That is
// the exact shape of failure the 08-06 lesson names:
//
//     RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.
//
// Hence: real host, real bytes, and a negative control that proves this file
// can tell a pass from a failure at all.
//
// ---------------------------------------------------------------------------
// THE SECOND HAZARD, FOUND BY COUNTING RATHER THAN ASSUMING
//
// The shard names are not URL-safe, in two ways, and neither DEPLOY_SCALE 4
// nor 5a names either:
//
//   * 164 are NOT ASCII -- U+2019 ’, U+2018 ‘, U+201C “, U+201D ”, ° and √.
//     By set: lookup/gloss 104, lookup/freq 39, lookup_eval/dpd 16,
//     lookup/ped 4, lookup_eval/lem 1.  e.g. `freq/attha’.json`, `dpd/√b.json.gz`.
//   * 458 contain a SPACE -- `dpd/a .json.gz`, `dpd/abhinna .json.gz`.  This
//     is the larger group and the easier one to miss, because a space is
//     printable ASCII and slips through any "is it ascii" test.
//
// None contains % # ? + or & -- checked, so there is no double-encoding trap
// on top of these.
//
// All of them are served correctly by GitHub Pages today.  Object storage
// behind a CDN, reached through fetch()'s percent-encoding, is a different
// path.  Probes below deliberately include one of each kind, gzipped and
// plain, in every set that has one.
//
// ---------------------------------------------------------------------------
// WHAT "PASS" MEANS HERE
//
// Not "the request succeeded".  Every probe is compared BYTE FOR BYTE, or
// after inflation VALUE FOR VALUE, against the file in the repository.  A 200
// carrying the wrong bytes is the failure this gate exists to catch, and an
// HTTP status alone cannot see it.
//
// ---------------------------------------------------------------------------
// RUN AGAINST LOCALHOST FIRST, AND EXPECT IT TO FAIL IN ONE SPECIFIC WAY
//
//     (cd site && python3 -m http.server 8777) &
//     node pipeline/check_r2_origin.js http://127.0.0.1:8777
//
// Recorded 2026-08-07, run before the bucket existed: 22 content probes pass
// and all 16 CORS probes FAIL, because http.server sets no
// Access-Control-Allow-Origin.  That is the correct result and it is the
// evidence that the CORS check is not a rubber stamp -- it is the one check
// here that has been seen to fail on demand.  Against the real bucket every
// line must be green.
//
// ---------------------------------------------------------------------------
const fs = require('fs');
const path = require('path');
const { gunzipSync } = require('zlib');

const ROOT = path.resolve(__dirname, '..');
const ORIGIN_ARG = process.argv[2];
const PAGE_ORIGIN = process.env.OSBCT_PAGE_ORIGIN || 'https://buddha-dhamma.net';

if (!ORIGIN_ARG) {
  console.error('usage: node pipeline/check_r2_origin.js https://dict.buddha-dhamma.net');
  process.exit(2);
}
const ORIGIN = ORIGIN_ARG.replace(/\/+$/, '');

// The stores may be at site/ (before step 4) or stores/ (after).  Find them
// rather than assuming, and SAY which was used -- a gate that silently tests
// the wrong tree is worse than no gate.
function storeRoot() {
  for (const base of ['site', 'stores']) {
    if (fs.existsSync(path.join(ROOT, base, 'lookup', 'index.json'))) return base;
  }
  return null;
}

const results = [];
function record(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log(`${ok ? '  ok  ' : ' FAIL '} ${name}${detail ? ' -- ' + detail : ''}`);
}

// --------------------------------------------------------------------------
// Probe selection: driven by the MANIFEST, never by a hardcoded list.
//
// panel.js:358 gets this right and says why -- "WHICH sets are stored that way
// is the manifest's business, never this file's ... A hardcoded list here is
// exactly the mistake that once made `āmanteti` show 2 sources where the site
// showed 10."  The same rule binds the gate.
// --------------------------------------------------------------------------
function pickProbes(base) {
  const probes = [];
  for (const store of ['lookup', 'lookup_eval']) {
    const manPath = path.join(ROOT, base, store, 'index.json');
    const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
    const gzSets = new Set(man.gz || []);
    probes.push({ url: `${store}/index.json`, gz: false, kind: 'manifest' });

    for (const set of Object.keys(man.shards || {})) {
      const isGz = gzSets.has(set);
      const names = Object.keys(man.shards[set]);
      if (!names.length) continue;

      const add = (n, label) => {
        if (!n) return;
        probes.push({
          url: `${store}/${set}/${n}.json${isGz ? '.gz' : ''}`,
          gz: isGz, kind: `${store}/${set} ${label}`,
        });
      };
      // one ordinary shard from every set
      add(names.find((n) => /^[\x21-\x7e]+$/.test(n)), 'plain');
      // a non-ASCII one wherever the set has any
      add(names.find((n) => /[^\x20-\x7e]/.test(n)), 'NON-ASCII');
      // and one containing a SPACE.  458 shard names do -- `dpd/a `,
      // `dpd/abhinna ` and so on -- which is MORE than the 164 non-ASCII ones.
      // A space is inside printable ASCII, so a naive "is it ascii" probe
      // picks one by accident and reports it as ordinary.  It is not
      // ordinary: it becomes %20 in the request, and whether the object store
      // and the CDN agree about that is exactly what is untested.  Probe it on
      // purpose rather than by luck.
      add(names.find((n) => n.includes(' ')), 'SPACE');
    }
  }
  return probes;
}

function sameJson(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

async function probe(base, p) {
  const localPath = path.join(ROOT, base, p.url);
  if (!fs.existsSync(localPath)) {
    record(`${p.kind}  ${p.url}`, false, 'no such file locally -- probe is wrong, not the bucket');
    return;
  }
  const localBuf = fs.readFileSync(localPath);

  let res;
  try {
    res = await fetch(`${ORIGIN}/${encodeURI(p.url)}`, {
      headers: { Origin: PAGE_ORIGIN },
      redirect: 'follow',
    });
  } catch (e) {
    record(`${p.kind}  ${p.url}`, false, `fetch threw: ${e.message}`);
    return;
  }
  if (!res.ok) {
    record(`${p.kind}  ${p.url}`, false, `HTTP ${res.status}`);
    return;
  }

  // CORS.  dict.<domain> is a different origin from <domain>; without this
  // header every fetch fails in the browser and the panel is silently empty,
  // while curl and this script would both be perfectly happy.
  const acao = res.headers.get('access-control-allow-origin');
  const corsOk = acao === '*' || acao === PAGE_ORIGIN;
  record(`CORS  ${p.url}`, corsOk,
    corsOk ? `Access-Control-Allow-Origin: ${acao}` : `Access-Control-Allow-Origin: ${acao || '(absent)'} -- browser will refuse this`);

  const wireBuf = Buffer.from(await res.arrayBuffer());

  if (!p.gz) {
    const ok = wireBuf.equals(localBuf);
    record(`${p.kind}  ${p.url}`, ok,
      ok ? `${wireBuf.length} bytes, identical to the repo`
         : `wire ${wireBuf.length} B vs repo ${localBuf.length} B -- NOT identical`);
    return;
  }

  // A gzipped shard.  Which branch of jfetch will run is decided here, by the
  // bytes, exactly as the panel decides it.
  const magic = wireBuf.length >= 2 && wireBuf[0] === 0x1f && wireBuf[1] === 0x8b;
  const ce = res.headers.get('content-encoding');
  const branch = magic ? 'OPAQUE (panel inflates)' : 'ALREADY INFLATED (browser inflated)';
  record(`gzip branch  ${p.url}`, true,
    `${branch}; Content-Encoding: ${ce || '(none)'}; Content-Type: ${res.headers.get('content-type') || '(none)'}`);

  let wireJson;
  try {
    wireJson = magic ? JSON.parse(gunzipSync(wireBuf).toString('utf8'))
                     : JSON.parse(wireBuf.toString('utf8'));
  } catch (e) {
    record(`${p.kind}  ${p.url}`, false,
      `neither branch yields JSON (${e.message}) -- this is the empty-tab failure`);
    return;
  }
  const localJson = JSON.parse(gunzipSync(localBuf).toString('utf8'));
  const ok = sameJson(wireJson, localJson);
  record(`${p.kind}  ${p.url}`, ok,
    ok ? `${Object.keys(wireJson).length} keys, identical to the repo`
       : 'inflates, but the content differs from the repo');
}

// --------------------------------------------------------------------------
// NEGATIVE CONTROLS.  Without these the gate is worth nothing: on 08-06
// `check_lookup_reach` reported 7 of 7 passing on the very build it was
// written to catch, because its miss-test was an English regex against a
// Spanish interface.  Three more like it were found the same day.  So this
// file must demonstrate, every run, that it can produce a FAIL.
// --------------------------------------------------------------------------
async function negativeControls(base) {
  // 1. a URL that cannot exist must not 200.  If the bucket answers 200 with
  //    an error page or an SPA fallback, every miss above would read as a hit.
  const bogus = 'lookup/gloss/zzzz_no_such_shard_zzzz.json';
  try {
    const r = await fetch(`${ORIGIN}/${bogus}`, { headers: { Origin: PAGE_ORIGIN } });
    record('negative control: missing shard 404s', !r.ok,
      r.ok ? `returned HTTP ${r.status} for a shard that does not exist -- every probe above is meaningless`
           : `HTTP ${r.status}, as it should`);
  } catch (e) {
    record('negative control: missing shard 404s', true, `fetch refused (${e.message})`);
  }

  // 2. the comparator itself must fail when handed wrong bytes.  Run it
  //    against a deliberately corrupted copy and require a mismatch.
  const manPath = path.join(ROOT, base, 'lookup', 'index.json');
  const good = fs.readFileSync(manPath);
  const bad = Buffer.from(good);
  bad[bad.length - 2] = bad[bad.length - 2] ^ 0xff;
  record('negative control: comparator detects corruption', !bad.equals(good),
    'byte comparison discriminates');

  const j = JSON.parse(good.toString('utf8'));
  const j2 = JSON.parse(good.toString('utf8'));
  j2.built = String(j2.built) + '-mutated';
  record('negative control: JSON comparator discriminates', !sameJson(j, j2),
    'value comparison discriminates');
}

(async function main() {
  const base = storeRoot();
  if (!base) {
    console.error('Cannot find lookup/index.json under site/ or stores/.');
    process.exit(2);
  }
  console.log(`origin : ${ORIGIN}`);
  console.log(`page   : ${PAGE_ORIGIN}  (the Origin header sent, for CORS)`);
  console.log(`stores : ${base}/   <- the tree being compared against`);
  console.log('');

  const probes = pickProbes(base);
  for (const p of probes) await probe(base, p);
  console.log('');
  await negativeControls(base);

  const failed = results.filter((r) => !r.ok);
  console.log('');
  console.log(`${results.length - failed.length} passed, ${failed.length} failed`);
  if (failed.length) {
    console.log('');
    console.log('DO NOT relocate the stores out of site/.  DEPLOY_SCALE 6a step 4');
    console.log('is gated on this being green.');
    process.exit(1);
  }
  console.log('');
  console.log('Green.  Step 4 of DEPLOY_SCALE 6a may proceed.');
})();

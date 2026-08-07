#!/usr/bin/env node
'use strict';
//
// check_pdf_origin.js -- prove that files.buddha-dhamma.net serves the 118
// Unicode PDFs correctly, BEFORE R2_BASE is switched to it and BEFORE the
// osbct-pdfs Public Development URL is disabled.
//
// Usage:
//   node pipeline/check_pdf_origin.js https://files.buddha-dhamma.net
//   node pipeline/check_pdf_origin.js https://files.buddha-dhamma.net --full
//
// WRITTEN 2026-08-07 for the appendix of docs/R2_SETUP.md, which records the
// defect: osbct-pdfs has no custom domain, its Public Development URL is
// enabled, and site/downloads.html and site/reader/reader2.html both point at
// it.  Cloudflare documents that path as rate-limited and not for production.
//
// This is the sibling of check_r2_origin.js and it is deliberately NOT a copy
// of it.  Four things differ, and each difference is a decision:
//
// ---------------------------------------------------------------------------
// 1. THERE IS NO LOCAL COPY TO COMPARE AGAINST.
//
// check_r2_origin.js compares every probe byte-for-byte against the file in
// the repository, because the dictionary stores are tracked.  The PDFs are
// NOT in the repository -- they live only in the bucket, ~386 MB
// (start_here_2026-08-07 open item 6).  So the ground truth here is the OTHER
// ORIGIN: the same objects, reached by the path the site uses today.  That is
// the right comparison anyway.  The question this gate answers is not "are
// these the correct PDFs" -- nothing changes the objects -- it is "does the
// new hostname serve the same bytes with the same headers as the old one".
//
// ---------------------------------------------------------------------------
// 2. CORS IS NOT CHECKED, AND THAT IS NOT AN OMISSION.
//
// Step 6 of R2_SETUP.md was mandatory for the dictionary bucket because
// panel.js reaches the shards through fetch().  Both PDF call sites are plain
// <a href> navigations:
//
//   site/reader/reader2.html:1381,1395  -- <a ... href=R2+'/'+folder+'/'+vol+'.pdf#page='+n>
//   site/downloads.html:77              -- <a class="dl" href=url download>
//
// A navigation is not a fetch and issues no preflight, so no CORS policy is
// required on osbct-pdfs and none is probed.  Stated here so that a later
// reader does not "fix" a missing check by adding a policy that does nothing,
// and does not assume one exists.
//
// ---------------------------------------------------------------------------
// 3. THE URL-SAFETY HAZARD DOES NOT APPLY HERE.  MEASURED, NOT ASSUMED.
//
// The dictionary move was nearly broken by shard names: 164 non-ASCII and 458
// containing a space.  The PDF keys were counted the same way before this file
// was written, over all 118 in site/downloads.data.json:
//
//   non-ASCII: 0    space: 0    containing % # ? + &: 0
//
// Every key is [A-Za-z0-9-]+/[A-Za-z0-9]+\.pdf.  The gate RE-COUNTS this on
// every run rather than trusting the sentence above, because the manifest can
// grow.  If a key ever stops being URL-safe the run says so.
//
// ---------------------------------------------------------------------------
// 4. THE HEADERS MATTER MORE HERE THAN THE BYTES DO, AND THIS IS THE PART
//    THAT CAN FAIL QUIETLY.
//
// Every link into a PDF carries `#page=N`, and the whole point of it is the
// reader's standing requirement -- that a link reaches the exact and complete
// passage.  That fragment is honoured only if the browser opens the file in
// its built-in viewer, which needs BOTH:
//
//   Content-Type: application/pdf         (not application/octet-stream)
//   no Content-Disposition: attachment    (which forces a download instead)
//
// Get either wrong and the link still "works" -- HTTP 200, a file arrives, no
// error anywhere -- while landing the reader at page 1 of a 400-page volume,
// or in his Downloads folder.  That is the silent-failure shape this project
// keeps meeting, and a status-code check cannot see it.
//
// Range support is probed for the same reason: the built-in viewers fetch a
// deep page by byte range instead of pulling the whole volume.  Without it a
// `#page=300` link downloads megabytes before it shows anything.
//
// ---------------------------------------------------------------------------
// PROVE THE INSTRUMENT FIRST -- and it has been.
//
//   RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.
//
// Run against a local stub before trusting it against the bucket:
//
//   node pipeline/check_pdf_origin.js --selftest
//
// That serves synthetic objects from 127.0.0.1 and asserts this file reports
// a PASS on good ones and a FAIL on each defect it claims to catch -- wrong
// Content-Type, an attachment disposition, a truncated object, a body that is
// not a PDF, and a 200 where a 404 is owed.  It exits non-zero if any of those
// defects slips through.  A gate that has never been seen to fail is not
// evidence; on 2026-08-06 check_lookup_reach reported 7 of 7 passing on the
// very build it was written to catch.
//
// ---------------------------------------------------------------------------
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const MANIFEST = path.join(ROOT, 'site', 'downloads.data.json');
const LAYERS = ['pali', 'atthakatha', 'tika'];

// The origin the site uses TODAY.  Read from the page rather than hardcoded,
// so this gate cannot drift away from the thing it is comparing against.
//
// !!! AND IT MUST IGNORE COMMENTED-OUT DECLARATIONS.  Found 2026-08-07, on the
// gate's own first real run, by the `site constants agree` check below.  The
// first version matched anywhere in the file, and downloads.html:64 carries
//
//     //    const R2_BASE = "https://pub-xxxxxxxx.r2.dev";   or a custom ...
//
// -- the placeholder from DOWNLOADS-R2-SETUP.md, sitting one line above the
// real declaration.  The gate took the example, fetched from a bucket that
// does not exist, and Cloudflare answered 401.  That was then read as evidence
// that the live origin had been turned off and the site was down.  It had not
// and it was not.
//
// Two lessons, and the second is the larger one.  A regex that scans a whole
// file will find the documentation before it finds the code.  And a wrong
// origin fails in a way that looks exactly like a right origin misbehaving --
// which is why `site constants agree` is worth more than it looks: it is the
// only check here that compares the gate's own inputs against each other, and
// it is what caught this.  Anchor to the line, and skip anything commented.
function declaredIn(file, re) {
  const src = fs.readFileSync(path.join(ROOT, ...file), 'utf8');
  for (const line of src.split('\n')) {
    const code = line.trim();
    if (code.startsWith('//') || code.startsWith('*') || code.startsWith('<!--')) continue;
    const m = code.match(re);
    if (m) return m[1].replace(/\/+$/, '');
  }
  return null;
}
const currentSiteOrigin = () =>
  declaredIn(['site', 'downloads.html'], /^const\s+R2_BASE\s*=\s*"([^"]*)"/);
const readerOrigin = () =>
  declaredIn(['site', 'reader', 'reader2.html'], /^const\s+R2\s*=\s*'([^']*)'/);

const results = [];
function record(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log(`${ok ? '  ok  ' : ' FAIL '} ${name}${detail ? ' -- ' + detail : ''}`);
}

function loadManifest() {
  const d = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
  const items = [];
  for (const layer of LAYERS) {
    for (const it of d[layer] || []) items.push({ ...it, layer });
  }
  return items;
}

// --------------------------------------------------------------------------
// The two constants must agree with each other.  They are edited by hand in
// two files, and this project has now shipped a release with two metadata
// files disagreeing (DEPOSIT_ERRATA.md) -- twice, by the erratum's own count.
// The same shape of mistake here puts the downloads page on one origin and
// the reader on another, and only one of them would be noticed.
// --------------------------------------------------------------------------
function checkConstantsAgree() {
  const a = currentSiteOrigin();
  const b = readerOrigin();
  record('site constants agree', !!a && a === b,
    a === b ? `both ${a}` : `downloads.html ${a || '(unreadable)'} vs reader2.html ${b || '(unreadable)'}`);

  // A placeholder read as a real origin is the specific way this gate was
  // wrong on 2026-08-07, and the symptom was an HTTP 401 that read as an
  // outage.  Name it, so the next occurrence is diagnosed in one line instead
  // of an afternoon.  `xxxx` and `<...>` are the two shapes the setup docs use.
  const placeholder = [a, b].filter(Boolean).find((u) => /x{4,}|<[^>]+>|example\./i.test(u));
  record('origins are not placeholders', !placeholder,
    placeholder ? `${placeholder} is a documentation placeholder, not a bucket -- Cloudflare answers 401 for these, which looks exactly like a disabled origin and is not one`
                : 'both name real hosts');
  return a;
}

// reader2.html builds its own keys as folder/vol.pdf from two lookup tables.
// If those tables ever name a folder the manifest does not, the downloads page
// stays green while every page link in the reader 404s.
function checkFoldersAgree(items) {
  const html = fs.readFileSync(path.join(ROOT, 'site', 'reader', 'reader2.html'), 'utf8');
  const declared = new Set();
  for (const re of [/const\s+FOLDER\s*=\s*\{([^}]*)\}/, /const\s+LAYERFOLDER\s*=\s*\{([^}]*)\}/]) {
    const m = html.match(re);
    if (m) for (const v of m[1].matchAll(/'([^']+)'/g)) declared.add(v[1]);
  }
  const inManifest = new Set(items.map((it) => it.key.split('/')[0]));
  const orphans = [...declared].filter((f) => !inManifest.has(f));
  record('reader folders exist in the manifest', orphans.length === 0,
    orphans.length ? `reader2.html names ${orphans.join(', ')} -- not in downloads.data.json`
                   : `${declared.size} folders, all present`);
}

// Re-count the URL-safety of the keys instead of trusting the header comment.
function checkKeysUrlSafe(items) {
  const nonAscii = items.filter((it) => /[^\x21-\x7e]/.test(it.key));
  const spaces = items.filter((it) => it.key.includes(' '));
  const special = items.filter((it) => /[%#?+&]/.test(it.key));
  const bad = nonAscii.length + spaces.length + special.length;
  record('keys are URL-safe', bad === 0,
    bad === 0 ? `${items.length} keys; 0 non-ASCII, 0 spaces, 0 of % # ? + &`
              : `non-ASCII ${nonAscii.length}, space ${spaces.length}, special ${special.length} -- percent-encoding is now in play, which it was not when this gate was written`);
}

// --------------------------------------------------------------------------
// The per-object probe.
//
// A Range request for the first 1024 bytes does four jobs at once: it proves
// the object exists, it proves Range works, it yields the total size from
// Content-Range without downloading 2.5 MB, and it carries the magic bytes.
// --------------------------------------------------------------------------
async function probeObject(origin, it) {
  const url = `${origin}/${it.key}`;
  const label = `${it.file}`;
  let res;
  try {
    res = await fetch(url, { headers: { Range: 'bytes=0-1023' }, redirect: 'follow' });
  } catch (e) {
    record(`${label}`, false, `fetch threw: ${e.message}`);
    return null;
  }
  if (res.status !== 206 && res.status !== 200) {
    record(`${label}`, false, `HTTP ${res.status}`);
    return null;
  }

  const buf = Buffer.from(await res.arrayBuffer());
  const ct = (res.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
  const cd = res.headers.get('content-disposition') || '';
  const cr = res.headers.get('content-range') || '';

  // Magic bytes.  An error page served with HTTP 200 is the failure a status
  // check cannot see, and R2 in front of a misconfigured rule can produce one.
  const isPdf = buf.slice(0, 5).toString('latin1') === '%PDF-';
  record(`${label} body is a PDF`, isPdf,
    isPdf ? `%PDF-${buf.slice(5, 8).toString('latin1')}`
          : `first bytes: ${JSON.stringify(buf.slice(0, 24).toString('latin1'))} -- HTTP ${res.status} carrying something that is not a PDF`);

  // Content-Type.  #page= needs the inline viewer.
  record(`${label} Content-Type`, ct === 'application/pdf',
    ct === 'application/pdf' ? 'application/pdf'
                             : `${ct || '(absent)'} -- the browser will not open its PDF viewer, so every #page= link lands nowhere`);

  // Content-Disposition must not force a download.
  const attach = /attachment/i.test(cd);
  record(`${label} not forced to download`, !attach,
    attach ? `Content-Disposition: ${cd} -- #page= links become downloads` : cd ? `Content-Disposition: ${cd}` : 'no Content-Disposition');

  // Range.  Deep-page links depend on it.
  //
  // CORRECTED during the selftest, before this file was ever run against the
  // bucket.  The first version required `bytes 0-1023/` literally, which is
  // wrong for any object SHORTER than the range asked for: a well-behaved
  // host answering `bytes 0-28/29` was reported as having no Range support.
  // No real volume is under 1 MB so it would not have fired in production --
  // which is the point.  It would have sat here reading as a passing check
  // while testing the wrong thing, and been trusted by the next reader.
  const crm = cr.match(/^bytes 0-(\d+)\/(\d+)$/);
  const ranged = res.status === 206 && !!crm &&
    Number(crm[1]) === Math.min(1023, Number(crm[2]) - 1);
  record(`${label} Range supported`, ranged,
    ranged ? cr : `HTTP ${res.status}, Content-Range: ${cr || '(absent)'} -- a #page=300 link will pull the whole volume first`);

  // Size against the manifest's own record.  `mb` is rounded to one decimal
  // and MB is ambiguous between 10^6 and 2^20, so accept either convention.
  // This is a COARSE check: it catches a truncated or substituted object, not
  // a subtle one.  The byte-for-byte sample below is what catches subtle.
  let total = null;
  const m = cr.match(/\/(\d+)$/);
  if (m) total = Number(m[1]);
  else if (res.status === 200) total = buf.length;
  if (total != null && typeof it.mb === 'number') {
    const dec = total / 1e6, bin = total / 1048576;
    const ok = Math.abs(dec - it.mb) <= 0.06 || Math.abs(bin - it.mb) <= 0.06;
    record(`${label} size`, ok,
      ok ? `${total} B (${dec.toFixed(2)} MB) vs manifest ${it.mb} MB`
         : `${total} B = ${dec.toFixed(2)}/${bin.toFixed(2)} MB, manifest says ${it.mb} MB -- disagrees under either convention`);
  }
  return { url, total };
}

// --------------------------------------------------------------------------
// Byte-for-byte, new origin against the one the site uses today.  Sampled by
// default: 118 volumes is ~386 MB from EACH origin, and pulling all of it
// through the rate-limited development URL is the very load this repair
// exists to stop.  --full does all 118 when that is wanted.
// --------------------------------------------------------------------------
async function sha256(url) {
  const res = await fetch(url, { redirect: 'follow' });
  if (!res.ok) return { err: `HTTP ${res.status}` };
  const buf = Buffer.from(await res.arrayBuffer());
  return { hash: crypto.createHash('sha256').update(buf).digest('hex'), len: buf.length };
}

async function compareBytes(newOrigin, oldOrigin, items, full) {
  if (!oldOrigin) {
    record('byte comparison', false, 'cannot read the current origin from downloads.html');
    return;
  }
  if (oldOrigin === newOrigin) {
    record('byte comparison', true,
      'SKIPPED: downloads.html already names the origin under test, so there is nothing to compare against. Run this gate BEFORE the R2_BASE edit, or pass the old origin in OSBCT_PDF_OLD_ORIGIN.');
    return;
  }
  // Smallest of each layer, so the sample spans all three folders and costs
  // the least; plus the largest object overall, because a size ceiling is a
  // real failure mode and only the largest can meet it.
  let chosen;
  if (full) chosen = items;
  else {
    chosen = LAYERS.map((L) => items.filter((i) => i.layer === L).sort((a, b) => a.mb - b.mb)[0]).filter(Boolean);
    const biggest = items.slice().sort((a, b) => b.mb - a.mb)[0];
    if (biggest && !chosen.includes(biggest)) chosen.push(biggest);
  }
  for (const it of chosen) {
    const [a, b] = await Promise.all([
      sha256(`${newOrigin}/${it.key}`),
      sha256(`${oldOrigin}/${it.key}`),
    ]);
    if (a.err || b.err) {
      record(`bytes ${it.file}`, false, `new: ${a.err || 'ok'}, old: ${b.err || 'ok'}`);
      continue;
    }
    const ok = a.hash === b.hash;
    record(`bytes ${it.file}`, ok,
      ok ? `${a.len} B, sha256 ${a.hash.slice(0, 16)}… identical on both origins`
         : `new ${a.len} B ${a.hash.slice(0, 16)}… vs old ${b.len} B ${b.hash.slice(0, 16)}… -- DIFFERENT OBJECTS`);
  }
}

// --------------------------------------------------------------------------
// NEGATIVE CONTROLS.  Same reason as check_r2_origin.js: a gate that has
// never produced a FAIL is not evidence of anything.
// --------------------------------------------------------------------------
async function negativeControls(origin) {
  const bogus = 'pali-unicode/zzzz_no_such_volume_zzzz.pdf';
  try {
    const r = await fetch(`${origin}/${bogus}`);
    record('negative control: missing object 404s', !r.ok,
      r.ok ? `HTTP ${r.status} for an object that cannot exist -- every probe above is meaningless`
           : `HTTP ${r.status}, as it should`);
  } catch (e) {
    record('negative control: missing object 404s', true, `fetch refused (${e.message})`);
  }

  const good = Buffer.from('%PDF-1.7 body');
  const bad = Buffer.from('<html>Object not found</html>');
  record('negative control: magic-byte test discriminates',
    good.slice(0, 5).toString('latin1') === '%PDF-' && bad.slice(0, 5).toString('latin1') !== '%PDF-',
    'a non-PDF body is rejected');

  const h1 = crypto.createHash('sha256').update(good).digest('hex');
  const h2 = crypto.createHash('sha256').update(Buffer.concat([good, Buffer.from('!')])).digest('hex');
  record('negative control: hash comparator discriminates', h1 !== h2, 'one appended byte changes the digest');
}

// --------------------------------------------------------------------------
// SELF-TEST.  Serves synthetic objects and requires this file to catch each
// defect it advertises.  No network beyond 127.0.0.1.
// --------------------------------------------------------------------------
async function selftest() {
  const http = require('http');
  const BODY = Buffer.concat([Buffer.from('%PDF-1.7\n'), Buffer.alloc(2000, 0x41), Buffer.from('\n%%EOF\n')]);
  const cases = {
    '/good.pdf':        { ct: 'application/pdf', body: BODY },
    '/wrongtype.pdf':   { ct: 'application/octet-stream', body: BODY },
    '/attach.pdf':      { ct: 'application/pdf', body: BODY, cd: 'attachment; filename="x.pdf"' },
    '/nothtml.pdf':     { ct: 'application/pdf', body: Buffer.from('<html>Object not found</html>') },
    '/norange.pdf':     { ct: 'application/pdf', body: BODY, norange: true },
    // A well-formed PDF of the wrong LENGTH.  Added because the header comment
    // claimed the size check "catches a truncated object" and nothing here
    // demonstrated it -- a claim in a comment with no instrument behind it,
    // which is the thing this project keeps finding in its own gates.  Probed
    // with mb: 2.5 below, against a 2 KB body.
    '/truncated.pdf':   { ct: 'application/pdf', body: BODY },
  };
  const srv = http.createServer((req, res) => {
    const c = cases[req.url.split('?')[0]];
    if (!c) { res.writeHead(200, { 'Content-Type': 'text/plain' }); res.end('found anyway'); return; }
    const h = { 'Content-Type': c.ct };
    if (c.cd) h['Content-Disposition'] = c.cd;
    const range = req.headers.range;
    if (range && !c.norange) {
      const end = Math.min(1023, c.body.length - 1);
      h['Content-Range'] = `bytes 0-${end}/${c.body.length}`;
      res.writeHead(206, h); res.end(c.body.slice(0, end + 1));
    } else { res.writeHead(200, h); res.end(c.body); }
  });
  await new Promise((r) => srv.listen(0, '127.0.0.1', r));
  const origin = `http://127.0.0.1:${srv.address().port}`;
  console.log(`selftest origin: ${origin}\n`);

  // Each row: the object, the check that MUST fail on it, and the manifest
  // `mb` to probe it with.  Every row but the first must also leave the OTHER
  // checks passing -- a gate that fails everything on every defect tells you
  // nothing about which defect it found.
  const expect = [
    ['good.pdf',      'good',                    BODY.length / 1e6],
    ['wrongtype.pdf', 'Content-Type',            BODY.length / 1e6],
    ['attach.pdf',    'not forced to download',  BODY.length / 1e6],
    ['nothtml.pdf',   'body is a PDF',           29 / 1e6],
    ['norange.pdf',   'Range supported',         BODY.length / 1e6],
    ['truncated.pdf', 'size',                    2.5],
  ];
  let bad = 0;
  for (const [name, want, mb] of expect) {
    results.length = 0;
    console.log(`-- ${name} (expect ${want === 'good' ? 'all pass' : `a FAIL on "${want}", and nothing else`})`);
    await probeObject(origin, { key: name, file: name, mb });
    const fails = results.filter((r) => !r.ok);
    if (want === 'good') {
      if (fails.length) { console.log(`   SELFTEST BROKEN: clean object produced ${fails.length} failure(s)`); bad++; }
      else console.log('   selftest ok: clean object passes');
    } else {
      const caught = fails.some((f) => f.name.includes(want));
      const stray = fails.filter((f) => !f.name.includes(want)).map((f) => f.name);
      if (!caught) { console.log(`   SELFTEST BROKEN: "${want}" defect was NOT caught`); bad++; }
      else if (stray.length) { console.log(`   SELFTEST BROKEN: caught "${want}" but ALSO failed ${stray.join(', ')} -- the gate cannot say which defect it found`); bad++; }
      else console.log(`   selftest ok: "${want}" defect caught, and only that one`);
    }
    console.log('');
  }
  results.length = 0;
  console.log('-- negative controls against a host that 200s on everything');
  await negativeControls(origin);
  if (results.some((r) => r.name.includes('missing object') && r.ok)) {
    console.log('   SELFTEST BROKEN: a permissive host was not detected'); bad++;
  } else console.log('   selftest ok: permissive host detected');

  srv.close();
  console.log('');
  if (bad) { console.log(`SELFTEST FAILED: ${bad} defect(s) this gate claims to catch, it does not.`); process.exit(1); }
  console.log('SELFTEST GREEN. This gate passes clean objects and fails each defect it advertises.');
}

(async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--selftest')) return selftest();

  const originArg = args.find((a) => !a.startsWith('--'));
  if (!originArg) {
    console.error('usage: node pipeline/check_pdf_origin.js https://files.buddha-dhamma.net [--full]');
    console.error('       node pipeline/check_pdf_origin.js --selftest');
    process.exit(2);
  }
  const ORIGIN = originArg.replace(/\/+$/, '');
  const full = args.includes('--full');

  const items = loadManifest();
  const siteOrigin = checkConstantsAgree();
  const oldOrigin = (process.env.OSBCT_PDF_OLD_ORIGIN || siteOrigin || '').replace(/\/+$/, '');

  console.log(`origin under test : ${ORIGIN}`);
  console.log(`origin in site/   : ${siteOrigin || '(unreadable)'}`);
  console.log(`compared against  : ${oldOrigin || '(none)'}`);
  console.log(`manifest          : site/downloads.data.json -- ${items.length} objects`);
  console.log(`byte comparison   : ${full ? 'ALL 118 (~386 MB per origin)' : 'sampled (4 objects)'}`);
  console.log('');

  checkFoldersAgree(items);
  checkKeysUrlSafe(items);
  console.log('');

  for (const it of items) await probeObject(ORIGIN, it);
  console.log('');

  await compareBytes(ORIGIN, oldOrigin, items, full);
  console.log('');
  await negativeControls(ORIGIN);

  const failed = results.filter((r) => !r.ok);
  console.log('');
  console.log(`${results.length - failed.length} passed, ${failed.length} failed`);
  if (failed.length) {
    console.log('');
    console.log('DO NOT change R2_BASE, and DO NOT disable the Public Development URL.');
    console.log('The r2.dev origin is still serving the site and nothing has been risked.');
    process.exit(1);
  }
  console.log('');
  console.log('Green. R2_BASE may be switched to this origin.');
  console.log('Disable the Public Development URL only AFTER that change is deployed');
  console.log('and the live site has been seen to serve a PDF from the new domain.');
})();
